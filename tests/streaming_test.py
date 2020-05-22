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

    def request_from_socket_mock(self, socket):
        return json.loads(
            socket.send.call_args_list[0].args[0])['requests'][0]

    def success_response(self, request_id, service, command):
        return {
            'response': [
                {
                    'service': service,
                    'requestid': str(request_id),
                    'command': command,
                    'timestamp': 1590116673258,
                    'content': {
                        'code': 0,
                        'msg': 'success'
                    }
                }
            ]
        }

    def streaming_entry(self, service, command):
        return {
                'data': [{
                    'service': service,
                    'command': command,
                    'timestamp': 1590186642440
                    }]
            }

    async def login_and_get_socket(self, ws_connect):
        principals = account_principals()

        self.http_client.get_user_principals.return_value = MockResponse(
            principals, True)
        socket = AsyncMock()
        ws_connect.return_value = socket

        socket.recv.side_effect = [json.dumps(self.success_response(
            0, 'ADMIN', 'LOGIN'))]

        await self.client.login()

        socket.reset_mock()
        return socket

    ##########################################################################
    # Login

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_login_single_account_success(self, ws_connect):
        principals = account_principals()
        principals['accounts'].clear()
        principals['accounts'].append(self.account(1))

        self.http_client.get_user_principals.return_value = MockResponse(
            principals, True)
        socket = AsyncMock()
        ws_connect.return_value = socket

        socket.recv.side_effect = [json.dumps(self.success_response(
            0, 'ADMIN', 'LOGIN'))]

        await self.client.login()

        socket.send.assert_awaited_once()
        request = self.request_from_socket_mock(socket)
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

        socket.recv.side_effect = [json.dumps(self.success_response(
            0, 'ADMIN', 'LOGIN'))]

        self.client = StreamClient(self.http_client, account_id=1002)
        await self.client.login()

        socket.send.assert_awaited_once()
        request = self.request_from_socket_mock(socket)
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

        response = self.success_response(0, 'ADMIN', 'LOGIN')
        response['response'][0]['content']['code'] = 21
        response['response'][0]['content']['msg'] = 'failed for some reason'
        socket.recv.side_effect = [json.dumps(response)]

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

        response = self.success_response(0, 'ADMIN', 'LOGIN')
        response['response'][0]['requestid'] = 9999
        socket.recv.side_effect = [json.dumps(response)]

        with self.assertRaisesRegex(tda.streaming.UnexpectedResponse,
                                    'unexpected requestid: 9999'):
            await self.client.login()

    ##########################################################################
    # QOS

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_qos_success(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        socket.recv.side_effect = [json.dumps(self.success_response(
            1, 'ADMIN', 'QOS'))]

        await self.client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        socket.recv.assert_awaited_once()
        request = self.request_from_socket_mock(socket)

        self.assertEqual(request, {
            'account': '1001',
            'service': 'ADMIN',
            'command': 'QOS',
            'requestid': '1',
            'source': 'streamerInfo-appId',
            'parameters': {
                'qoslevel': '0'
            }
        })

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_qos_failure(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        response = self.success_response(1, 'ADMIN', 'QOS')
        response['response'][0]['content']['code'] = 21
        socket.recv.side_effect = [json.dumps(response)]

        with self.assertRaises(tda.streaming.UnexpectedResponseCode):
            await self.client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        socket.recv.assert_awaited_once()

    ############################################################################
    # CHART_EQUITY

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_equity_subs_and_add_success(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        socket.recv.side_effect = [json.dumps(self.success_response(
            1, 'CHART_EQUITY', 'SUBS'))]

        await self.client.chart_equity_subs(['GOOG,MSFT'])
        socket.recv.assert_awaited_once()
        request = self.request_from_socket_mock(socket)

        self.assertEqual(request, {
            'account': '1001',
            'service': 'CHART_EQUITY',
            'command': 'SUBS',
            'requestid': '1',
            'source': 'streamerInfo-appId',
            'parameters': {
                'keys': 'GOOG,MSFT',
                'fields': '0,1,2,3,4,5,6,7,8'
            }
        })

        socket.reset_mock()

        socket.recv.side_effect = [json.dumps(self.success_response(
            2, 'CHART_EQUITY', 'ADD'))]

        await self.client.chart_equity_add(['INTC'])
        socket.recv.assert_awaited_once()
        request = self.request_from_socket_mock(socket)

        self.assertEqual(request, {
            'account': '1001',
            'service': 'CHART_EQUITY',
            'command': 'ADD',
            'requestid': '2',
            'source': 'streamerInfo-appId',
            'parameters': {
                'keys': 'INTC',
                'fields': '0,1,2,3,4,5,6,7,8'
            }
        })

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_equity_subs_failure(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        response = self.success_response(1, 'CHART_EQUITY', 'SUBS')
        response['response'][0]['content']['code'] = 21
        socket.recv.side_effect = [json.dumps(response)]

        with self.assertRaises(tda.streaming.UnexpectedResponseCode):
            await self.client.chart_equity_subs(['GOOG,MSFT'])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_equity_add_failure(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        response_subs = self.success_response(1, 'CHART_EQUITY', 'SUBS')

        response_add = self.success_response(2, 'CHART_EQUITY', 'ADD')
        response_add['response'][0]['content']['code'] = 21
        socket.recv.side_effect = [
                json.dumps(response_subs),
                json.dumps(response_add)]

        await self.client.chart_equity_subs(['GOOG,MSFT'])

        with self.assertRaises(tda.streaming.UnexpectedResponseCode):
            await self.client.chart_equity_add(['INTC'])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_equity_handler(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        stream_item = self.streaming_entry('CHART_EQUITY', 'SUBS')
        stream_item['data'][0]['content'] = [{'fake': 'data'}]

        socket.recv.side_effect = [
                json.dumps(self.success_response(1, 'CHART_EQUITY', 'SUBS')),
                json.dumps(stream_item)]
        await self.client.chart_equity_subs(['GOOG,MSFT'])

        handler = Mock()
        self.client.add_chart_equity_handler(handler)
        await self.client.handle_message()

        handler.assert_called_once_with(stream_item['data'][0])
