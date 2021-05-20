.. py:module:: tda.orders.generic

.. _order_builder:

==========================
``OrderBuilder`` Reference
==========================

The :meth:`Client.place_order() <tda.client.Client.place_order>` method expects 
a rather complex JSON object that describes the desired order. TDA provides some 
`example order specs 
<https://developer.tdameritrade.com/content/place-order-samples>`__ to
illustrate the process and provides a schema in the `place order documentation 
<https://developer.tdameritrade.com/account-access/apis/post/accounts/
%7BaccountId%7D/orders-0>`__, but beyond that we're on our own. ``tda-api`` aims 
to be useful to everyone, from users who want to easily place common equities 
and options trades, to advanced users who want to place complex multi-leg, 
multi-asset type trades. 

For users interested in simple trades, ``tda-api`` supports pre-built 
:ref:`order_templates` that allow fast construction of many common trades. 
Advanced users can modify these trades however they like, and can even build 
trades from scratch.

This page describes the features of the complete order schema in all their 
complexity. It is aimed at advanced users who want to create complex orders. 
Less advanced users can use the :ref:`order templates <order_templates>` to 
create orders. If they find themselves wanting to go beyond those templates, 
they can return to this page to learn how.


------------------------------------------
Optional: Order Specification Introduction
------------------------------------------

Before we dive in to creating order specs, let's briefly introduce their 
structure. This section is optional, although users wanting to use more advanced 
featured like stop prices and complex options orders will likely want to read it.

Here is an example of a spec that places a limit order to buy 13 shares of
``MSFT`` for no more than $190. This is exactly the order that would be returned 
by :func:`tda.orders.equities.equity_buy_limit`:

.. code-block:: JSON

  {
      "session": "NORMAL",
      "duration": "DAY",
      "orderType": "LIMIT",
      "price": "190.90",
      "orderLegCollection": [
          {
              "instruction": "BUY",
              "instrument": {
                  "assetType": "EQUITY",
                  "symbol": "MSFT"
              },
              "quantity": 1
          }
      ],
      "orderStrategyType": "SINGLE"
  }

Some key points are:

 * The ``LIMIT`` order type notifies TD that you'd like to place a limit order.
 * The order strategy type is ``SINGLE``, meaning this order is not a composite 
   order.
 * The order leg collection contains a single leg to purchase the equity.
 * The price is specified *outside* the order leg. This may seem 
   counterintuitive, but it's important when placing composite options orders.

If this seems like a lot of detail to specify a rather simple order, it is. The 
thing about the order spec object is that it can express *every* order that can 
be made through the TD Ameritrade API. For an advanced example, here is a order 
spec for a standing order to enter a long position in ``GOOG`` at $1310 or less 
that triggers a one-cancels-other order that exits the position if the price 
rises to $1400 or falls below $1250:

.. code-block:: JSON

  {
      "session": "NORMAL",
      "duration": "GOOD_TILL_CANCEL",
      "orderType": "LIMIT",
      "price": "1310.00",
      "orderLegCollection": [
          {
              "instruction": "BUY",
              "instrument": {
                  "assetType": "EQUITY",
                  "symbol": "GOOG"
              },
              "quantity": 1
          }
      ],
      "orderStrategyType": "TRIGGER",
      "childOrderStrategies": [
          {
              "orderStrategyType": "OCO",
              "childOrderStrategies": [
                  {
                      "session": "NORMAL",
                      "duration": "GOOD_TILL_CANCEL",
                      "orderType": "LIMIT",
                      "price": "1400.00",
                      "orderLegCollection": [
                          {
                              "instruction": "SELL",
                              "instrument": {
                                  "assetType": "EQUITY",
                                  "symbol": "GOOG"
                              },
                              "quantity": 1
                          }
                      ]
                  },
                  {
                      "session": "NORMAL",
                      "duration": "GOOD_TILL_CANCEL",
                      "orderType": "STOP_LIMIT",
                      "stopPrice": "1250.00",
                      "orderLegCollection": [
                          {
                              "instruction": "SELL",
                              "instrument": {
                                  "assetType": "EQUITY",
                                  "symbol": "GOOG"
                              },
                              "quantity": 1
                          }
                      ]
                  }
              ]
          }
      ]
  }

While this looks complex, it can be broken down into the same components as the 
simpler buy order:

 * This time, the ``LIMIT`` order type applies to the top-level order.
 * The order strategy type is ``TRIGGER``, which tells TD Ameritrade to hold off 
   placing the the second order until the first one completes.
 * The order leg collection still contains a single leg, and the price is still 
   defined outside the order leg. This is typical for equities orders.

There are also a few things that aren't there in the simple buy order:

 * The ``childOrderStrategies`` contains the ``OCO`` order that is triggered 
   when the first ``LIMIT`` order is executed. 
 * If you look carefully, you'll notice that the inner ``OCO`` is a 
   fully-featured suborder in itself. 

This order is large and complex, and it takes a lot of reading to understand 
what's going on here. Fortunately for you, you don't have to; ``tda-api`` cuts 
down on this complexity by providing templates and helpers to make building 
orders easy:

.. code-block:: python

  from tda.orders.common import OrderType
  from tda.orders.generic import OrderBuilder

  one_triggers_other(
      equity_buy_limit('GOOG', 1, 1310),
      one_cancels_other(
          equity_sell_limit('GOOG', 1, 1400),
          equity_sell_limit('GOOG', 1, 1240)
              .set_order_type(OrderType.STOP_LIMIT)
              .clear_price()
              .set_stop_price(1250)
      )

You can find the full listing of order templates and utility functions 
:ref:`here <order_templates>`.

Now that you have some background on how orders are structured, let's dive into 
the order builder itself. 


------------------------------------------------------------
Constructing ``OrderBuilder`` Objects from Historical Orders
------------------------------------------------------------

TDAmeritrade supports a huge array of order specifications, including both 
equity and option orders, stop, conditionals, etc. However, the exact format of 
these orders is tricky: if you don't specify the order *exactly* how TDA expects 
it, you'll either have your order rejected for no reason, or you'll end up 
placing a different order than you intended. 

Meanwhile, thinkorswim and the TDAmeritrade web and app UIs let you easily place 
these orders, just not in a programmatic way. ``tda-api`` helps bridge this gap 
by allowing you to place a complex order through your preferred UI and then 
producing code that would have generated this order using ``tda-api``. This 
process looks like this: 

1. Place an order using your favorite UI.
2. Call the following script to generate code for the most recently-placed 
   order:

.. code-block:: shell

  # Notice we don't prefix this with "python" because this is a script that was 
  # installed by pip when you installed tda-api
  tda-orders-codegen.py --token_file <your token file path> --api_key <your API key>

3. Copy-paste the resulting code and adapt it to your needs.

This script is installed by ``pip``, and will only be accessible if you've added
pip's executable locations to your ``$PATH``. If you're having a hard time, feel
free to ask for help on our `Discord server 
<https://discord.gg/nfrd9gh>`__.


--------------------------
``OrderBuilder`` Reference
--------------------------

This section provides a detailed reference of the generic order builder. You can 
use it to help build your own custom orders, or you can modify the pre-built 
orders generated by ``tda-api``'s order templates.

Unfortunately, this reference is largely reverse-engineered. It was initially 
generated from the schema provided in the `official API documents
<https://developer.tdameritrade.com/account-access/apis/post/accounts/
%7BaccountId%7D/orders-0>`__, but many of the finer points, such as which fields 
should be populated for which order types, etc. are best guesses. If you find 
something is inaccurate or missing, please `let us know 
<https://github.com/alexgolec/tda-api/issues>`__.

That being said, experienced traders who understand how various order types and 
complex strategies work should find this builder easy to use, at least for the 
order types with which they are familiar. Here are some resources you can use to 
learn more, courtesy of the Securites and Exchange Commission:

 * `Trading Basics: Understanding the Different Ways to Buy and Sell Stock 
   <https://www.sec.gov/investor/alerts/trading101basics.pdf>`__
 * `Trade Execution: What Every Investor Should Know <https://www.sec.gov/
   reportspubs/investor-publications/investorpubstradexechtm.html>`__
 * `Investor Bulletin: An Introduction to Options <https://www.sec.gov/oiea/
   investor-alerts-bulletins/ib_introductionoptions.html>`__

You can also find TD Ameritrade's official documentation on orders `here
<https://www.tdameritrade.com/retail-en_us/resources/pdf/SDPS819.pdf>`__, 
although it doesn't actually cover all functionality that ``tda-api`` supports.


+++++++++++
Order Types
+++++++++++

Here are the order types that can be used:

.. autoclass:: tda.orders.common::OrderType
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_order_type
.. automethod:: tda.orders.generic.OrderBuilder.clear_order_type


++++++++++++++++++++
Session and Duration
++++++++++++++++++++

Together, these fields control when the order will be placed and how long it 
will remain active. Note ``tda-api``'s :ref:`templates <order_templates>` place 
orders that are active for the duration of the current normal trading session. 
If you want to modify the default session and duration, you can use these 
methods to do so.

.. autoclass:: tda.orders.common::Session
  :members:
  :undoc-members:
.. autoclass:: tda.orders.common::Duration
  :members:
  :undoc-members:

.. automethod:: tda.orders.generic.OrderBuilder.set_duration
.. automethod:: tda.orders.generic.OrderBuilder.clear_duration
.. automethod:: tda.orders.generic.OrderBuilder.set_session
.. automethod:: tda.orders.generic.OrderBuilder.clear_session


+++++
Price
+++++

Price is the amount you'd like to pay for each unit of the position you're 
taking:

 * For equities and simple options limit orders, this is the price which you'd 
   like to pay/receive. 
 * For complex options limit orders (net debit/net credit), this is the total
   credit or debit you'd like to receive.

In other words, the price is the sum of the prices of the :ref:`order_legs`. 
This is particularly powerful for complex multi-leg options orders, which 
support complex top and/or limit orders that trigger when the price of a 
position reaches certain levels. In those cases, the price of an order can drop 
below the specified price as a result of movements in multiple legs of the 
trade. 

.. _number_truncation:

~~~~~~~~~~~~~~~~~~
Note on Truncation
~~~~~~~~~~~~~~~~~~

**Important Note:** Under the hood, the TDAmeritrade API expects price as a 
string, whereas ``tda-api`` allows setting prices as a floating point number for
convenience. The passed value is then converted to a string under the hood, 
which involves some truncation logic:

 * If the price has absolute value less than one, truncate  (not round!) to 
   four decimal places. For example, `0.186992` will become `0.1869`.
 * For all other values, truncate to two decimal places. The above example would 
   become `0.18`. 

This behavior is meant as a sane heuristic, and there are almost certainly 
situations where it is not the correct thing to do. You can sidestep this entire 
process by passing your price as a string, although be forewarned that 
TDAmeritrade may reject your order or even interpret it in unexpected ways. 

.. automethod:: tda.orders.generic.OrderBuilder.set_price
.. automethod:: tda.orders.generic.OrderBuilder.copy_price
.. automethod:: tda.orders.generic.OrderBuilder.clear_price


.. _order_legs:

++++++++++
Order Legs
++++++++++

Order legs are where the actual assets being bought or sold are specified. For 
simple equity or single-options orders, there is just one leg. However, for 
complex multi-leg options trades, there can be more than one leg.

Note that order legs often do not execute all at once. Order legs can be 
executed over the specified :class:`~tda.orders.common.Duration` of the order. 
What's more, if order legs request a large number of shares, legs themselves can 
be partially filled. You can control this setting using the 
:class:`~tda.orders.common.SpecialInstruction` value ``ALL_OR_NONE``. 

With all that out of the way, order legs are relatively simple to specify. 
``tda-api`` currently supports equity and option order legs:

.. automethod:: tda.orders.generic.OrderBuilder.add_equity_leg
.. autoclass:: tda.orders.common::EquityInstruction
  :members:
  :undoc-members:

.. automethod:: tda.orders.generic.OrderBuilder.add_option_leg
.. autoclass:: tda.orders.common::OptionInstruction
  :members:
  :undoc-members:

.. automethod:: tda.orders.generic.OrderBuilder.clear_order_legs



+++++++++++++++++++++
Requested Destination
+++++++++++++++++++++

By default, TD Ameritrade sends trades to whichever exchange provides the best 
price. This field allows you to request a destination exchange for your trade, 
although whether your order is actually executed there is up to TDA.

.. autoclass:: tda.orders.common::Destination
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_requested_destination
.. automethod:: tda.orders.generic.OrderBuilder.clear_requested_destination


++++++++++++++++++++
Special Instructions
++++++++++++++++++++

Trades can contain special instructions which handle some edge cases:

.. autoclass:: tda.orders.common::SpecialInstruction
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_special_instruction
.. automethod:: tda.orders.generic.OrderBuilder.clear_special_instruction


++++++++++++++++++++++++++
Complex Options Strategies
++++++++++++++++++++++++++

TD Ameritrade supports a number of complex options strategies. These strategies 
are complex affairs, with each leg of the trade specified in the order legs. TD 
performs additional validation on these strategies, so they are somewhat 
complicated to place. However, the benefit is more flexibility, as trades like 
trailing stop orders based on net debit/credit can be specified.

Unfortunately, due to the complexity of these orders and the lack of any real 
documentation, we cannot offer definitively say how to structure these orders. A 
few things have been observed, however:

 * The legs of the order can be placed by adding them as option order legs using
   :meth:`~tda.orders.generic.OrderBuilder.add_option_leg`.
 * For spreads resulting in a new debit/credit, the price represents the overall 
   debit or credit desired.

If you successfully use these strategies, we want to know about it. Please let 
us know by joining our `Discord server <https://discord.gg/nfrd9gh>`__ to chat 
about it, or by `creating a feature request <https://github.com/alexgolec/
tda-api/issues>`__.

.. autoclass:: tda.orders.common::ComplexOrderStrategyType
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_complex_order_strategy_type
.. automethod:: tda.orders.generic.OrderBuilder.clear_complex_order_strategy_type


++++++++++++++++
Composite Orders
++++++++++++++++

``tda-api`` supports composite order strategies, in which execution of one order 
has an effect on another:

 * ``OCO``, or "one cancels other" orders, consist of a pair of orders where 
   execution of one immediately cancels the other.
 * ``TRIGGER`` orders consist of a pair of orders where execution of one 
   immediately results in placement of the other.

``tda-api`` provides helpers to specify these easily: 
:func:`~tda.orders.common.one_cancels_other` and
:func:`~tda.orders.common.first_triggers_second`. This is almost certainly 
easier than specifying these orders manually. However, if you still want to 
create them yourself, you can specify these composite order strategies like so:

.. autoclass:: tda.orders.common::OrderStrategyType
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_order_strategy_type
.. automethod:: tda.orders.generic.OrderBuilder.clear_order_strategy_type


+++++++++++++++++++
Undocumented Fields
+++++++++++++++++++

Unfortunately, your humble author is not an expert in all things trading. The 
order spec schema describes some things that are outside my ability to document, 
so rather than make stuff up, I'm putting them here in the hopes that someone 
will come along and shed some light on them. You can make suggestions by filing 
an issue on our 
`GitHub issues page <https://github.com/alexgolec/tda-api/issues>`__, 
or by joining our `Discord server <https://discord.gg/M3vjtHj>`__.


.. _undocumented_quantity:

~~~~~~~~
Quantity
~~~~~~~~

This one seems obvious: doesn't the quantity mean the number of stock I want to 
buy? The trouble is that the order legs also have a ``quantity`` field, which 
suggests this field means something else. The leading hypothesis is that is 
outlines the number of copies of the order to place, although we have yet to 
verify that.

.. automethod:: tda.orders.generic.OrderBuilder.set_quantity
.. automethod:: tda.orders.generic.OrderBuilder.clear_quantity


~~~~~~~~~~~~~~~~~~~~~~~~
Stop Order Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

Stop orders and their variants (stop limit, trailing stop, trailing stop limit) 
support some rather complex configuration. Both stops prices and the limit 
prices of the resulting order can be configured to follow the market in a 
dynamic fashion. The market dimensions that they follow can also be configured 
differently, and it appears that which dimensions are supported varies by order 
type. 

We have unfortunately not yet done a thorough analysis of what's supported, nor 
have we made the effort to make it simple and easy. While we're *pretty* sure we 
understand how these fields work, they've been temporarily placed into the 
"undocumented" section, pending a followup. Users are invited to experiment with 
these fields at their own risk. 


.. automethod:: tda.orders.generic.OrderBuilder.set_stop_price
.. automethod:: tda.orders.generic.OrderBuilder.copy_stop_price
.. automethod:: tda.orders.generic.OrderBuilder.clear_stop_price

.. autoclass:: tda.orders.common::StopPriceLinkBasis
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_stop_price_link_basis
.. automethod:: tda.orders.generic.OrderBuilder.clear_stop_price_link_basis

.. autoclass:: tda.orders.common::StopPriceLinkType
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_stop_price_link_type
.. automethod:: tda.orders.generic.OrderBuilder.clear_stop_price_link_type

.. automethod:: tda.orders.generic.OrderBuilder.set_stop_price_offset
.. automethod:: tda.orders.generic.OrderBuilder.clear_stop_price_offset

.. autoclass:: tda.orders.common::StopType
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_stop_type
.. automethod:: tda.orders.generic.OrderBuilder.clear_stop_type

.. autoclass:: tda.orders.common::PriceLinkBasis
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_price_link_basis
.. automethod:: tda.orders.generic.OrderBuilder.clear_price_link_basis

.. autoclass:: tda.orders.common::PriceLinkType
  :members:
  :undoc-members:
.. automethod:: tda.orders.generic.OrderBuilder.set_price_link_type
.. automethod:: tda.orders.generic.OrderBuilder.clear_price_link_type

.. automethod:: tda.orders.generic.OrderBuilder.set_activation_price
.. automethod:: tda.orders.generic.OrderBuilder.clear_activation_price
