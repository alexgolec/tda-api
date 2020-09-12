from collections import deque
from enum import Enum

import asyncio
import copy
import datetime
import inspect
import json
import logging
import tda
import urllib.parse
import websockets

from .exceptions import *
from . import services
from ..utils import EnumEnforcer


def get_logger():
    return logging.getLogger(__name__)


class StreamClient(EnumEnforcer):
    def __init__(self, client, *, account_id=None, enforce_enums=True, ssl_context=None):
        super().__init__(enforce_enums)

        self._ssl_context = ssl_context
        self._client = client

        # If None, will be set by the login() function
        self._account_id = account_id

        # Set by the login() function
        self._account = None
        self._stream_key = None
        self._socket = None
        self._source = None

        # Internal fields
        self._request_id = 0
        # Construct a dict for all services
        self._handlers = dict(
            [(svc, set()) for svc in services.get_service_classes()])

        # we use these to track request responses
        self._awaiting_requests = set()
        self._pending_response_blobs  = {}

        # Logging-related fields
        self.logger = get_logger()

    def _validate_response(self, request, response):
        # Validate request ID
        if response['requestid'] != request['requestid']:
            raise UnexpectedResponse(
                response, 'unexpected requestid: {}'.format(
                    request['requestid']))

        # Validate service
        if response['service'] != request['service']:
            raise UnexpectedResponse(
                response, 'unexpected service: {}'.format(
                    response['service']))

        # Validate command
        if response['command'] != request['command']:
            raise UnexpectedResponse(
                response, 'unexpected command: {}'.format(
                    response['command']))

        # Validate response code
        if response['content']['code'] != 0:
            raise UnexpectedResponseCode(
                response,
                'unexpected response code: {}, msg is \'{}\''.format(
                    response['content']['code'],
                    response['content']['msg']))

    async def _send(self, obj, await_response=True):
        if self._socket is None:
            raise ValueError(
                'Socket not open. Did you forget to call login()?')

        if len(obj['requests']) != 1:
            raise UnsupportedNumberOfRequests

        await self._socket.send(json.dumps(obj))

        if await_response:
            # grab the requestid from the request obj
            request_id = obj['requests'][0]['requestid']

            # register ourselves as awaiting a response
            self._awaiting_requests.add(request_id)
            
            # in case user code is not already looping messages, lets loop here
            while request_id not in self._pending_response_blobs:
                await self.handle_message()

            # fetch, remove, and then validate the response
            response = self._pending_response_blobs.pop(request_id)
            self._validate_response(obj['requests'][0], response)

            return response

    async def _receive(self):
        if self._socket is None:
            raise ValueError(
                'Socket not open. Did you forget to call login()?')

        raw = await self._socket.recv()
        try:
            ret = json.loads(raw)
        except json.decoder.JSONDecodeError as e:
            msg = ('Failed to parse message. This often happens with ' +
                   'unknown symbols or other error conditions. Full ' +
                   'message text: ' + raw)
            raise UnparsableMessage(raw, e, msg)

        self.logger.debug(
            'Receive {}: Returning message from stream: {}'.format(
                self._request_id, json.dumps(ret, indent=4)))

        return ret

    async def _init_from_principals(self, principals):
        # Initialize accounts and streamer keys.
        # Assume a 1-to-1 mapping of streamer keys to accounts.
        accounts = principals['accounts']
        num_accounts = len(accounts)
        assert num_accounts > 0, 'zero accounts found'

        # If there's only one account, use it. Otherwise require an account ID.
        if num_accounts == 1:
            self._account = accounts[0]
        else:
            if self._account_id is None:
                raise ValueError(
                    'multiple accounts found and StreamClient was ' +
                    'initialized with unspecified account_id')
            for idx, account in enumerate(accounts):
                if int(account['accountId']) == self._account_id:
                    self._account = account

        if self._account is None:
            raise ValueError(
                'no account found with account_id {}'.format(
                    self._account_id))

        if self._account_id is None:
            self._account_id = self._account['accountId']

        # Record streamer subscription keys
        stream_keys = principals['streamerSubscriptionKeys']['keys']
        if len(stream_keys) > 1:
            self.logger.warn('Found {} stream keys, using the first one'.format(
                len(stream_keys)))
        self._stream_key = stream_keys[0]['key']

        # Initialize socket
        wss_url = 'wss://{}/ws'.format(
            principals['streamerInfo']['streamerSocketUrl'])
        if self._ssl_context:
            self._socket = await websockets.client.connect(
                    wss_url, ssl=self._ssl_context)
        else:
            self._socket = await websockets.client.connect(wss_url)

        # Initialize miscellaneous parameters
        self._source = principals['streamerInfo']['appId']

    def _make_request(self, *, service, command, parameters):
        request_id = self._request_id
        self._request_id += 1

        request = {
            'service': service,
            'requestid': str(request_id),
            'command': command,
            'account': self._account_id,
            'source': self._source,
            'parameters': parameters
        }

        return request, request_id

    async def _service_op(self, symbols, service, command, field_type,
                          *, fields=None, await_response=True):
        if fields is None:
            fields = field_type.all_fields()
        fields = sorted(self.convert_enum_iterable(fields, field_type))

        request, request_id = self._make_request(
            service=service, command=command,
            parameters={
                'keys': ','.join(symbols),
                'fields': ','.join(str(f) for f in fields)})

        self.logger.debug('Send {}: Sending {}'.format(
            request_id,  json.dumps(request, indent=4)))

        return await self._send({'requests': [request]}, await_response=True)

    async def handle_message(self):
        msg = await self._receive()

        # response
        if 'response' in msg:
            for response in msg['response']:
                request_id = response['requestid']
                if request_id in self._awaiting_requests:
                    self._pending_response_blobs[request_id] = response
                    self._awaiting_requests.remove(request_id)
                else:
                    raise UnexpectedResponse(
                        response, 'unexpected requestid: {}'.format(
                            request_id))
            return

        data = msg.get('data') or msg.get('notify')

        for d in data:
            # If this is a heartbeat, set the service so we can fetch handlers
            if 'heartbeat' in d:
                d['service'] = 'HEARTBEAT'
            service_name = d['service']
            service_class = services.get_service_class(service_name)
            handlers = self._handlers[service_class]
            if len(handlers) > 0:
                # If this is a data msg, we need to normalize fields first
                if 'data' in msg: d = service_class.normalize_fields(d)
                for handler in self._handlers[service_class]:
                    # We cannot "trust" the handler not to modify the
                    # object we pass it, therefore we pass it a copy
                    h = handler(copy.deepcopy(d))

                    # Check if the returned value is awaitable
                    # This allows us to support both sync and async handlers
                    if inspect.isawaitable(h):
                        await h

    ##########################################################################
    # LOGIN

    async def login(self, await_response=True):
        '''
        `Official Documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640574>`__

        Performs initial stream setup:
         * Fetches streaming information from the HTTP client's
           :meth:`~tda.client.Client.get_user_principals` method
         * Initializes the socket
         * Builds and sends and authentication request
         * Waits for response indicating login success

        All stream operations are available after this method completes.
        '''

        # Fetch required data and initialize the client

        # TODO: Figure out which of these are actually needed
        r = self._client.get_user_principals(fields=[
            self._client.UserPrincipals.Fields.STREAMER_CONNECTION_INFO,
            self._client.UserPrincipals.Fields.STREAMER_SUBSCRIPTION_KEYS])
        assert r.ok, r.raise_for_status()
        r = r.json()

        await self._init_from_principals(r)

        # Build and send the request object
        token_ts = datetime.datetime.strptime(
            r['streamerInfo']['tokenTimestamp'], '%Y-%m-%dT%H:%M:%S%z')
        token_ts = int(token_ts.timestamp()) * 1000

        credentials = {
            'userid': self._account_id,
            'token': r['streamerInfo']['token'],
            'company': self._account['company'],
            'segment': self._account['segment'],
            'cddomain': self._account['accountCdDomainId'],
            'usergroup': r['streamerInfo']['userGroup'],
            'accesslevel': r['streamerInfo']['accessLevel'],
            'authorized': 'Y',
            'timestamp': token_ts,
            'appid': r['streamerInfo']['appId'],
            'acl': r['streamerInfo']['acl']
        }

        request_parameters = {
            'credential': urllib.parse.urlencode(credentials),
            'token': r['streamerInfo']['token'],
            'version': '1.0'
        }

        request, request_id = self._make_request(
            service='ADMIN', command='LOGIN',
            parameters=request_parameters)

        return await self._send(
            {'requests': [request]}, await_response=await_response)

    ##########################################################################
    # QOS

    class QOSLevel(Enum):
        '''Quality of service levels'''

        #: 500ms between updates. Fastest available
        EXPRESS = '0'

        #: 750ms between updates
        REAL_TIME = '1'

        #: 1000ms between updates. Default value.
        FAST = '2'

        #: 1500ms between updates
        MODERATE = '3'

        #: 3000ms between updates
        SLOW = '4'

        #: 5000ms between updates
        DELAYED = '5'

    async def quality_of_service(self, qos_level, await_response=True):
        '''
        `Official Documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640578>`__

        Specifies the frequency with which updated data should be sent to the
        client. If not called, the frequency will default to every second.

        :param qos_level: Quality of service level to request. See
                          :class:`QOSLevel` for options.
        '''

        qos_level = self.convert_enum(qos_level, self.QOSLevel)

        request, request_id = self._make_request(
            service='ADMIN', command='QOS',
            parameters={'qoslevel': qos_level})

        return await self._send(
            {'requests': [request]}, await_response=await_response)

    ##########################################################################
    # Streaming API v2.0

    async def subscribe(self, service, symbols=None,
            fields=None, await_response=True):
        if service == services.ACCT_ACTIVITY:
            # Special case where ACCT_ACTIVITY wants our stream key
            symbols = [self._stream_key]
        if fields is None:
            fields = service.Fields.all_fields()
        return await self._service_op(
              symbols, service.__name__, 'SUBS', service.Fields,
              fields=fields, await_response=await_response)

    async def append_subscription(self, service, symbols,
            fields=None, await_response=True):
        if service == services.ACCT_ACTIVITY:
            # Special case where ACCT_ACTIVITY wants our stream key
            symbols = [self._stream_key]
        if fields is None:
            fields = service.Fields.all_fields()
        return await self._service_op(
              symbols, service.__name__, 'ADD', service.Fields,
              fields=service.Fields.all_fields(), await_response=await_response)

    async def unsubscribe(self, service, symbols, await_response=True):
        if service == services.ACCT_ACTIVITY:
            # Special case where ACCT_ACTIVITY wants our stream key
            symbols = [self._stream_key]
        return await self._service_op(
            symbols, service.__name__, 'UNSUBS', service.Fields,
            fields=service.Fields.all_fields(), await_response=await_response)

    def add_handler(self, service, handler):
        self._handlers[service].add(handler)

    def remove_handler(self, service, handler):
        self._handlers[services].remove(handler)

    ##########################################################################
    # HEARTBEAT

    def add_heartbeat_handler(self, handler):
        self.add_handler(services.HEARTBEAT, handler)

    ##########################################################################
    # ACCT_ACTIVITY

    async def account_activity_sub(self):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640580>`__

        Subscribe to account activity for the account id associated with this
        streaming client. See :class:`AccountActivityFields` for more info.
        '''
        await self.subscribe(services.ACCT_ACTIVITY)

    def add_account_activity_handler(self, handler):
        '''
        Adds a handler to the account activity subscription. See
        :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.ACCT_ACTIVITY, handler)

    ##########################################################################
    # CHART_EQUITY

    async def chart_equity_subs(self, symbols):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640587>`__

        Subscribe to equity charts. Behavior is undefined if called multiple
        times.

        :param symbols: Equity symbols to subscribe to.'''
        await self.subscribe(services.CHART_EQUITY, symbols)

    async def chart_equity_add(self, symbols):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640588>`__

        Add a symbol to the equity charts subscription. Behavior is undefined
        if called before :meth:`chart_equity_subs`.

        :param symbols: Equity symbols to add to the subscription.
        '''
        await self.append_subscription(services.CHART_EQUITY, symbols)

    def add_chart_equity_handler(self, handler):
        '''
        Adds a handler to the equity chart subscription. See
        :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.CHART_EQUITY, handler)

    ##########################################################################
    # CHART_FUTURES

    async def chart_futures_subs(self, symbols):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640587>`__

        Subscribe to futures charts. Behavior is undefined if called multiple
        times.

        :param symbols: Futures symbols to subscribe to.
        '''
        await self.subscribe(services.CHART_FUTURES, symbols)

    async def chart_futures_add(self, symbols):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640590>`__

        Add a symbol to the futures chart subscription. Behavior is undefined
        if called before :meth:`chart_futures_subs`.

        :param symbols: Futures symbols to add to the subscription.
        '''
        await self.append_subscription(services.CHART_FUTURES, symbols)

    def add_chart_futures_handler(self, handler):
        '''
        Adds a handler to the futures chart subscription. See
        :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.CHART_FUTURES, handler)

    ##########################################################################
    # QUOTE

    async def level_one_equity_subs(self, symbols, *, fields=None):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640599>`__

        Subscribe to level one equity quote data.

        :param symbols: Equity symbols to receive quotes for
        :param fields: Iterable of :class:`LevelOneEquityFields` representing
                       the fields to return in streaming entries. If unset, all
                       fields will be requested.
        '''
        await self.subscribe(services.QUOTE, symbols, fields)

    def add_level_one_equity_handler(self, handler):
        '''
        Register a function to handle level one equity quotes as they are sent.
        See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.QUOTE, handler)

    ##########################################################################
    # OPTION

    async def level_one_option_subs(self, symbols, *, fields=None):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640602>`__

        Subscribe to level one option quote data.

        :param symbols: Option symbols to receive quotes for
        :param fields: Iterable of :class:`LevelOneOptionFields` representing
                       the fields to return in streaming entries. If unset, all
                       fields will be requested.
        '''
        await self.subscribe(services.OPTION, symbols, fields)

    def add_level_one_option_handler(self, handler):
        '''
        Register a function to handle level one options quotes as they are sent.
        See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.OPTION, handler)

    ##########################################################################
    # LEVELONE_FUTURES

    async def level_one_futures_subs(self, symbols, *, fields=None):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640604>`__

        Subscribe to level one futures quote data.

        :param symbols: Futures symbols to receive quotes for
        :param fields: Iterable of :class:`LevelOneFuturesFields` representing
                       the fields to return in streaming entries. If unset, all
                       fields will be requested.
        '''
        await self.subscribe(services.LEVELONE_FUTURES, symbols, fields)

    def add_level_one_futures_handler(self, handler):
        '''
        Register a function to handle level one futures quotes as they are sent.
        See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.LEVELONE_FUTURES, handler)

    ##########################################################################
    # LEVELONE_FOREX

    async def level_one_forex_subs(self, symbols, *, fields=None):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640606>`__

        Subscribe to level one forex quote data.

        :param symbols: Forex symbols to receive quotes for
        :param fields: Iterable of :class:`LevelOneForexFields` representing
                       the fields to return in streaming entries. If unset, all
                       fields will be requested.
        '''
        await self.subscribe(services.LEVELONE_FOREX, symbols, fields)

    def add_level_one_forex_handler(self, handler):
        '''
        Register a function to handle level one forex quotes as they are sent.
        See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.LEVELONE_FOREX, handler)

    ##########################################################################
    # LEVELONE_FUTURES_OPTIONS

    async def level_one_futures_options_subs(self, symbols, *, fields=None):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640610>`__

        Subscribe to level one futures options quote data.

        :param symbols: Futures options symbols to receive quotes for
        :param fields: Iterable of :class:`LevelOneFuturesOptionsFields`
                       representing the fields to return in streaming entries.
                       If unset, all fields will be requested.
        '''
        await self.subscribe(
                services.LEVELONE_FUTURES_OPTIONS, symbols, fields)

    def add_level_one_futures_options_handler(self, handler):
        '''
        Register a function to handle level one futures options quotes as they
        are sent. See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.LEVELONE_FUTURES_OPTIONS, handler)

    ##########################################################################
    # TIMESALE

    async def timesale_equity_subs(self, symbols, *, fields=None):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640628>`__

        Subscribe to time of sale notifications for equities.

        :param symbols: Equity symbols to subscribe to
        '''
        await self.subscribe(services.TIMESALE_EQUITY, symbols, fields)

    def add_timesale_equity_handler(self, handler):
        '''
        Register a function to handle equity trade notifications as they happen
        See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.TIMESALE_EQUITY, handler)

    async def timesale_futures_subs(self, symbols, *, fields=None):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640628>`__

        Subscribe to time of sale notifications for futures.

        :param symbols: Futures symbols to subscribe to
        '''
        await self.subscribe(services.TIMESALE_FUTURES, symbols, fields)

    def add_timesale_futures_handler(self, handler):
        '''
        Register a function to handle futures trade notifications as they happen
        See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.TIMESALE_FUTURES, handler)

    async def timesale_options_subs(self, symbols, *, fields=None):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640628>`__

        Subscribe to time of sale notifications for options.

        :param symbols: Options symbols to subscribe to
        '''
        await self.subscribe(services.TIMESALE_OPTIONS, symbols, fields)

    def add_timesale_options_handler(self, handler):
        '''
        Register a function to handle options trade notifications as they happen
        See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.TIMESALE_OPTIONS, handler)

    ##########################################################################
    # LISTED_BOOK

    async def listed_book_subs(self, symbols):
        '''
        Subscribe to the NYSE level two order book. Note this stream has no
        official documentation.
        '''
        await self.subscribe(services.LISTED_BOOK, symbols)

    def add_listed_book_handler(self, handler):
        '''
        Register a function to handle level two NYSE book data as it is updated
        See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.LISTED_BOOK, handler)

    ##########################################################################
    # NASDAQ_BOOK

    async def nasdaq_book_subs(self, symbols):
        '''
        Subscribe to the NASDAQ level two order book. Note this stream has no
        official documentation.
        '''
        await self.subscribe(services.NASDAQ_BOOK, symbols)

    def add_nasdaq_book_handler(self, handler):
        '''
        Register a function to handle level two NASDAQ book data as it is
        updated See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.NASDAQ_BOOK, handler)

    ##########################################################################
    # OPTIONS_BOOK

    async def options_book_subs(self, symbols):
        '''
        Subscribe to the level two order book for options. Note this stream has no
        official documentation, and it's not entirely clear what exchange it
        corresponds to. Use at your own risk.
        '''
        await self.subscribe(services.OPTIONS_BOOK, symbols)

    def add_options_book_handler(self, handler):
        '''
        Register a function to handle level two options book data as it is
        updated See :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.OPTIONS_BOOK, handler)

    ##########################################################################
    # NEWS_HEADLINE

    async def news_headline_subs(self, symbols):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640626>`__

        Subscribe to news headlines related to the given symbols.
        '''
        await self.subscribe(services.NEWS_HEADLINE, symbols)

    def add_news_headline_handler(self, handler):
        '''
        Register a function to handle news headlines as they are provided. See
        :ref:`registering_handlers` for details.
        '''
        self.add_handler(services.NEWS_HEADLINE, handler)
