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
        self.account = None
        self.socket = None
        self.source = None


    async def send(self, obj):
        await self.socket.send(json.dumps(obj))


    async def receive(self):
        return json.loads(await self.socket.recv())


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
                self.account = account

        if self.account is None:
            raise ValueError(
                    'no account found with account_id {}'.format(
                        self.account_id))

        if self.account_id is None:
            self.account_id = self.account['accountId']


        # Initialize socket
        wss_url = 'wss://{}/ws'.format(
                principals['streamerInfo']['streamerSocketUrl'])
        self.socket = await websockets.client.connect(wss_url)

        # Initialize miscellaneous parameters
        self.source = principals['streamerInfo']['appId']


    def __make_request(self, *, service, command, parameters):
        return {
            "service": "ADMIN",
            "requestid": "0",
            "command": "LOGIN",
            "account": self.account_id,
            "source": self.source,
            "parameters": parameters
        }


    async def login(self):
        r = self.client.get_user_principals(fields=[
            self.client.UserPrincipals.Fields.PREFERENCES,
            self.client.UserPrincipals.Fields.STREAMER_CONNECTION_INFO,
            self.client.UserPrincipals.Fields.STREAMER_SUBSCRIPTION_KEYS,
            self.client.UserPrincipals.Fields.SURROGATE_IDS])
        assert r.ok
        r = r.json()

        await self.__init_from_principals(r)

        token_ts = datetime.datetime.strptime(
                r['streamerInfo']['tokenTimestamp'], "%Y-%m-%dT%H:%M:%S%z")
        token_ts = int(token_ts.timestamp()) * 1000

        credentials = {
            "userid": self.account_id,
            "token": r['streamerInfo']['token'],
            "company": self.account['company'],
            "segment": self.account['segment'],
            "cddomain": self.account['accountCdDomainId'],
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

        request = {
            "requests": [
                self.__make_request(service='ADMIN', command='LOGIN', 
                    parameters=request_parameters)
            ]
        }

        print(json.dumps(request, indent=4))
        await self.send(request)
        resp = await self.receive()
        print(json.dumps(resp, indent=4))

