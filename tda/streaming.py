from collections import defaultdict, deque
from enum import Enum

import asyncio
import copy
import datetime
import json
import urllib.parse
import websockets

from .utils import EnumEnforcer


class BaseFieldEnum(Enum):
    @classmethod
    def all_fields(cls):
        return list(cls)

    @classmethod
    def key_mapping(cls):
        try:
            return cls._key_mapping
        except AttributeError:
            cls._key_mapping = dict(
                    (str(enum.value), name)
                    for name, enum in cls.__members__.items())
            return cls._key_mapping

    @classmethod
    def relabel_message(cls, old_msg, new_msg):
        # Make a copy of the items so we can modify the dict during iteration
        for old_key, value in list(old_msg.items()):
            if old_key in cls.key_mapping():
                new_key = cls.key_mapping()[old_key]
                new_msg[new_key] = value
                del new_msg[old_key]


class UnexpectedResponse(Exception):
    def __init__(self, response, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = response


class UnexpectedResponseCode(Exception):
    def __init__(self, response, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = response


class Handler:
    def __init__(self, func, field_enum_type):
        self._func = func
        self._field_enum_type = field_enum_type

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def label_message(self, msg):
        if 'content' in msg:
            new_msg = copy.deepcopy(msg)
            for idx in range(len(msg['content'])):
                self._field_enum_type.relabel_message(msg['content'][idx],
                        new_msg['content'][idx])
            return new_msg
        else:
            return msg


class StreamClient(EnumEnforcer):

    def __init__(self, client, *, account_id=None, enforce_enums=True):
        super().__init__(enforce_enums)

        self.client = client

        # If None, will be set by the login() function
        self.account_id = account_id

        # Set by the login() function
        self._account = None
        self._socket = None
        self._source = None

        # Internal fields
        self._request_id = 0
        self._handlers = defaultdict(list)

        # When listening for responses, we sometimes encounter non-response
        # messages. Since this happens outside the context of the handler
        # dispatcher, we cannot handle these messages. However, we still need to
        # deliver these messages. This list records the messages that were read
        # from the stream but not handled yet. Messages should be read from this
        # list before they are read from the stream.
        self._overflow_items = deque()

    async def __send(self, obj):
        await self._socket.send(json.dumps(obj))

    async def __receive(self):
        if len(self._overflow_items) > 0:
            ret = self._overflow_items.pop()
        else:
            raw = await self._socket.recv()
            ret = json.loads(raw)
        return ret

    async def __init_from_principals(self, principals):
        # Initialize accounts
        accounts = principals['accounts']
        num_accounts = len(accounts)
        assert num_accounts > 0, 'zero accounts found'

        if num_accounts == 1:
            return accounts[0]

        if self.account_id is None:
            raise ValueError(
                'multiple accounts found StreamClient was initialized ' +
                'with unspecified account_id')

        for account in accounts:
            if int(account['accountId']) == self.account_id:
                self._account = account

        if self._account is None:
            raise ValueError(
                'no account found with account_id {}'.format(
                    self.account_id))

        if self.account_id is None:
            self.account_id = self._account['accountId']

        # Initialize socket
        wss_url = 'wss://{}/ws'.format(
            principals['streamerInfo']['streamerSocketUrl'])
        self._socket = await websockets.client.connect(wss_url)

        # Initialize miscellaneous parameters
        self._source = principals['streamerInfo']['appId']

    def __make_request(self, *, service, command, parameters):
        request_id = self._request_id
        self._request_id += 1

        request = {
            "service": service,
            "requestid": str(request_id),
            "command": command,
            "account": self.account_id,
            "source": self._source,
            "parameters": parameters
        }

        return request, request_id

    async def __await_response(self, request_id):
        deferred_messages = []

        # Context handler to ensure we always append the deferred messages,
        # regardless of how we exit the await loop below
        class WriteDeferredMessages:
            def __init__(self, this_client):
                self.this_client = this_client

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.this_client._overflow_items.extendleft(deferred_messages)

        with WriteDeferredMessages(self):
            while True:
                resp = await self.__receive()

                if 'response' not in resp:
                    deferred_messages.append(resp)
                    continue

                # Validate response
                resp_request_id = int(resp['response'][0]['requestid'])
                assert resp_request_id == request_id, \
                    'unexpected requestid: {}'.format(resp_request_id)

                resp_code = resp['response'][0]['content']['code']
                if resp_code != 0:
                    raise UnexpectedResponseCode(
                        resp,
                        'unexpected response code: {}, msg is \'{}\''.format(
                            resp_code,
                            resp['response'][0]['content']['msg']))

                break

    async def __service_op(self, symbols, service, command, field_type,
                           *, fields=None):
        if fields is None:
            fields = field_type.all_fields()
        fields = sorted(self.convert_enum_iterable(fields, field_type))

        request, request_id = self.__make_request(
            service=service, command=command,
            parameters={
                'keys': ','.join(symbols),
                'fields': ','.join(str(f) for f in fields)})

        await self.__send({'requests': [request]})
        await self.__await_response(request_id)

    async def handle_message(self):
        msg = await self.__receive()

        # response
        if 'response' in msg:
            raise UnexpectedResponse(msg)

        # data
        if 'data' in msg:
            for d in msg['data']:
                if d['service'] in self._handlers:
                    for handler in self._handlers[d['service']]:
                        labeled_d = handler.label_message(d)
                        handler(labeled_d)

        # notify
        if 'notify' in msg:
            pass

    ##########################################################################
    # LOGIN

    async def login(self):
        # Fetch required data and initialize the client

        # TODO: Figure out which of these are actually needed
        r = self.client.get_user_principals(fields=[
            self.client.UserPrincipals.Fields.PREFERENCES,
            self.client.UserPrincipals.Fields.STREAMER_CONNECTION_INFO,
            self.client.UserPrincipals.Fields.STREAMER_SUBSCRIPTION_KEYS,
            self.client.UserPrincipals.Fields.SURROGATE_IDS])
        assert r.ok, r.raise_for_status()
        r = r.json()

        await self.__init_from_principals(r)

        # Build and send the request object
        token_ts = datetime.datetime.strptime(
            r['streamerInfo']['tokenTimestamp'], "%Y-%m-%dT%H:%M:%S%z")
        token_ts = int(token_ts.timestamp()) * 1000

        credentials = {
            "userid": self.account_id,
            "token": r['streamerInfo']['token'],
            "company": self._account['company'],
            "segment": self._account['segment'],
            "cddomain": self._account['accountCdDomainId'],
            "usergroup": r['streamerInfo']['userGroup'],
            "accesslevel": r['streamerInfo']['accessLevel'],
            "authorized": "Y",
            "timestamp": token_ts,
            "appid": r['streamerInfo']['appId'],
            "acl": r['streamerInfo']['acl']
        }

        request_parameters = {
            "credential": urllib.parse.urlencode(credentials),
            "token": r['streamerInfo']['token'],
            "version": "1.0"
        }

        request, request_id = self.__make_request(
            service='ADMIN', command='LOGIN',
            parameters=request_parameters)

        await self.__send({'requests': [request]})
        await self.__await_response(request_id)

    ##########################################################################
    # QOS

    class QOSLevel(Enum):
        EXPRESS = '0'
        REAL_TIME = '1'
        FAST = '2'
        MODERATE = '3'
        SLOW = '4'
        DELAYED = '5'

    async def quality_of_service(self, qos_level):
        qos_level = self.convert_enum(qos_level, self.QOSLevel)

        request, request_id = self.__make_request(
            service='ADMIN', command='QOS',
            parameters={'qoslevel': qos_level})

        await self.__send({'requests': [request]})
        await self.__await_response(request_id)

    ##########################################################################
    # CHART_EQUITY

    class ChartFields(BaseFieldEnum):
        SYMBOL = 0
        OPEN_PRICE = 1
        HIGH_PRICE = 2
        LOW_PRICE = 3
        CLOSE_PRICE = 4
        VOLUME = 5
        SEQUENCE = 6
        CHART_TIME = 7
        CHART_DAY = 8

    async def __chart_op(self, symbols, service, command):
        # Testing indicates that passed fields are ignored and all fields are
        # always returned
        fields = self.ChartFields.all_fields()
        request, request_id = self.__make_request(
            service=service, command=command,
            parameters={
                'keys': ','.join(symbols),
                'fields': ','.join(str(f) for f in fields)})

        await self.__send({'requests': [request]})
        await self.__await_response(request_id)

    async def chart_equity_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'CHART_EQUITY', 'SUBS', self.ChartFields,
            fields=fields)

    async def chart_equity_add(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'CHART_EQUITY', 'ADD', self.ChartFields,
            fields=fields)

    def add_chart_equity_handler(self, handler):
        self._handlers['CHART_EQUITY'].append(Handler(handler,
                                                      self.ChartFields))

    ##########################################################################
    # CHART_FUTURES

    class ChartFields(BaseFieldEnum):
        SYMBOL = 0
        OPEN_PRICE = 1
        HIGH_PRICE = 2
        LOW_PRICE = 3
        CLOSE_PRICE = 4
        VOLUME = 5
        SEQUENCE = 6
        CHART_TIME = 7
        CHART_DAY = 8

    async def chart_futures_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'CHART_FUTURES', 'SUBS', self.ChartFields,
            fields=fields)

    async def chart_futures_add(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'CHART_FUTURES', 'ADD', self.ChartFields,
            fields=fields)

    def add_chart_futures_handler(self, handler):
        self._handlers['CHART_FUTURES'].append(Handler(handler,
                                                       self.ChartFields))

    ##########################################################################
    # QUOTE

    class LevelOneQuoteFields(BaseFieldEnum):
        SYMBOL = 0
        BID_PRICE = 1
        ASK_PRICE = 2
        LAST_PRICE = 3
        BID_SIZE = 4
        ASK_SIZE = 5
        ASK_ID = 6
        BID_ID = 7
        TOTAL_VOLUME = 8
        LAST_SIZE = 9
        TRADE_TIME = 10
        QUOTE_TIME = 11
        HIGH_PRICE = 12
        LOW_PRICE = 13
        BID_TICK = 14
        CLOSE_PRICE = 15
        EXCHANGE_ID = 16
        MARGINABLE = 17
        SHORTABLE = 18
        ISLAND_BID_DEPRECATED = 19
        ISLAND_ASK_DEPRECATED = 20
        ISLAND_VOLUME_DEPRECATED = 21
        QUOTE_DAY = 22
        TRADE_DAY = 23
        VOLATILITY = 24
        DESCRIPTION = 25
        LAST_ID = 26
        DIGITS = 27
        OPEN_PRICE = 28
        NET_CHANGE = 29
        HIGH_52_WEEK = 30
        LOW_52_WEEK = 31
        PE_RATIO = 32
        DIVIDEND_AMOUNT = 33
        DIVIDEND_YIELD = 34
        NAV = 37
        FUND_PRICE = 38
        EXCHANGE_NAME = 39
        DIVIDEND_DATE = 40
        IS_REGULAR_MARKET_QUOTE = 41
        IS_REGULAR_MARKET_TRADE = 42
        REGULAR_MARKET_LAST_PRICE = 43
        REGULAR_MARKET_LAST_SIZE = 44
        REGULAR_MARKET_TRADE_TIME = 45
        REGULAR_MARKET_TRADE_DAY = 46
        REGULAR_MARKET_NET_CHANGE = 47
        SECURITY_STATUS = 48
        MARK = 49
        QUOTE_TIME_IN_LONG = 50
        TRADE_TIME_IN_LONG = 51
        REGULAR_MARKET_TRADE_TIME_IN_LONG = 52

    async def level_one_quote_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'QUOTE', 'SUBS', self.LevelOneQuoteFields,
            fields=fields)

    def add_level_one_quote_handler(self, handler):
        self._handlers['QUOTE'].append(Handler(handler,
                                               self.LevelOneQuoteFields))

    ##########################################################################
    # OPTION

    class LevelOneOptionFields(BaseFieldEnum):
        SYMBOL = 0
        DESCRIPTION = 1
        BID_PRICE = 2
        ASK_PRICE = 3
        LAST_PRICE = 4
        HIGH_PRICE = 5
        LOW_PRICE = 6
        CLOSE_PRICE = 7
        TOTAL_VOLUME = 8
        OPEN_INTEREST = 9
        VOLATILITY = 10
        QUOTE_TIME = 11
        TRADE_TIME = 12
        MONEY_INTRINSIC_VALUE = 13
        QUOTE_DAY = 14
        TRADE_DAY = 15
        EXPIRATION_YEAR = 16
        MULTIPLIER = 17
        DIGITS = 18
        OPEN_PRICE = 19
        BID_SIZE = 20
        ASK_SIZE = 21
        LAST_SIZE = 22
        NET_CHANGE = 23
        STRIKE_PRICE = 24
        CONTRACT_TYPE = 25
        UNDERLYING = 26
        EXPIRATION_MONTH = 27
        DELIVERABLES = 28
        TIME_VALUE = 29
        EXPIRATION_DAY = 30
        DAYS_TO_EXPIRATION = 31
        DELTA = 32
        GAMMA = 33
        THETA = 34
        VEGA = 35
        RHO = 36
        SECURITY_STATUS = 37
        THEORETICAL_OPTION_VALUE = 38
        UNDERLYING_PRICE = 39
        UV_EXPIRATION_TYPE = 40
        MARK = 41

    async def level_one_option_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'OPTION', 'SUBS', self.LevelOneOptionFields,
            fields=fields)

    def add_level_one_option_handler(self, handler):
        self._handlers['OPTION'].append(Handler(handler,
                                                self.LevelOneOptionFields))

    ##########################################################################
    # LEVELONE_FUTURES

    class LevelOneFuturesFields(BaseFieldEnum):
        SYMBOL = 0
        BID_PRICE = 1
        ASK_PRICE = 2
        LAST_PRICE = 3
        BID_SIZE = 4
        ASK_SIZE = 5
        ASK_ID = 6
        BID_ID = 7
        TOTAL_VOLUME = 8
        LAST_SIZE = 9
        QUOTE_TIME = 10
        TRADE_TIME = 11
        HIGH_PRICE = 12
        LOW_PRICE = 13
        CLOSE_PRICE = 14
        EXCHANGE_ID = 15
        DESCRIPTION = 16
        LAST_ID = 17
        OPEN_PRICE = 18
        NET_CHANGE = 19
        FUTURE_PERCENT_CHANGE = 20
        EXCHANGE_NAME = 21
        SECURITY_STATUS = 22
        OPEN_INTEREST = 23
        MARK = 24
        TICK = 25
        TICK_AMOUNT = 26
        PRODUCT = 27
        FUTURE_PRICE_FORMAT = 28
        FUTURE_TRADING_HOURS = 29
        FUTURE_IS_TRADEABLE = 30
        FUTURE_MULTIPLIER = 31
        FUTURE_IS_ACTIVE = 32
        FUTURE_SETTLEMENT_PRICE = 33
        FUTURE_ACTIVE_SYMBOL = 34
        FUTURE_EXPIRATION_DATE = 35

    async def level_one_futures_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'LEVELONE_FUTURES', 'SUBS', self.LevelOneFuturesFields,
            fields=fields)

    def add_level_one_futures_handler(self, handler):
        self._handlers['LEVELONE_FUTURES'].append(Handler(handler,
                                                          self.LevelOneFuturesFields))

    ##########################################################################
    # LEVELONE_FOREX

    class LevelOneForexFields(BaseFieldEnum):
        SYMBOL = 0
        BID_PRICE = 1
        ASK_PRICE = 2
        LAST_PRICE = 3
        BID_SIZE = 4
        ASK_SIZE = 5
        TOTAL_VOLUME = 6
        LAST_SIZE = 7
        QUOTE_TIME = 8
        TRADE_TIME = 9
        HIGH_PRICE = 10
        LOW_PRICE = 11
        CLOSE_PRICE = 12
        EXCHANGE_ID = 13
        DESCRIPTION = 14
        OPEN_PRICE = 15
        NET_CHANGE = 16
        # Disabled because testing indicates the API returns some unparsable
        # characters
        # PERCENT_CHANGE = 17
        EXCHANGE_NAME = 18
        DIGITS = 19
        SECURITY_STATUS = 20
        TICK = 21
        TICK_AMOUNT = 22
        PRODUCT = 23
        # XXX: Documentation has TRADING_HOURS as 23, but testing suggests it's
        # actually 23. See here for details:
        # https://developer.tdameritrade.com/content/streaming-data#_Toc504640606
        TRADING_HOURS = 24
        IS_TRADABLE = 25
        MARKET_MAKER = 26
        HIGH_52_WEEK = 27
        LOW_52_WEEK = 28
        MARK = 29

    async def level_one_forex_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'LEVELONE_FOREX', 'SUBS', self.LevelOneForexFields,
            fields=fields)

    def add_level_one_forex_handler(self, handler):
        self._handlers['LEVELONE_FOREX'].append(Hander(handler,
                                                       self.LevelOneForexFields))

    ##########################################################################
    # LEVELONE_FUTURES_OPTIONS

    class LevelOneFuturesOptionsFields(BaseFieldEnum):
        SYMBOL = 0
        BID_PRICE = 1
        ASK_PRICE = 2
        LAST_PRICE = 3
        BID_SIZE = 4
        ASK_SIZE = 5
        ASK_ID = 6
        BID_ID = 7
        TOTAL_VOLUME = 8
        LAST_SIZE = 9
        QUOTE_TIME = 10
        TRADE_TIME = 11
        HIGH_PRICE = 12
        LOW_PRICE = 13
        CLOSE_PRICE = 14
        EXCHANGE_ID = 15
        DESCRIPTION = 16
        LAST_ID = 17
        OPEN_PRICE = 18
        NET_CHANGE = 19
        FUTURE_PERCENT_CHANGE = 20
        EXCHANGE_NAME = 21
        SECURITY_STATUS = 22
        OPEN_INTEREST = 23
        MARK = 24
        TICK = 25
        TICK_AMOUNT = 26
        PRODUCT = 27
        FUTURE_PRICE_FORMAT = 28
        FUTURE_TRADING_HOURS = 29
        FUTURE_IS_TRADEABLE = 30
        FUTURE_MULTIPLIER = 31
        FUTURE_IS_ACTIVE = 32
        FUTURE_SETTLEMENT_PRICE = 33
        FUTURE_ACTIVE_SYMBOL = 34
        FUTURE_EXPIRATION_DATE = 35

    async def level_one_futures_options_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'LEVELONE_FUTURES_OPTIONS', 'SUBS',
            self.LevelOneFuturesOptionsFields, fields=fields)

    def add_level_one_futures_options_handler(self, handler):
        self._handlers['LEVELONE_FUTURES_OPTIONS'].append(Handler(handler,
                                                                  self.LevelOneFuturesOptionsFields))

    ##########################################################################
    # TIMESALE

    class TimesaleFields(BaseFieldEnum):
        SYMBOL = 0
        TRADE_TIME = 1
        LAST_PRICE = 2
        LAST_SIZE = 3
        LAST_SEQUENCE = 4

    async def timesale_equity_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'TIMESALE_EQUITY', 'SUBS',
            self.TimesaleFields, fields=fields)

    def add_timesale_equity_handler(self, handler):
        self._handlers['TIMESALE_EQUITY'].append(Handler(handler,
                                                         self.TimesaleFields))

    async def timesale_futures_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'TIMESALE_FUTURES', 'SUBS',
            self.TimesaleFields, fields=fields)

    def add_timesale_futures_handler(self, handler):
        self._handlers['TIMESALE_FUTURES'].append(Handler(handler,
                                                          self.TimesaleFields))

    async def timesale_options_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'TIMESALE_OPTIONS', 'SUBS',
            self.TimesaleFields, fields=fields)

    def add_timesale_options_handler(self, handler):
        self._handlers['TIMESALE_OPTIONS'].append(Handler(handler,
                                                          self.TimesaleFields))

    ##########################################################################
    # FUTURES_BOOK

    class FuturesBookFields(BaseFieldEnum):
        SYMBOL = 0

    async def futures_book_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'FUTURES_BOOK', 'SUBS',
            self.FuturesBookFields, fields=fields)

    def add_futures_book_handler(self, handler):
        self._handlers['FUTURES_BOOK'].append(Handler(handler,
                                                      self.FuturesBookFields))

    ##########################################################################
    # FOREX_BOOK

    class ForexBookFields(BaseFieldEnum):
        SYMBOL = 0

    async def forex_book_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'FOREX_BOOK', 'SUBS',
            self.ForexBookFields, fields=fields)

    def add_forex_book_handler(self, handler):
        self._handlers['FOREX_BOOK'].append(Handler(handler,
                                                    self.ForexBookFields))

    ##########################################################################
    # FUTURES_OPTIONS_BOOK

    class FuturesOptionsBookFields(BaseFieldEnum):
        SYMBOL = 0

    async def futures_options_book_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'FUTURES_OPTIONS_BOOK', 'SUBS',
            self.FuturesOptionsBookFields, fields=fields)

    def add_futures_options_book_handler(self, handler):
        self._handlers['FUTURES_OPTIONS_BOOK'].append(
            Handler(handler, self.FuturesOptionsBookFields))

    ##########################################################################
    # LISTED_BOOK

    class ListedBookFields(BaseFieldEnum):
        SYMBOL = 0

    async def listed_book_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'LISTED_BOOK', 'SUBS',
            self.ListedBookFields, fields=fields)

    def add_listed_book_handler(self, handler):
        self._handlers['LISTED_BOOK'].append(Handler(handler,
                                                     self.ListedBookFields))

    ##########################################################################
    # NASDAQ_BOOK

    class NasdaqBookFields(BaseFieldEnum):
        SYMBOL = 0
        BOOK_TIME = 1
        BIDS = 2
        ASKS = 3

    class BidFields(BaseFieldEnum):
        BID_PRICE = 0
        TOTAL_VOLUME = 1
        NUM_BIDS = 2
        BIDS = 3

    class PerExchangeBidFields(BaseFieldEnum):
        EXCHANGE = 0
        BID_VOLUME = 1
        SEQUENCE = 2

    class AskFields(BaseFieldEnum):
        ASK_PRICE = 0
        TOTAL_VOLUME = 1
        NUM_ASKS = 2
        ASKS = 3

    class PerExchangeAskFields(BaseFieldEnum):
        EXCHANGE = 0
        ASK_VOLUME = 1
        SEQUENCE = 2

    class NasdaqBookHandler(Handler):
        def label_message(self, msg):
            # Relabel top-level fields
            new_msg = super().label_message(msg)

            # Relabel bids
            for content in new_msg['content']:
                if 'BIDS' in content:
                    for bid in content['BIDS']:
                        # Relabel top-level bids
                        StreamClient.BidFields.relabel_message(bid, bid)

                        # Relabel per-exchange bids
                        for e_bid in bid['BIDS']:
                            StreamClient.PerExchangeBidFields.relabel_message(
                                    e_bid, e_bid)

            # Relabel asks
            for content in new_msg['content']:
                if 'ASKS' in content:
                    for ask in content['ASKS']:
                        # Relabel top-level asks
                        StreamClient.AskFields.relabel_message(ask, ask)

                        # Relabel per-exchange bids
                        for e_ask in ask['ASKS']:
                            StreamClient.PerExchangeAskFields.relabel_message(
                                    e_ask, e_ask)

            return new_msg

    async def nasdaq_book_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'NASDAQ_BOOK', 'SUBS',
            self.NasdaqBookFields, fields=fields)

    def add_nasdaq_book_handler(self, handler):
        self._handlers['NASDAQ_BOOK'].append(
                self.NasdaqBookHandler(handler, self.NasdaqBookFields))

    ##########################################################################
    # OPTIONS_BOOK

    class OptionsBookFields(BaseFieldEnum):
        SYMBOL = 0

    async def options_book_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'OPTIONS_BOOK', 'SUBS',
            self.OptionsBookFields, fields=fields)

    def add_options_book_handler(self, handler):
        self._handlers['OPTIONS_BOOK'].append(Handler(handler,
                                                      self.OptionsBookFields))
