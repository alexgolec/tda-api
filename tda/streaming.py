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
        return json.loads(await self._socket.recv())

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

            print(json.dumps(resp, indent=4))

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

    ##########################################################################
    # Login

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
        await self.__chart_op(symbols, 'CHART_EQUITY', 'SUBS', 
                fields=fields)

    async def chart_equity_add(self, symbols, *, fields=None):
        await self.__chart_op(symbols, 'CHART_EQUITY', 'ADD', 
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
        await self.__chart_op(symbols, 'CHART_FUTURES', 'SUBS', 
                fields=fields)

    async def chart_futures_add(self, symbols, *, fields=None):
        await self.__chart_op(symbols, 'CHART_FUTURES', 'ADD', 
                fields=fields)

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
