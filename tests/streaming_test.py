from tests.test_utils import MockResponse, account_principals
from unittest.mock import ANY, AsyncMock, MagicMock, Mock, patch
from tda.streaming import StreamClient

import aiounittest
import asyncio
import copy
import json
import urllib.parse
import tda

ACCOUNT_ID = 1000
TOKEN_TIMESTAMP = '2020-05-22T02:12:48+0000'


class StreamClientTest(aiounittest.AsyncTestCase):

    def setUp(self):
        self.http_client = MagicMock()
        self.client = StreamClient(self.http_client)

    def account(self, index):
        account = account_principals()['accounts'][0]
        account['accountId'] = str(ACCOUNT_ID + index)

        def parsable_as_int(s):
            try:
                int(s)
                return True
            except ValueError:
                return False
        for key, value in list(account.items()):
            if isinstance(value, str) and not parsable_as_int(value):
                account[key] = value + '-' + str(account['accountId'])
        return account

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_login_single_account_success(self, ws_connect):
        principals = account_principals()
        principals['accounts'].clear()
        principals['accounts'].append(self.account(1))

        self.http_client.get_user_principals.return_value = MockResponse(
            principals, True)
        socket = AsyncMock()
        ws_connect.return_value = socket

        # Use side_effect rather than return_value because otherwise we'll
        # infinite loop looking for the response object
        socket.recv.side_effect = [json.dumps(
            {
                'response': [
                    {
                        'service': 'ADMIN',
                        'requestid': '0',
                        'command': 'LOGIN',
                        'timestamp': 1590116673258,
                        'content': {
                            'code': 0,
                            'msg': '04-1'
                        }
                    }
                ]
            })]

        await self.client.login()

        socket.send.assert_awaited_once()
        request = json.loads(
            socket.send.call_args_list[0].args[0])['requests'][0]
        creds = urllib.parse.parse_qs(request['parameters']['credential'])

        self.assertEqual(creds['userid'], ['1001'])
        self.assertEqual(creds['token'], ['streamerInfo-token'])
        self.assertEqual(creds['company'], ['accounts-company-1001'])
        self.assertEqual(
            creds['cddomain'],
            ['accounts-accountCdDomainId-1001'])
        self.assertEqual(creds['usergroup'], ['streamerInfo-userGroup'])
        self.assertEqual(creds['accesslevel'], ['streamerInfo-accessLevel'])
        self.assertEqual(creds['authorized'], ['Y'])
        self.assertEqual(creds['timestamp'], ['1590113568000'])
        self.assertEqual(creds['appid'], ['streamerInfo-appId'])
        self.assertEqual(creds['acl'], ['streamerInfo-acl'])

        self.assertEqual(request['parameters']['token'], 'streamerInfo-token')
        self.assertEqual(request['parameters']['version'], '1.0')

        self.assertEqual(request['requestid'], '0')
        self.assertEqual(request['service'], 'ADMIN')
        self.assertEqual(request['command'], 'LOGIN')

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_login_multiple_accounts_require_account_id(self, ws_connect):
        # Unfortunately, AsyncTestCase does not offer an async equivalent to
        # unittest.mock.patch
        principals = account_principals()
        principals['accounts'].clear()
        principals['accounts'].append(self.account(1))
        principals['accounts'].append(self.account(2))

        self.http_client.get_user_principals.return_value = MockResponse(
            principals, True)

        with self.assertRaisesRegex(ValueError,
                '.*initialized with unspecified account_id.*'):
            await self.client.login()
        ws_connect.assert_not_called()

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_login_multiple_accounts_with_account_id(self, ws_connect):
        principals = account_principals()
        principals['accounts'].clear()
        principals['accounts'].append(self.account(1))
        principals['accounts'].append(self.account(2))

        self.http_client.get_user_principals.return_value = MockResponse(
            principals, True)
        socket = AsyncMock()
        ws_connect.return_value = socket

        # Use side_effect rather than return_value because otherwise we'll
        # infinite loop looking for the response object
        socket.recv.side_effect = [json.dumps(
            {
                'response': [
                    {
                        'service': 'ADMIN',
                        'requestid': '0',
                        'command': 'LOGIN',
                        'timestamp': 1590116673258,
                        'content': {
                            'code': 0,
                            'msg': '04-1'
                        }
                    }
                ]
            })]

        self.client = StreamClient(self.http_client, account_id=1002)
        await self.client.login()

        socket.send.assert_awaited_once()
        request = json.loads(
            socket.send.call_args_list[0].args[0])['requests'][0]
        creds = urllib.parse.parse_qs(request['parameters']['credential'])

        self.assertEqual(creds['userid'], ['1002'])
        self.assertEqual(creds['token'], ['streamerInfo-token'])
        self.assertEqual(creds['company'], ['accounts-company-1002'])
        self.assertEqual(
            creds['cddomain'],
            ['accounts-accountCdDomainId-1002'])
        self.assertEqual(creds['usergroup'], ['streamerInfo-userGroup'])
        self.assertEqual(creds['accesslevel'], ['streamerInfo-accessLevel'])
        self.assertEqual(creds['authorized'], ['Y'])
        self.assertEqual(creds['timestamp'], ['1590113568000'])
        self.assertEqual(creds['appid'], ['streamerInfo-appId'])
        self.assertEqual(creds['acl'], ['streamerInfo-acl'])

        self.assertEqual(request['parameters']['token'], 'streamerInfo-token')
        self.assertEqual(request['parameters']['version'], '1.0')

        self.assertEqual(request['requestid'], '0')
        self.assertEqual(request['service'], 'ADMIN')
        self.assertEqual(request['command'], 'LOGIN')


    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_login_unrecognized_account_id(self, ws_connect):
        principals = account_principals()
        principals['accounts'].clear()
        principals['accounts'].append(self.account(1))
        principals['accounts'].append(self.account(2))

        self.http_client.get_user_principals.return_value = MockResponse(
            principals, True)

        self.client = StreamClient(self.http_client, account_id=999999)

        with self.assertRaisesRegex(ValueError,
                '.*no account found with account_id 999999.*'):
            await self.client.login()
        ws_connect.assert_not_called()

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_login_bad_response(self, ws_connect):
        principals = account_principals()
        principals['accounts'].clear()
        principals['accounts'].append(self.account(1))

        self.http_client.get_user_principals.return_value = MockResponse(
            principals, True)
        socket = AsyncMock()
        ws_connect.return_value = socket

        # Use side_effect rather than return_value because otherwise we'll
        # infinite loop looking for the response object
        socket.recv.side_effect = [json.dumps(
            {
                'response': [
                    {
                        'service': 'ADMIN',
                        'requestid': '0',
                        'command': 'LOGIN',
                        'timestamp': 1590116673258,
                        'content': {
                            'code': 21,
                            'msg': 'Failed for some reason'
                        }
                    }
                ]
            })]

        with self.assertRaises(tda.streaming.UnexpectedResponseCode):
            await self.client.login()

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_login_unexpected_request_id(self, ws_connect):
        principals = account_principals()
        principals['accounts'].clear()
        principals['accounts'].append(self.account(1))

        self.http_client.get_user_principals.return_value = MockResponse(
            principals, True)
        socket = AsyncMock()
        ws_connect.return_value = socket

        # Use side_effect rather than return_value because otherwise we'll
        # infinite loop looking for the response object
        socket.recv.side_effect = [json.dumps(
            {
                'response': [
                    {
                        'service': 'ADMIN',
                        'requestid': '9999',
                        'command': 'LOGIN',
                        'timestamp': 1590116673258,
                        'content': {
                            'code': 0,
                            'msg': '04-1'
                        }
                    }
                ]
            })]

        with self.assertRaisesRegex(tda.streaming.UnexpectedResponse,
                'unexpected requestid: 9999'):
            await self.client.login()
