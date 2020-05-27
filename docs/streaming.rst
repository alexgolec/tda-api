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

+++++++++++++++++++++++++++++++
Conventions and Design Patterns
+++++++++++++++++++++++++++++++

------------------
Types of Functions
------------------

The functionality provided by ``tda.stream`` breaks down into several 
categories:

~~~~~~~~~~~~
Subscription
~~~~~~~~~~~~

These methods have names that follow the pattern ``SERVICE_NAME_subs``. These 
methods send a request to enable streaming data for a particular data stream. 
They are *not* thread safe, so they should only be called in series.

~~~~~~~~~~~~~~~~~~~~
Handler Registration
~~~~~~~~~~~~~~~~~~~~

By themselves, the subscription methods outlined above do nothing except cause 
messages to be sent to the client. The ``add_SERVICE_NAME_handler`` methods 
register methods that will receive these messages when they arrive. When 
messages arrive, these handlers will be called serially. There is no limit to 
the number of handlers that can be registered to a service.

---------------------
Data Field Relabeling
---------------------

Under the hood, this API returns JSON with numerical key representing labels: 

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

This documentation describes the various fields and their numerical values.
