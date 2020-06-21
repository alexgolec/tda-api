.. py:module:: tda.orders.templates

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

  (equity_buy_limit('GOOG', 1, 1250.0)
   .set_duration(Duration.GOOD_TILL_CANCEL)
   .set_session(Session.SEAMLESS))

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

Due to their complexity, options order templates are pending. Templates for 
options orders will be added in subsequent releases. 

In the meantime, you can construct all supported options orders using the 
:ref:`OrderBuilder <order_builder>`, although you will have to construct them 
yourself.

---------------
Utility Methods
---------------

These methods return orders that represent complex multi-order strategies. Note 
expect all their parameters to be of type ``OrderBuilder``. You can construct 
these orders using the templates above or by 
:ref:`creating them from scratch <order_builder>`.

.. autofunction:: tda.orders.common.one_cancels_other
.. autofunction:: tda.orders.common.first_triggers_second


----------------------------------------
What happened to ``EquityOrderBuilder``?
----------------------------------------

Long-time users may notice that this documentation no longer mentions the 
``EquityOrderBuilder`` class. This class used to be used to create equities 
orders, and offered a subset of the functionality offered by the 
:ref:`OrderBuilder <order_builder>`. This class has been deprecated in favor of 
the order builder and the above templates, and will be removed from a future 
release. 

In the meantime, you can continue using this order builder, although you really 
should migrate to the new one soon. You can find documentation for this class in 
the `older versions 
<https://tda-api.readthedocs.io/en/v0.3.2/orders.html>`__ of ``tda-api``'s 
documentation. 
