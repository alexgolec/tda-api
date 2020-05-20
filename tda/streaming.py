from enum import Enum

import asyncio
import datetime
import json
import urllib.parse
import websockets

from .utils import EnumEnforcer


class BaseFieldEnum(Enum):
    @classmethod
    def all_fields(cls):
        return list(cls.__members__.values())


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
        self._handlers = {}

    async def send(self, obj):
        await self._socket.send(json.dumps(obj))

    async def receive(self):
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

    async def await_response(self, request_id):
        while True:
            resp = await self.receive()

            if 'response' not in resp:
                continue

            # Validate response
            resp_request_id = int(resp['response'][0]['requestid'])
            assert resp_request_id == request_id, \
                'unexpected requestid: {}'.format(resp_request_id)

            resp_code = resp['response'][0]['content']['code']
            assert resp_code == 0, 'unexpected response code: {}'.format(
                resp_code)

            return

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

        await self.send({'requests': [request]})
        await self.await_response(request_id)

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

        await self.send({'requests': [request]})
        await self.await_response(request_id)

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

        await self.send({'requests': [request]})
        await self.await_response(request_id)

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

    async def __chart_op(self, symbols, service, command, *, fields=None):
        if fields is None:
            fields = self.ChartFields.all_fields()
        fields = sorted(self.convert_enum_iterable(fields,
                                                   self.ChartFields))

        request, request_id = self.__make_request(
            service=service, command=command,
            parameters={
                'keys': ','.join(symbols),
                'fields': ','.join(str(f) for f in fields)})

        await self.send({'requests': [request]})
        await self.await_response(request_id)

    async def chart_equity_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'CHART_EQUITY', 'SUBS', self.ChartFields,
            fields=fields)

    async def chart_equity_add(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'CHART_EQUITY', 'ADD', self.ChartFields,
            fields=fields)

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
        #PERCENT_CHANGE = 17
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

    async def timesale_futures_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'TIMESALE_FUTURES', 'SUBS',
            self.TimesaleFields, fields=fields)

    async def timesale_options_subs(self, symbols, *, fields=None):
        await self.__service_op(
            symbols, 'TIMESALE_OPTIONS', 'SUBS',
            self.TimesaleFields, fields=fields)


def make_data_container(class_name, fields):
    if len({type(f) for f in fields}) != 1:
        raise ValueError('logic error: multiple types in fields')

    class BaseDataContainer:
        def __init__(self, content):
            self._content = content

    attrs = {}

    # add getters
    for field in fields:
        attrs[field.name.lower()] = \
            lambda self: self._content[str(field.value)]

    # wire up properties
    attrs.update((name, property(fget=attr))
                 for name, attr in attrs.items())

    # add __getattr__ that recommends what entries to initialize with
    def custom_getattr(self, name):
        fields_type = type(fields[0])

        try:
            desired_name = str(fields_type.__members__[name.upper()])
            raise AttributeError(
                ('\'{}\' object has no attribute \'{}\', ' +
                 'initialize with {} to receive it').format(
                    class_name, name, desired_name))
        except KeyError:
            raise AttributeError(
                ('unrecognized field \'{}\', no corresponding field ' +
                 'value in {}').format(name, fields_type))
    attrs['__getattr__'] = custom_getattr

    return type(class_name, (BaseDataContainer,), attrs)
