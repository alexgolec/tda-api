.. py:module:: tda.orders.templates

.. _order_templates:

===============
Order Templates
===============

``tda-api`` strives to be easy to use. This means making it easy to do simple 
things while making it possible to do complicated things. Order construction is 
a major challenge to this mission: both simple and complicated orders use the 
same format, meaning simple orders require a surprising amount of sophistication 
to place. 

We get around this by providing a fully-featured order builder to help build 
arbitrarily complex orders, along with a number of templates that pre-configure 
an order builder for common orders. This page describes the simple templates, 
while the :ref:`order_builder` page documents the order builder in all its 
complexity. 


---------------------
Using These Templates
---------------------

These templates serve two purposes. First, they are designed to choose defaults 
so you can immediately :ref:`place them <placing_new_orders>`. These defaults 
are:

 * Placed during the normal trading sessions.
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
