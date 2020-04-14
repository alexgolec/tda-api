.. _orders:

=============================
Creating Order Specifications
=============================

The :meth:`Client.place_order() <tda.client.Client.place_order>` method expects 
a rather complex JSON object that describes the desired order. TDA provides some 
`example order specs 
<https://developer.tdameritrade.com/content/place-order-samples>`__ to
illustrate the process and provides a schema in the `place order documentation 
<https://developer.tdameritrade.com/account-access/apis/post/accounts/
%7BaccountId%7D/orders-0>`__, but beyond that we're on our own.

The ``tda.orders`` module provides an incomplete set of helpers for building 
these order specs. The aim is to make it impossible to build an invalid JSON 
object. For example, here is how you might use this module to place a market 
order for ten shares of Apple common stock:

.. code-block:: python

  from tda.orders import EquityOrderBuilder, Duration, Session

  builder = EquityOrderBuilder('AAPL', 10)
  builder.set_instruction(EquityOrderBuilder.Instruction.SELL)
  builder.set_order_type(EquityOrderBuilder.OrderType.MARKET)
  builder.set_duration(Duration.DAY)
  builder.set_session(Session.NORMAL)

  client = ...  # Get a client however you see fit
  account_id = 12345678

  resp = client.place_order(account_id, builder.build())
  assert resp.ok

-------------
Common Values
-------------

.. autoclass:: tda.orders.Duration
  :members:
  :undoc-members:
.. autoclass:: tda.orders.Session
  :members:
  :undoc-members:

.. autoexception:: tda.orders.InvalidOrderException

-------------
Equity Orders
-------------

.. autoclass:: tda.orders.EquityOrderBuilder
  :members:
  :undoc-members:

  .. automethod:: __init__
