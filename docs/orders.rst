.. _orders:
.. py:module:: tda.orders.generic

===============
Building Orders
===============

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

For users interested in simple trades, ``tda-api`` supports pre-built trade 
templates that allow fast construction of the most common trades. Advanced users 
can modify these trades however they like, and can even build trades from 
scratch.

This section begins by listing the supported common trades, and then describing 
the fully-featured order construction system that supports them. Advanced users 
can skip straight to that section.


------------------------------------------
Optional: Order Specification Introduction
------------------------------------------

Before we dive in to creating order specs, let's briefly introduce their 
structure. This section is optional, and if you just want to place common 
orders, you can skip ahead to the templates below. However, ``tda-api`` supports 
a lot more than just what those templates provide, so if you want to do 
something that's not supported out-of-the-box, this section will give you some 
background to help you achieve it.

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
spec for a standing order to enter a long position in ``GOOG`` that triggers a 
one-cancels-other order that exits the position if the price rises to $1400 or 
falls below $1250:

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
 * The order strategy type is ``TRIGGER``, which tell TD Ameritrade to wait on 
   the second order until the first one completes.
 * The order leg collection still contains a single leg, and the price is still 
   defined outside the order leg. This is typical for equities orders.

There are also a few things that weren' there in the simple buy order:

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

Now that you have some background on how orders are structured, let's dive into 
the order builder itself. 


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
complex strategies work will find this builder easy to use, at least for the 
order types with which they are familiar. Here are some resources you can use to 
learn more, courtesy of the Securites and Exchange Commission:

 * `Trading Basics: Understanding the Different Ways to Buy and Sell Stock 
   <https://www.sec.gov/investor/alerts/trading101basics.pdf>`__
 * `Trade Execution: What Every Investor Should Know <https://www.sec.gov/
   reportspubs/investor-publications/investorpubstradexechtm.html>`__
 * `Investor Bulletin: An Introduction to Options <https://www.sec.gov/oiea/
   investor-alerts-bulletins/ib_introductionoptions.html>`__

You can also find TD Ameritrade's official documentation on orders `here
<https://www.tdameritrade.com/retail-en_us/resources/pdf/SDPS819.pdf>`__.

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
will remain active. Note ``tda-api``'s templates place orders that are active 
for the duration of the current normal trading session. If you want to modify 
the default session and duration, you can use these methods to do so.

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


