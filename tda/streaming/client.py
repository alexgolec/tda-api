from collections import deque
from enum import Enum

import asyncio
import copy
import datetime
import inspect
import json
import tda
import urllib.parse
import warnings
import websockets

from .exceptions import *
from . import services
from ..utils import deprecated, get_logger, EnumEnforcer



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


