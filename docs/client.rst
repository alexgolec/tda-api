.. highlight:: python
.. py:module:: tda.client

.. _client:

===========
HTTP Client
===========

A naive, unopinionated wrapper around the
`TD Ameritrade HTTP API <https://developer.tdameritrade.com/apis>`_. This
client provides access to all endpoints of the API in as easy and direct a way 
as possible. For example, here is how you can fetch the past 20 years of data 
for Apple stock: 

**Do not attempt to use more than one Client object per token file, as
this will likely cause issues with the underlying OAuth2 session management**

.. code-block:: python

  from tda.auth import easy_client
  from tda.client import Client

  c = easy_client(
          api_key='APIKEY',
          redirect_uri='https://localhost',
          token_path='/tmp/token.pickle')

  resp = c.get_price_history('AAPL',
          period_type=Client.PriceHistory.PeriodType.YEAR,
          period=Client.PriceHistory.Period.TWENTY_YEARS,
          frequency_type=Client.PriceHistory.FrequencyType.DAILY,
          frequency=Client.PriceHistory.Frequency.DAILY)
  assert resp.status_code == httpx.codes.OK
  history = resp.json()

Note we we create a new client using the ``auth`` package as described in
:ref:`auth`. Creating a client directly is possible, but not recommended.

+++++++++++++++++++
Asyncio Support
+++++++++++++++++++

An asynchronous variant is available through a keyword to the client
constructor. This allows for higher-performance API usage, at the cost
of slightly increased application complexity.

.. code-block:: python

  from tda.auth import easy_client
  from tda.client import Client

  async def main():
      c = easy_client(
              api_key='APIKEY',
              redirect_uri='https://localhost',
              token_path='/tmp/token.pickle',
              asyncio=True)

      resp = await c.get_price_history('AAPL',
              period_type=Client.PriceHistory.PeriodType.YEAR,
              period=Client.PriceHistory.Period.TWENTY_YEARS,
              frequency_type=Client.PriceHistory.FrequencyType.DAILY,
              frequency=Client.PriceHistory.Frequency.DAILY)
      assert resp.status_code == httpx.codes.OK
      history = resp.json()

  if __name__ == '__main__':
      import asyncio
      asyncio.run_until_complete(main())

For more examples, please see the ``examples/async`` directory in
GitHub.

+++++++++++++++++++
Calling Conventions
+++++++++++++++++++

Function parameters are categorized as either required or optional. 
Required parameters, such as ``'AAPL'`` in the example above, are passed as 
positional arguments. Optional parameters, like ``period_type`` and the rest, 
are passed as keyword arguments. 

Parameters which have special values recognized by the API are 
represented by `Python enums <https://docs.python.org/3/library/enum.html>`_. 
This is because the API rejects requests which pass unrecognized values, and 
this enum wrapping is provided as a convenient mechanism to avoid consternation 
caused by accidentally passing an unrecognized value.

By default, passing values other than the required enums will raise a
``ValueError``. If you believe the API accepts a value that isn't supported 
here, you can use ``set_enforce_enums`` to disable this behavior at your own 
risk. If you *do* find a supported value that isn't listed here, please open an
issue describing it or submit a PR adding the new functionality.

+++++++++++++
Return Values
+++++++++++++

All methods return a response object generated under the hood by the
`HTTPX <https://www.python-httpx.org/quickstart/#response-content>`__ module. 
For a full listing of what's possible, read that module's documentation. Most if
not all users can simply use the following pattern:

.. code-block:: python

  r = client.some_endpoint()
  assert r.status_code == httpx.codes.OK, r.raise_for_status()
  data = r.json()

The API indicates errors using the response status code, and this pattern will 
raise the appropriate exception if the response is not a success. The data can 
be fetched by calling the ``.json()`` method. 

This data will be pure python data structures which can be directly accessed. 
You can also use your favorite data analysis library's dataframe format using 
the appropriate library. For instance you can create a `pandas
<https://pandas.pydata.org/>`__ dataframe using `its conversion method 
<https://pandas.pydata.org/pandas-docs/stable/reference/api/
pandas.DataFrame.from_dict.html>`__.

**Note:** Because the author has no relationship whatsoever with TD Ameritrade, 
this document makes no effort to describe the structure of the returned JSON 
objects. TDA might change them at any time, at which point this document will 
become silently out of date. Instead, each of the methods described below 
contains a link to the official documentation. For endpoints that return 
meaningful JSON objects, it includes a JSON schema which describes the return 
value. Please use that documentation or your own experimentation when figuring 
out how to use the data returned by this API.

+++++++++++++++++++++
Creating a New Client
+++++++++++++++++++++

99.9% of users should not create their own clients, and should instead follow 
the instructions outlined in :ref:`auth`. For those brave enough to build their
own, the constructor looks like this:

.. automethod:: tda.client.Client.__init__

.. _orders-section:

++++++
Orders
++++++


.. _placing_new_orders:

------------------
Placing New Orders
------------------

Placing new orders can be a complicated task. The :meth:`Client.place_order` method is
used to create all orders, from equities to options. The precise order type is
defined by a complex order spec. TDA provides some `example order specs`_ to
illustrate the process and provides a schema in the `place order documentation 
<https://developer.tdameritrade.com/account-access/apis/post/accounts/
%7BaccountId%7D/orders-0>`__, but beyond that we're on our own.

``tda-api`` includes some helpers, described in :ref:`order_templates`, which 
provide an incomplete utility for creating various order types. While it only 
scratches the surface of what's possible, we encourage you to use that module 
instead of creating your own order specs.

.. _`example order specs`: https://developer.tdameritrade.com/content/place-order-samples

.. automethod:: tda.client.Client.place_order

.. _accessing_existing_orders:

-------------------------
Accessing Existing Orders
-------------------------

.. automethod:: tda.client.Client.get_orders_by_path
.. automethod:: tda.client.Client.get_orders_by_query
.. automethod:: tda.client.Client.get_order
.. autoclass:: tda.client.Client.Order
  :members:
  :undoc-members:

-----------------------
Editing Existing Orders
-----------------------

Endpoints for canceling and replacing existing orders.
Annoyingly, while these endpoints require an order ID, it seems that when
placing new orders the API does not return any metadata about the new order. As 
a result, if you want to cancel or replace an order after you've created it, you 
must search for it using the methods described in :ref:`accessing_existing_orders`.

.. automethod:: tda.client.Client.cancel_order
.. automethod:: tda.client.Client.replace_order

++++++++++++
Account Info
++++++++++++

These methods provide access to useful information about accounts. An incomplete 
list of the most interesting bits:

* Account balances, including available trading balance
* Positions
* Order history

See the official documentation for each method for a complete response schema.

.. automethod:: tda.client.Client.get_account
.. automethod:: tda.client.Client.get_accounts
.. autoclass:: tda.client.Client.Account
  :members:
  :undoc-members:

+++++++++++++++
Instrument Info
+++++++++++++++

Note: symbol fundamentals (P/E ratios, number of shares outstanding, dividend 
yield, etc.) is available using the :attr:`Instrument.Projection.FUNDAMENTAL`
projection.

.. automethod:: tda.client.Client.search_instruments
.. automethod:: tda.client.Client.get_instrument
.. autoclass:: tda.client.Client.Instrument
  :members:
  :undoc-members:


.. _option_chain:

++++++++++++
Option Chain
++++++++++++

Unfortunately, option chains are well beyond the ability of your humble author. 
You are encouraged to read the official API documentation to learn more.

If you *are* knowledgeable enough to write something more substantive here, 
please follow the instructions in :ref:`contributing` to send in a patch.

.. automethod:: tda.client.Client.get_option_chain
.. autoclass:: tda.client.Client.Options
  :members:
  :undoc-members:

+++++++++++++
Price History
+++++++++++++

Fetching price history is somewhat complicated due to the fact that only certain 
combinations of parameters are valid. To avoid accidentally making it impossible
to send valid requests, this method performs no validation on its parameters. If
you are receiving empty requests or other weird return values, see the official
documentation for more details.

.. automethod:: tda.client.Client.get_price_history
.. autoclass:: tda.client.Client.PriceHistory
  :members:
  :undoc-members:
  :member-order: bysource

++++++++++++++
Current Quotes
++++++++++++++

.. automethod:: tda.client.Client.get_quote
.. automethod:: tda.client.Client.get_quotes

+++++++++++++++
Other Endpoints
+++++++++++++++

Note If your account limited to delayed quotes, these quotes will also be 
delayed.

-------------------
Transaction History
-------------------

.. automethod:: tda.client.Client.get_transaction
.. automethod:: tda.client.Client.get_transactions
.. autoclass:: tda.client.Client.Transactions
  :members:
  :undoc-members:

------------
Saved Orders
------------

.. automethod:: tda.client.Client.create_saved_order
.. automethod:: tda.client.Client.delete_saved_order
.. automethod:: tda.client.Client.get_saved_order
.. automethod:: tda.client.Client.get_saved_orders_by_path
.. automethod:: tda.client.Client.replace_saved_order

------------
Market Hours
------------

.. automethod:: tda.client.Client.get_hours_for_multiple_markets
.. automethod:: tda.client.Client.get_hours_for_single_market
.. autoclass:: tda.client.Client.Markets
  :members:
  :undoc-members:

------
Movers
------

.. automethod:: tda.client.Client.get_movers
.. autoclass:: tda.client.Client.Movers
  :members:
  :undoc-members:

-------------------------
User Info and Preferences
-------------------------

.. automethod:: tda.client.Client.get_preferences
.. automethod:: tda.client.Client.get_user_principals
.. automethod:: tda.client.Client.update_preferences
.. autoclass:: tda.client.Client.UserPrincipals
  :members:
  :undoc-members:

----------
Watchlists
----------

**Note**: These methods only support static watchlists, i.e. they cannot access 
dynamic watchlists.

.. automethod:: tda.client.Client.create_watchlist
.. automethod:: tda.client.Client.delete_watchlist
.. automethod:: tda.client.Client.get_watchlist
.. automethod:: tda.client.Client.get_watchlists_for_multiple_accounts
.. automethod:: tda.client.Client.get_watchlists_for_single_account
.. automethod:: tda.client.Client.replace_watchlist
.. automethod:: tda.client.Client.update_watchlist
