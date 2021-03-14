.. py:module:: tda.orders

.. _order_templates:

===============
Order Templates
===============

``tda-api`` strives to be easy to use. This means making it easy to do simple 
things, while making it possible to do complicated things. Order construction is
a major challenge to this mission: both simple and complicated orders use the 
same format, meaning simple orders require a surprising amount of sophistication 
to place. 

We get around this by providing templates that make it easy to place common 
orders, while allowing advanced users to modify the orders returned from the 
templates to create more complex ones. Very advanced users can even create their 
own orders from scratch. This page describes the simple templates, while the 
:ref:`order_builder` page documents the order builder in all its complexity. 


---------------------
Using These Templates
---------------------

These templates serve two purposes. First, they are designed to choose defaults 
so you can immediately :ref:`place them <placing_new_orders>`. These defaults 
are:

 * All orders execute during the current normal trading session. If placed 
   outside of trading hours, the execute during the next normal trading session.
 * Time-in-force is set to ``DAY``.
 * All other fields (such as requested destination, etc.) are left unset, 
   meaning they receive default treatment from TD Ameritrade. Note this 
   treatment depends on TDA's implementation, and may change without warning.

Secondly, they serve as starting points for building more complex order types. 
All templates return a pre-populated ``OrderBuilder`` object, meaning complex 
functionality can be specified by modifying the returned object. For example, 
here is how you would place an order to buy ``GOOG`` for no more than $1250 at 
any time in the next six months:

.. code-block:: python

  from tda.orders.equities import equity_buy_limit
  from tda.orders.common import Duration, Session

  client = ... # See "Authentication and Client Creation"

  client.place_order(
      1000,  # account_id
      equity_buy_limit('GOOG', 1, 1250.0)
          .set_duration(Duration.GOOD_TILL_CANCEL)
          .set_session(Session.SEAMLESS)
          .build())

You can find a full reference for all supported fields in :ref:`order_builder`.


----------------
Equity Templates
----------------

++++++++++
Buy orders
++++++++++

.. autofunction:: tda.orders.equities.equity_buy_market
.. autofunction:: tda.orders.equities.equity_buy_limit

+++++++++++
Sell orders
+++++++++++

.. autofunction:: tda.orders.equities.equity_sell_market
.. autofunction:: tda.orders.equities.equity_sell_limit

+++++++++++++++++
Sell short orders
+++++++++++++++++

.. autofunction:: tda.orders.equities.equity_sell_short_market
.. autofunction:: tda.orders.equities.equity_sell_short_limit

+++++++++++++++++++
Buy to cover orders
+++++++++++++++++++

.. autofunction:: tda.orders.equities.equity_buy_to_cover_market
.. autofunction:: tda.orders.equities.equity_buy_to_cover_limit


-----------------
Options Templates
-----------------

TD Ameritrade supports over a dozen options strategies, each of which involve a 
precise structure in the order builder. ``tda-api`` is slowly gaining support 
for these strategies, and they are documented here as they become ready for use. 
As time goes on, more templates will be added here. 

In the meantime, you can construct all supported options orders using the 
:ref:`OrderBuilder <order_builder>`, although you will have to construct them 
yourself.

Note orders placed using these templates may be rejected, depending on the 
user's options trading authorization.


++++++++++++++++++++++++
Building Options Symbols
++++++++++++++++++++++++

All templates require option symbols, which are somewhat more involved than 
equity symbols. They encode the underlying, the expiration date, option type 
(put or call) and the strike price. They are especially tricky to extract 
because both the TD Ameritrade UI and the thinkorswim UI don't reveal the symbol 
in the option chain view. 

Real trading symbols can be found by requesting the :ref:`option_chain`. They 
can also be built using the ``OptionSymbol`` helper, which provides utilities 
for creating options symbols. Note it only emits syntactically correct symbols 
and does not validate whether the symbol actually represents a traded option:

.. code-block:: python

  from tda.order.options import OptionSymbol

  symbol = OptionSymbol(
      'TSLA', datetime.date(year=2020, month=11, day=20), 'P', '1360').build()

.. autoclass:: tda.orders.options.OptionSymbol
  :special-members:


++++++++++++++
Single Options
++++++++++++++

Buy and sell single options.

.. autofunction:: tda.orders.options.option_buy_to_open_market
.. autofunction:: tda.orders.options.option_buy_to_open_limit
.. autofunction:: tda.orders.options.option_sell_to_open_market
.. autofunction:: tda.orders.options.option_sell_to_open_limit
.. autofunction:: tda.orders.options.option_buy_to_close_market
.. autofunction:: tda.orders.options.option_buy_to_close_limit
.. autofunction:: tda.orders.options.option_sell_to_close_market
.. autofunction:: tda.orders.options.option_sell_to_close_limit


.. _vertical_spreads:

++++++++++++++++
Vertical Spreads
++++++++++++++++

Vertical spreads are a complex option strategy that provides both limited upside
and limited downside. They are constructed using by buying an option at one 
strike while simultaneously selling another option with the same underlying and 
expiration date, except with a different strike, and they can be constructed 
using either puts or call. You can find more information about this strategy on 
`Investopedia <https://www.investopedia.com/articles/active-trading/032614/
which-vertical-option-spread-should-you-use.asp>`__

``tda-api`` provides utilities for opening and closing vertical spreads in 
various ways. It follows the standard ``(bull/bear) (put/call)`` naming 
convention, where the name specifies the market attitude and the option type 
used in construction. 

For consistency's sake, the option with the smaller strike price is always 
passed first, followed by the higher strike option. You can find the option 
symbols by consulting the return value of the :ref:`option_chain` client call.


~~~~~~~~~~~~~~
Call Verticals
~~~~~~~~~~~~~~

.. autofunction:: tda.orders.options.bull_call_vertical_open
.. autofunction:: tda.orders.options.bull_call_vertical_close
.. autofunction:: tda.orders.options.bear_call_vertical_open
.. autofunction:: tda.orders.options.bear_call_vertical_close


~~~~~~~~~~~~~
Put Verticals
~~~~~~~~~~~~~

.. autofunction:: tda.orders.options.bull_put_vertical_open
.. autofunction:: tda.orders.options.bull_put_vertical_close
.. autofunction:: tda.orders.options.bear_put_vertical_open
.. autofunction:: tda.orders.options.bear_put_vertical_close


---------------
Utility Methods
---------------

These methods return orders that represent complex multi-order strategies, 
namely "one cancels other" and "first triggers second" strategies. Note they 
expect all their parameters to be of type ``OrderBuilder``. You can construct 
these orders using the templates above or by 
:ref:`creating them from scratch <order_builder>`.

Note that you do **not** construct composite orders by placing the constituent 
orders and then passing the results to the utility methods: 

.. code-block:: python

  order_one = c.place_order(config.account_id, 
                    option_buy_to_open_limit(trade_symbol, contracts, safety_ask)
                    .set_duration(Duration.GOOD_TILL_CANCEL)
                    .set_session(Session.NORMAL)
                    .build())

  order_two = c.place_order(config.account_id, 
                    option_sell_to_close_limit(trade_symbol, half, double)
                    .set_duration(Duration.GOOD_TILL_CANCEL)
                    .set_session(Session.NORMAL)
                    .build())

  # THIS IS BAD, DO NOT DO THIS
  exec_trade =  c.place_order(config.account_id, first_triggers_second(order_one, order_two))

What's happening here is both constituent orders are being executed, and then 
``place_order`` will fail. Creating an ``OrderBuilder`` defers their execution, 
subject to your composite order rules. 

**Note:** It appears that using these methods requires disabling Advanced 
Features on your account. It is not entirely clear why this is the case, but 
we've seen numerous reports of issues with OCO and trigger orders being resolved 
by this method. You can disable advanced features by calling TDAmeritrade 
support and requesting that they be turned off. If you need more help, we 
recommend `joining our discord <https://discord.gg/M3vjtHj>`__ to ask the 
community for help. 

.. autofunction:: tda.orders.common.one_cancels_other
.. autofunction:: tda.orders.common.first_triggers_second


----------------------------------------
What happened to ``EquityOrderBuilder``?
----------------------------------------

Long-time users and new users following outdated tutorials may notice that
this documentation no longer mentions the ``EquityOrderBuilder`` class. This
class used to be used to create equities orders, and offered a subset of the
functionality offered by the :ref:`OrderBuilder <order_builder>`. This class
has been removed in favor of the order builder and the above templates. 
