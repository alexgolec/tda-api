import asyncio
import datetime
import json
import urllib.parse
import websockets


class StreamClient:

    def __init__(self, client, *, account_id=None):
        self.client = client

        # If None, will be set by the login() function
        self.account_id = account_id

        # Set by the login() function
        self._account = None
        self._socket = None
        self._source = None

        # Internal fields
        self._request_id = 0


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


    async def login(self):
        # Fetch required data and initialize the client

        # TODO: Figure out which of these are actually needed
        r = self.client.get_user_principals(fields=[
            self.client.UserPrincipals.Fields.PREFERENCES,
            self.client.UserPrincipals.Fields.STREAMER_CONNECTION_INFO,
            self.client.UserPrincipals.Fields.STREAMER_SUBSCRIPTION_KEYS,
            self.client.UserPrincipals.Fields.SURROGATE_IDS])
        assert r.ok
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
        resp = await self.receive()

        # Validate response
        resp_request_id = int(resp['response'][0]['requestid'])
        assert resp_request_id == request_id, \
                'unexpected requestid: {}'.format(resp_request_id)
        
        resp_code = resp['response'][0]['content']['code']
        assert resp_code == 0, 'unexpected response code: {}'.format(resp_code)
