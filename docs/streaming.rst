.. highlight:: python
.. py:module:: tda.streaming

.. _stream:

================
Streaming Client
================

A minimally-opinionated wapper around the
`TD Ameritrade Streaming API <https://developer.tdameritrade.com/content/streaming-data>`__. This API is a 
websockets-based interface to extensive up-to-the-second data on market 
activity. Most impressively, it allows (apparently truncated) Level Two data for 
all major markets for equities, options, and futures.

Here's an example of how you can receive book snapshots of ``GOOG`` (note if you 
run this outside regular trading hours you may not see anything:)

.. code-block:: python

  from tda.auth import easy_client
  from tda.client import Client
  from tda.streaming import StreamClient

  import asyncio
  import json

  client = easy_client(
          api_key='APIKEY',
          redirect_uri='https://localhost',
          token_path='/tmp/token.pickle')
  stream_client = StreamClient(client, account_id=1234567890)

  async def read_stream():
      await stream_client.login()
      await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
      await stream_client.nasdaq_book_subs(['GOOG'])
      stream_client.add_timesale_options_handler(
              lambda msg: print(json.dumps(msg, indent=4)))

      while True:
          await stream_client.handle_message()

  asyncio.get_event_loop().run_until_complete(read_stream())

This API uses Python
`coroutines <https://docs.python.org/3/library/asyncio-task.html>`_ to simplify 
implementation and preserve performance. As a result, it requires Python 3.8 or 
higher to use. Attempting to import ``tda.stream`` on a too-old version of 
Python will result in an ``EnvironmentError``.

++++++++++++
Use Overview
++++++++++++

The example above demonstrates the end-to-end workflow for using ``tda.stream``. 
In this section, we dive into what each part does and why it's important.

----------
Logging In
----------

Before any stream operations can be performed, the client must first be logged 
in. Note this is distinct from the token generation step that has to happen
before we create an HTTP client.

Stream login is accomplished simply by calling ``login()``. Once this happens 
successfully, all stream operations can be performed. Attemping to perform
operations that require login before this function is called raises an exception.

----------------------
Subscribing to Streams
----------------------

These functions have names that follow the pattern ``SERVICE_NAME_subs``. These 
functions send a request to enable streaming data for a particular data stream. 
They are *not* thread safe, so they should only be called in series.

When subscriptions are called multiple times on the same stream, the results 
vary. What's more, these results aren't documented in the official 
documentation. As a result, it's recommended not to call a subscription function 
more than once for any given stream.

Some services, notably the ``CHART_EQUITY`` and ``CHART_FUTURES`` services, 
offer ``SERVICE_NAME_add`` functions which can be used to augment the subscription 
with additional symbols.

--------------------
Registering Handlers
--------------------

By themselves, the subscription functions outlined above do nothing except cause 
messages to be sent to the client. The ``add_SERVICE_NAME_handler`` functions 
register functions that will receive these messages when they arrive. When 
messages arrive, these handlers will be called serially. There is no limit to 
the number of handlers that can be registered to a service.

-----------------
Handling Messages
-----------------

Once the stream client is properly logged in, subscribed to streams, and has 
handlers registered, we can start handling messages. This is done simply by 
awaiting on the ``handle_message()`` function. This function reads a single 
message and dispatches it to the appropriate handler or handlers.

If a message is received for which no handler is registered, that message is 
ignored.

---------------------
Data Field Relabeling
---------------------

Under the hood, this API returns JSON objects with numerical key representing
labels: 

.. code-block:: python

  {
      "service": "CHART_EQUITY",
      "timestamp": 1590597641293,
      "command": "SUBS",
      "content": [
          {
              "seq": 985,
              "key": "MSFT",
              "1": 179.445,
              "2": 179.57,
              "3": 179.4299,
              "4": 179.52,
              "5": 53742.0,
              "6": 339,
              "7": 1590597540000,
              "8": 18409
          },
      ]
  }

These labels are tricky to decode, and require a knowledge of the documentation 
to decode properly. ``tda-api`` makes your life easier by doing this decoding 
for you, replacing numerical labels with strings pulled from the documentation. 
For instance, the message above would be translated to:

.. code-block:: python

  {
      "service": "CHART_EQUITY",
      "timestamp": 1590597641293,
      "command": "SUBS",
      "content": [
          {
              "seq": 985,
              "key": "MSFT",
              "OPEN_PRICE": 179.445,
              "HIGH_PRICE": 179.57,
              "LOW_PRICE": 179.4299,
              "CLOSE_PRICE": 179.52,
              "VOLUME": 53742.0,
              "SEQUENCE": 339,
              "CHART_TIME": 1590597540000,
              "CHART_DAY": 18409
          },
      ]
  }

This documentation describes the various fields and their numerical values. You 
can find them by investigating the various enum classes ending in ``***Fields``.

