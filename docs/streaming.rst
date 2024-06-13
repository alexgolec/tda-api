.. highlight:: python
.. py:module:: tda.streaming

.. _stream:


================
Streaming Client
================

A wrapper around the
`TD Ameritrade Streaming API <https://developer.tdameritrade.com/content/
streaming-data>`__. This API is a 
websockets-based streaming API that provides to up-to-the-second data on market 
activity. Most impressively, it provides realtime data, including Level Two and 
time of sale data for major equities, options, and futures exchanges. 

Here's an example of how you can receive book snapshots of ``GOOG`` (note if you 
run this outside regular trading hours you may not see anything):

.. code-block:: python

  from tda.auth import easy_client
  from tda.client import Client
  from tda.streaming import StreamClient

  import asyncio
  import json

  client = easy_client(
          api_key='APIKEY',
          redirect_uri='https://localhost',
          token_path='/tmp/token.json')
  stream_client = StreamClient(client, account_id=1234567890)
  stream_client.add_nasdaq_book_handler(
          lambda msg: print(json.dumps(msg, indent=4)))

  async def read_stream():
      await stream_client.login()
      await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
 
      def print_message(message):
        print(json.dumps(message, indent=4))

      # Always add handlers before subscribing because many streams start sending 
      # data immediately after success, and messages with no handlers are dropped.
      stream_client.add_nasdaq_book_handler(print_message)
      await stream_client.nasdaq_book_subs(['GOOG'])

      while True:
          await stream_client.handle_message()

  asyncio.run(read_stream())

This API uses Python
`coroutines <https://docs.python.org/3/library/asyncio-task.html>`__ to simplify 
implementation and preserve performance. As a result, it requires Python 3.8 or 
higher to use. ``tda.stream`` will not be available on older versions of Python.


++++++++++++
Use Overview
++++++++++++

The example above demonstrates the end-to-end workflow for using ``tda.stream``. 
There's more in there than meets the eye, so let's dive into the details.


----------
Logging In
----------

Before we can perform any stream operations, the client must be logged in to the 
stream. Unlike the HTTP client, in which every request is authenticated using a 
token, this client sends unauthenticated requests and instead authenticates the 
entire stream. As a result, this login process is distinct from the token 
generation step that's used in the HTTP client.

Stream login is accomplished simply by calling :meth:`StreamClient.login()`. Once
this happens successfully, all stream operations can be performed. Attemping to
perform operations that require login before this function is called raises an
exception.

.. automethod:: tda.streaming.StreamClient.login


--------------------------
Setting Quality of Service
--------------------------

By default, the stream's update frequency is set to 1000ms. The frequency can be
increased by calling the ``quality_of_service`` function and passing an
appropriate ``QOSLevel`` value.

.. automethod:: tda.streaming::StreamClient.quality_of_service
.. autoclass:: tda.streaming::StreamClient.QOSLevel
  :members:
  :undoc-members:


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

Some services, notably :ref:`equity_charts` and :ref:`futures_charts`, 
offer ``SERVICE_NAME_add`` functions which can be used to add symbols to the 
stream after the subscription has been created. For others, calling the 
subscription methods again seems to clear the old subscription and create a new 
one. Note this behavior is not officially documented, so this interpretation may 
be incorrect.

-------------------------
Un-Subscribing to Streams
-------------------------

These functions have names that follow the pattern ``SERVICE_NAME_unsubs``. These
functions send a request to disable the symbols of a streaming data for a particular data stream.
They are *not* thread safe, so they should only be called in series.

When unsubscribing to services with symbols, the service behaves such that the initial set of subscribe symbols
minus the set of unsubscribe symbols -- as a result you get set difference and the set of symbols that were subscribe
but is not in unsubscribe will continue to publish to your handler.

It's known but not confirmed that if you unsubscribe from all streams, TD will close your stream if there are no other
activities in 20 seconds. Please refer to this comment : https://github.com/alexgolec/tda-api/pull/256#issuecomment-939194648
for ``Case: When no services are subscribed for 20 seconds - verify the last 2 messages from td``

--------------------
Registering Handlers
--------------------

By themselves, the subscription functions outlined above do nothing except cause 
messages to be sent to the client. The ``add_SERVICE_NAME_handler`` functions 
register functions that will receive these messages when they arrive. When 
messages arrive, these handlers will be called serially. There is no limit to 
the number of handlers that can be registered to a service.


.. _registering_handlers:

-----------------
Handling Messages
-----------------

Once the stream client is properly logged in, subscribed to streams, and has 
handlers registered, we can start handling messages. This is done simply by 
awaiting on the ``handle_message()`` function. This function reads a single 
message and dispatches it to the appropriate handler or handlers.

If a message is received for which no handler is registered, that message is 
ignored.

Handlers should take a single argument representing the stream message received:

.. code-block:: python

  import json

  def sample_handler(msg):
      print(json.dumps(msg, indent=4))


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
For instance, the message above would be relabeled as:

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

Some streams, such as the ones described in :ref:`level_one`, allow you to
specify a subset of fields to be returned. Subscription handlers for these
services take a list of the appropriate field enums the extra ``fields``
parameter. If nothing is passed to this parameter, all supported fields are 
requested.


-----------------------------
Interpreting Sequence Numbers
-----------------------------

Many endpoints include a ``seq`` parameter in their data contents. The official
documentation is unclear on the interpretation of this value: the `time of sale 
<https://developer.tdameritrade.com/content/streaming-data#_Toc504640628>`__ 
documentation states that messages containing already-observed values of ``seq``
can be ignored, but other streams contain this field both in their metadata and 
in their content, and yet their documentation doesn't mention ignoring any
``seq`` values.

This presents a design choice: should ``tda-api`` ignore duplicate ``seq``
values on users' behalf? Given the ambiguity of the documentation, it was
decided to not ignore them and instead pass them to all handlers. Clients 
are encouraged to use their judgment in handling these values.


---------------------
Unimplemented Streams
---------------------

This document lists the streams supported by ``tda-api``. Eagle-eyed readers may 
notice that some streams are described in the documentation but were not 
implemented. This is due to complexity or anticipated lack of interest. If you 
feel you'd like a stream added, please file an issue 
`here <https://github.com/alexgolec/tda-api/issues>`__ or see the 
`contributing guidelines <https://github.com/alexgolec/tda-api/blob/master/
CONTRIBUTING.rst>`__ to learn how to add the functionality yourself.


++++++++++++++++++++++++++++++
Enabling Real-Time Data Access
++++++++++++++++++++++++++++++

By default, TD Ameritrade delivers delayed quotes. However, as of this writing,
real time streaming is available for all streams, including quotes and level two 
depth of book data. It is also available for free, which in the author's opinion
is an impressive feature for a retail brokerage. For most users it's enough to 
`sign the relevant exchange agreements <https://invest.ameritrade.com/grid/p/
site#r=jPage/cgi-bin/apps/u/AccountSettings>`__ and then `subscribe to the
relevant streams <https://invest.ameritrade.com/grid/p/
site#r=jPage/cgi-bin/apps/u/Subscriptions>`__, although your mileage may vary.

Please remember that your use of this API is subject to agreeing to 
TDAmeritrade's terms of service. Please don't reach out to us asking for help 
enabling real-time data. Answers to most questions are a Google search away.


++++++++++++
OHLCV Charts
++++++++++++

These streams summarize trading activity on a minute-by-minute basis for 
equities and futures, providing OHLCV (Open/High/Low/Close/Volume) data.


.. _equity_charts:

-------------
Equity Charts
-------------

Minute-by-minute OHLCV data for equities.

.. automethod:: tda.streaming::StreamClient.chart_equity_subs
.. automethod:: tda.streaming::StreamClient.chart_equity_unsubs
.. automethod:: tda.streaming::StreamClient.chart_equity_add
.. automethod:: tda.streaming::StreamClient.add_chart_equity_handler
.. autoclass:: tda.streaming::StreamClient.ChartEquityFields
  :members:
  :undoc-members:


.. _futures_charts:

--------------
Futures Charts
--------------

Minute-by-minute OHLCV data for futures.

.. automethod:: tda.streaming::StreamClient.chart_futures_subs
.. automethod:: tda.streaming::StreamClient.chart_futures_unsubs
.. automethod:: tda.streaming::StreamClient.chart_futures_add
.. automethod:: tda.streaming::StreamClient.add_chart_futures_handler
.. autoclass:: tda.streaming::StreamClient.ChartFuturesFields
  :members:
  :undoc-members:


.. _level_one:

++++++++++++++++
Level One Quotes
++++++++++++++++

Level one quotes provide an up-to-date view of bid/ask/volume data. In 
particular they list the best available bid and ask prices, together with the 
requested volume of each. They are updated live as market conditions change.


---------------
Equities Quotes
---------------

Level one quotes for equities traded on NYSE, AMEX, and PACIFIC.

.. automethod:: tda.streaming::StreamClient.level_one_equity_subs
.. automethod:: tda.streaming::StreamClient.level_one_equity_unsubs
.. automethod:: tda.streaming::StreamClient.add_level_one_equity_handler
.. autoclass:: tda.streaming::StreamClient.LevelOneEquityFields
  :members:
  :undoc-members:


--------------
Options Quotes
--------------

Level one quotes for options. Note you can use 
:meth:`Client.get_option_chain() <tda.client.Client.get_option_chain>` to fetch
available option symbols.

.. automethod:: tda.streaming::StreamClient.level_one_option_subs
.. automethod:: tda.streaming::StreamClient.level_one_option_unsubs
.. automethod:: tda.streaming::StreamClient.add_level_one_option_handler
.. autoclass:: tda.streaming::StreamClient.LevelOneOptionFields
  :members:
  :undoc-members:


--------------
Futures Quotes
--------------

Level one quotes for futures.

.. automethod:: tda.streaming::StreamClient.level_one_futures_subs
.. automethod:: tda.streaming::StreamClient.level_one_futures_unsubs
.. automethod:: tda.streaming::StreamClient.add_level_one_futures_handler
.. autoclass:: tda.streaming::StreamClient.LevelOneFuturesFields
  :members:
  :undoc-members:


------------
Forex Quotes
------------

Level one quotes for foreign exchange pairs.

.. automethod:: tda.streaming::StreamClient.level_one_forex_subs
.. automethod:: tda.streaming::StreamClient.level_one_forex_unsubs
.. automethod:: tda.streaming::StreamClient.add_level_one_forex_handler
.. autoclass:: tda.streaming::StreamClient.LevelOneForexFields
  :members:
  :undoc-members:


----------------------
Futures Options Quotes
----------------------

Level one quotes for futures options.

.. automethod:: tda.streaming::StreamClient.level_one_futures_options_subs
.. automethod:: tda.streaming::StreamClient.level_one_futures_options_unsubs
.. automethod:: tda.streaming::StreamClient.add_level_one_futures_options_handler
.. autoclass:: tda.streaming::StreamClient.LevelOneFuturesOptionsFields
  :members:
  :undoc-members:


.. _level_two:

++++++++++++++++++++
Level Two Order Book 
++++++++++++++++++++

Level two streams provide a view on continuous order books of various securities.
The level two order book describes the current bids and asks on the market, and 
these streams provide snapshots of that state.

Due to the lack of `official documentation <https://developer.tdameritrade.com/
content/streaming-data#_Toc504640612>`__, these streams are largely reverse 
engineered. While the labeled data represents a best effort attempt to
interpret stream fields, it's possible that something is wrong or incorrectly
labeled.

The documentation lists more book types than are implemented here. In 
particular, it also lists ``FOREX_BOOK``, ``FUTURES_BOOK``, and
``FUTURES_OPTIONS_BOOK`` as accessible streams. All experimentation has resulted 
in these streams refusing to connect, typically returning errors about 
unavailable services. Due to this behavior and the lack of official 
documentation for book streams generally, ``tda-api`` assumes these streams are not
actually implemented, and so excludes them. If you have any insight into using
them, please
`let us know <https://github.com/alexgolec/tda-api/issues>`__.


-------------------------------------
Equities Order Books: NYSE and NASDAQ
-------------------------------------

``tda-api`` supports level two data for NYSE and NASDAQ, which are the two major 
exchanges dealing in equities, ETFs, etc. Stocks are typically listed on one or 
the other, and it is useful to learn about the differences between them:

 * `"The NYSE and NASDAQ: How They Work" on Investopedia
   <https://www.investopedia.com/articles/basics/03/103103.asp>`__
 * `"Here's the difference between the NASDAQ and NYSE" on Business Insider
   <https://www.businessinsider.com/
   heres-the-difference-between-the-nasdaq-and-nyse-2017-7>`__
 * `"Can Stocks Be Traded on More Than One Exchange?" on Investopedia
   <https://www.investopedia.com/ask/answers/05/stockmultipleexchanges.asp>`__

You can identify on which exchange a symbol is listed by using
:meth:`Client.search_instruments() <tda.client.Client.search_instruments>`:

.. code-block:: python

  r = c.search_instruments(['GOOG'], projection=c.Instrument.Projection.FUNDAMENTAL)
  assert r.status_code == httpx.codes.OK, r.raise_for_status()
  print(r.json()['GOOG']['exchange'])  # Outputs NASDAQ

However, many symbols have order books available on these streams even though 
this API call returns neither NYSE nor NASDAQ. The only sure-fire way to find out
whether the order book is available is to attempt to subscribe and see what 
happens.

Note to preserve equivalence with what little documentation there is, the NYSE
book is called "listed." Testing indicates this stream corresponds to the NYSE
book, but if you find any behavior that suggests otherwise please
`let us know <https://github.com/alexgolec/tda-api/issues>`__.

.. automethod:: tda.streaming::StreamClient.listed_book_subs
.. automethod:: tda.streaming::StreamClient.listed_book_unsubs
.. automethod:: tda.streaming::StreamClient.add_listed_book_handler

.. automethod:: tda.streaming::StreamClient.nasdaq_book_subs
.. automethod:: tda.streaming::StreamClient.nasdaq_book_unsubs
.. automethod:: tda.streaming::StreamClient.add_nasdaq_book_handler


------------------
Options Order Book
------------------

This stream provides the order book for options. It's not entirely clear what 
exchange it aggregates from, but it's been tested to work and deliver data. The 
leading hypothesis is that it is the order book for the 
`Chicago Board of Exchange <https://www.cboe.com/us/options>`__ options 
exchanges, although this is an admittedly an uneducated guess.

.. automethod:: tda.streaming::StreamClient.options_book_subs
.. automethod:: tda.streaming::StreamClient.options_book_unsubs
.. automethod:: tda.streaming::StreamClient.add_options_book_handler


++++++++++++
Time of Sale
++++++++++++

The data in :ref:`level_two` describes the bids and asks for various 
instruments, but by itself is insufficient to determine when trades actually 
take place. The time of sale streams notify on trades as they happen. Together 
with the level two data, they provide a fairly complete picture of what is 
happening on an exchange.

All time of sale streams uss a common set of fields:

.. autoclass:: tda.streaming::StreamClient.TimesaleFields
  :members:
  :undoc-members:


-------------
Equity Trades
-------------

.. automethod:: tda.streaming::StreamClient.timesale_equity_subs
.. automethod:: tda.streaming::StreamClient.timesale_equity_unsubs
.. automethod:: tda.streaming::StreamClient.add_timesale_equity_handler


--------------
Futures Trades
--------------

.. automethod:: tda.streaming::StreamClient.timesale_futures_subs
.. automethod:: tda.streaming::StreamClient.timesale_futures_unsubs
.. automethod:: tda.streaming::StreamClient.add_timesale_futures_handler


--------------
Options Trades
--------------

This stream is defined and will connect, however it appears that it does not
provide data. Connecting to it results in heartbeat messages that indicate that 
the stream is open, but to date we haven't seen any data be passed through.
We currently believe this is an issue on TDA's side. 

.. automethod:: tda.streaming::StreamClient.timesale_options_subs
.. automethod:: tda.streaming::StreamClient.timesale_options_unsubs
.. automethod:: tda.streaming::StreamClient.add_timesale_options_handler


++++++++++++++
News Headlines
++++++++++++++

This stream returns news headlines for a set of symbols. If you encounter issues
activating this stream or receive an error response from TDA, please reach out to
our `Discord server <https://discord.gg/BEr6y6Xqyv>`__ for help.

.. automethod:: tda.streaming::StreamClient.news_headline_subs
.. automethod:: tda.streaming::StreamClient.news_headline_unsubs
.. automethod:: tda.streaming::StreamClient.add_news_headline_handler
.. autoclass:: tda.streaming::StreamClient.NewsHeadlineFields
  :members:
  :undoc-members:


++++++++++++++++
Account Activity
++++++++++++++++

This stream allows you to monitor your account activity, including order 
execution/cancellation/expiration/etc. ``tda-api`` provide utilities for setting 
up and reading the stream, but leaves the task of parsing the `response XML 
object <https://developer.tdameritrade.com/content/streaming-data#_Toc504640581>`__
to the user.

.. automethod:: tda.streaming::StreamClient.account_activity_sub
.. automethod:: tda.streaming::StreamClient.account_activity_unsubs
.. automethod:: tda.streaming::StreamClient.add_account_activity_handler
.. autoclass:: tda.streaming::StreamClient.AccountActivityFields
  :members:
  :undoc-members:


+++++++++++++++
Troubleshooting
+++++++++++++++

There are a number of issues you might encounter when using the streaming 
client. This section attempts to provide a non-authoritative listing of the 
issues you may encounter when using this client. 

Unfortunately, use of the streaming client by non-TDAmeritrade apps is poorly
documented and apparently completely unsupported. This section attempts
to provide a non-authoritative listing of the issues you may encounter, but 
please note that these are best effort explanations resulting from reverse 
engineering and crowdsourced experience. Take them with a grain of salt. 

If you have specific questions, please join our `Discord server 
<https://discord.gg/BEr6y6Xqyv>`__ to discuss with the community.


-------------------------------------------------------------------------------
``ConnectionClosedOK: code = 1000 (OK), no reason`` Immediately on Stream Start
-------------------------------------------------------------------------------

There are a few known causes for this issue:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Streaming Account ID Doesn't Match Token Account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TDA allows you to link multiple accounts together, so that logging in to one 
main account allows you to have access to data from all other linked accounts. 
This is not a problem for the HTTP client, but the streaming client is a little 
more restrictive. In particular, it appears that opening a ``StreamClient`` with 
an account ID that is different from the account ID corresponding to the username
that was used to create the token is disallowed. 

If you're encountering this issue, make sure you are using the account ID of the 
account which was used during token login. If you're unsure which account was 
used to create the token, delete your token and create a new one, taking note of 
the account ID.


~~~~~~~~~~~~~~~~~~~~~~~~~~~
Multiple Concurrent Streams
~~~~~~~~~~~~~~~~~~~~~~~~~~~

TDA allows only one open stream per account ID.  If you open a second one, it 
will immediately close itself with this error. This is not a limitation of 
``tda-api``, this is a TDAmeritrade limitation. If you want to use multiple 
streams, you need to have multiple accounts, create a separate token under each, 
and pass each one's account ID into its own client. 


--------------------------------------------------------------------------------
``ConnectionClosedError: code = 1006 (connection closed abnormally [internal])``
--------------------------------------------------------------------------------

TDA has the right to kill the connection at any time for any reason, and this 
error appears to be a catchall for these sorts of failures. If you are 
encountering this error, it is almost certainly not the fault of the 
``tda-api`` library, but rather either an internal failure on TDA's side or a 
failure in the logic of your own code. 

That being said, there have been a number of situations where this error was 
encountered, and this section attempts to record the resolution of these 
failures. 


~~~~~~~~~~~~~~~~~~~~~~~~
Your Handler is Too Slow
~~~~~~~~~~~~~~~~~~~~~~~~

``tda-api`` cannot perform websocket message acknowledgement when your handler 
code is running. As a result, if your handler code takes longer than the stream 
update frequency, a backlog of unacknowledged messages will develop. TDA has 
been observed to terminate connections when many messages are unacknowledged. 

Fixing this is a task for the application developer: if you are writing to a 
database or filesystem as part of your handler, consider profiling it to make 
the write faster. You may also consider deferring your writes so that slow 
operations don't happen in the hotpath of the message handler. 


---------------
JSONDecodeError
---------------

This is an error that is most often raised when TDA sends an invalid JSON 
string. See :ref:`custom_json_decoding` for details.

For reasons known only to TDAmeritrade's development team, the API occasionally 
emits invalid stream messages for some endpoints. Because this issue does not 
affect all endpoints, and because ``tda-api``'s authors are not in the business 
of handling quirks of an API they don't control, the library simply passes these
errors up to the user. 

However, some applications cannot handle complete failure. What's more, some 
users have insight into how to work around these decoder errors. The streaming 
client supports setting a custom JSON decoder to help with this: 

.. automethod:: tda.streaming.StreamClient.set_json_decoder

Users are free to implement their own JSON decoders by subclassing the following 
abstract base class: 

.. autoclass:: tda.streaming::StreamJsonDecoder
  :members:
  :undoc-members:

Users looking for an out-of-the-box solution can consider using the 
community-maintained decoder described in :ref:`custom_json_decoding`. Note that 
while this decoder is constantly improving, it is not guaranteed to solve 
whatever JSON decoding errors your may be encountering. 
