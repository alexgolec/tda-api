.. _utils:

=========
Utilities
=========

This section describes miscellaneous utility methods provided by ``tda-api``. 
All utilities are presented under the ``Utils`` class:

.. autoclass:: tda.utils.Utils

  .. automethod:: __init__
  .. automethod:: set_account_id

-------------------------
Get the Most Recent Order
-------------------------

For successfully placed orders, :meth:`tda.client.Client.place_order` returns 
the ID of the newly created order, encoded in the ``r.headers['Location']`` 
header. This method inspects the response and extracts the order ID from the 
contents, if it's there. This order ID can then be used to monitor or modify the
order as described in the :ref:`Client documentation <orders-section>`. Example
usage:

.. code-block:: python

  # Assume client and order already exist and are valid
  account_id = 123456
  r = client.place_order(account_id, order)
  assert r.status_code == httpx.codes.OK, r.raise_for_status()
  order_id = Utils(client, account_id).extract_order_id(r)
  assert order_id is not None

.. automethod:: tda.utils.Utils.extract_order_id
