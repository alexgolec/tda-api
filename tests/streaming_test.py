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

    ##########################################################################
    # CHART_EQUITY

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_equity_subs_and_add_success(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        socket.recv.side_effect = [json.dumps(self.success_response(
            1, 'CHART_EQUITY', 'SUBS'))]

        await self.client.chart_equity_subs(['GOOG', 'MSFT'])
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
            await self.client.chart_equity_subs(['GOOG', 'MSFT'])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_equity_add_failure(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        response_subs = self.success_response(1, 'CHART_EQUITY', 'SUBS')

        response_add = self.success_response(2, 'CHART_EQUITY', 'ADD')
        response_add['response'][0]['content']['code'] = 21
        socket.recv.side_effect = [
            json.dumps(response_subs),
            json.dumps(response_add)]

        await self.client.chart_equity_subs(['GOOG', 'MSFT'])

        with self.assertRaises(tda.streaming.UnexpectedResponseCode):
            await self.client.chart_equity_add(['INTC'])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_equity_handler(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        stream_item = {
            'data': [
                {
                    'service': 'CHART_EQUITY',
                    'command': 'SUBS',
                    'timestamp': 1590186642440,
                    'content': [
                        {
                            'key': 'MSFT',
                            '1': 200,
                            '2': 300,
                            '3': 100,
                            '4': 200,
                            '5': 123456789,
                            '6': 901,
                            '7': 1590187260000,
                            '8': 18404,
                        },
                        {
                            'key': 'GOOG',
                            '1': 2000,
                            '2': 3000,
                            '3': 1000,
                            '4': 2000,
                            '5': 1234567890,
                            '6': 9010,
                            '7': 1590187260000,
                            '8': 18404,
                        }
                    ]
                }
            ]
        }

        socket.recv.side_effect = [
            json.dumps(self.success_response(1, 'CHART_EQUITY', 'SUBS')),
            json.dumps(stream_item)]
        await self.client.chart_equity_subs(['GOOG', 'MSFT'])

        handler = Mock()
        self.client.add_chart_equity_handler(handler)
        await self.client.handle_message()

        expected_item = {
            'service': 'CHART_EQUITY',
            'command': 'SUBS',
            'timestamp': 1590186642440,
            'content': [
                        {
                            'key': 'MSFT',
                            'OPEN_PRICE': 200,
                            'HIGH_PRICE': 300,
                            'LOW_PRICE': 100,
                            'CLOSE_PRICE': 200,
                            'VOLUME': 123456789,
                            'SEQUENCE': 901,
                            'CHART_TIME': 1590187260000,
                            'CHART_DAY': 18404,
                        },
                {
                            'key': 'GOOG',
                            'OPEN_PRICE': 2000,
                            'HIGH_PRICE': 3000,
                            'LOW_PRICE': 1000,
                            'CLOSE_PRICE': 2000,
                            'VOLUME': 1234567890,
                            'SEQUENCE': 9010,
                            'CHART_TIME': 1590187260000,
                            'CHART_DAY': 18404,
                        }
            ]
        }

        handler.assert_called_once_with(expected_item)

    ##########################################################################
    # CHART_FUTURES

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_futures_subs_and_add_success(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        socket.recv.side_effect = [json.dumps(self.success_response(
            1, 'CHART_FUTURES', 'SUBS'))]

        await self.client.chart_futures_subs(['/ES', '/CL'])
        socket.recv.assert_awaited_once()
        request = self.request_from_socket_mock(socket)

        self.assertEqual(request, {
            'account': '1001',
            'service': 'CHART_FUTURES',
            'command': 'SUBS',
            'requestid': '1',
            'source': 'streamerInfo-appId',
            'parameters': {
                'keys': '/ES,/CL',
                'fields': '0,1,2,3,4,5,6,7,8'
            }
        })

        socket.reset_mock()

        socket.recv.side_effect = [json.dumps(self.success_response(
            2, 'CHART_FUTURES', 'ADD'))]

        await self.client.chart_futures_add(['/ZC'])
        socket.recv.assert_awaited_once()
        request = self.request_from_socket_mock(socket)

        self.assertEqual(request, {
            'account': '1001',
            'service': 'CHART_FUTURES',
            'command': 'ADD',
            'requestid': '2',
            'source': 'streamerInfo-appId',
            'parameters': {
                'keys': '/ZC',
                'fields': '0,1,2,3,4,5,6,7,8'
            }
        })

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_futures_subs_failure(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        response = self.success_response(1, 'CHART_FUTURES', 'SUBS')
        response['response'][0]['content']['code'] = 21
        socket.recv.side_effect = [json.dumps(response)]

        with self.assertRaises(tda.streaming.UnexpectedResponseCode):
            await self.client.chart_futures_subs(['/ES', '/CL'])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_futures_add_failure(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        response_subs = self.success_response(1, 'CHART_FUTURES', 'SUBS')

        response_add = self.success_response(2, 'CHART_FUTURES', 'ADD')
        response_add['response'][0]['content']['code'] = 21
        socket.recv.side_effect = [
            json.dumps(response_subs),
            json.dumps(response_add)]

        await self.client.chart_futures_subs(['/ES', '/CL'])

        with self.assertRaises(tda.streaming.UnexpectedResponseCode):
            await self.client.chart_futures_add(['/ZC'])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_chart_futures_handler(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        stream_item = {
            'data': [
                {
                    'service': 'CHART_FUTURES',
                    'command': 'SUBS',
                    'timestamp': 1590186642440,
                    'content': [
                        {
                            'key': '/ES',
                            '1': 200,
                            '2': 300,
                            '3': 100,
                            '4': 200,
                            '5': 123456789,
                            '6': 901,
                            '7': 1590187260000,
                            '8': 18404,
                        },
                        {
                            'key': '/CL',
                            '1': 2000,
                            '2': 3000,
                            '3': 1000,
                            '4': 2000,
                            '5': 1234567890,
                            '6': 9010,
                            '7': 1590187260000,
                            '8': 18404,
                        }
                    ]
                }
            ]
        }

        socket.recv.side_effect = [
            json.dumps(self.success_response(1, 'CHART_FUTURES', 'SUBS')),
            json.dumps(stream_item)]
        await self.client.chart_futures_subs(['/ES', '/CL'])

        handler = Mock()
        self.client.add_chart_futures_handler(handler)
        await self.client.handle_message()

        expected_item = {
            'service': 'CHART_FUTURES',
            'command': 'SUBS',
            'timestamp': 1590186642440,
            'content': [
                        {
                            'key': '/ES',
                            'OPEN_PRICE': 200,
                            'HIGH_PRICE': 300,
                            'LOW_PRICE': 100,
                            'CLOSE_PRICE': 200,
                            'VOLUME': 123456789,
                            'SEQUENCE': 901,
                            'CHART_TIME': 1590187260000,
                            'CHART_DAY': 18404,
                        },
                {
                            'key': '/CL',
                            'OPEN_PRICE': 2000,
                            'HIGH_PRICE': 3000,
                            'LOW_PRICE': 1000,
                            'CLOSE_PRICE': 2000,
                            'VOLUME': 1234567890,
                            'SEQUENCE': 9010,
                            'CHART_TIME': 1590187260000,
                            'CHART_DAY': 18404,
                        }
            ]
        }

        handler.assert_called_once_with(expected_item)

    ###########################################################################
    # Handler edge cases
    #
    # Note: We use CHART_EQUITY as a test case, which leaks the implementation
    # detail that the handler dispatching is implemented by a common component.
    # If this were to ever change, these tests will have to be revisited.

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_messages_received_while_awaiting_response(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        stream_item = self.streaming_entry('CHART_EQUITY', 'SUBS')

        socket.recv.side_effect = [
            json.dumps(self.success_response(1, 'CHART_EQUITY', 'SUBS')),
            json.dumps(stream_item),
            json.dumps(self.success_response(2, 'CHART_EQUITY', 'ADD'))]

        await self.client.chart_equity_subs(['GOOG,MSFT'])
        await self.client.chart_equity_add(['INTC'])

        handler = Mock()
        self.client.add_chart_equity_handler(handler)
        await self.client.handle_message()
        handler.assert_called_once_with(stream_item['data'][0])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_messages_received_while_awaiting_failed_response_bad_code(
            self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        stream_item = self.streaming_entry('CHART_EQUITY', 'SUBS')

        failed_add_response = self.success_response(2, 'CHART_EQUITY', 'ADD')
        failed_add_response['response'][0]['content']['code'] = 21

        socket.recv.side_effect = [
            json.dumps(self.success_response(1, 'CHART_EQUITY', 'SUBS')),
            json.dumps(stream_item),
            json.dumps(failed_add_response)]

        await self.client.chart_equity_subs(['GOOG,MSFT'])
        with self.assertRaises(tda.streaming.UnexpectedResponseCode):
            await self.client.chart_equity_add(['INTC'])

        handler = Mock()
        self.client.add_chart_equity_handler(handler)
        await self.client.handle_message()
        handler.assert_called_once_with(stream_item['data'][0])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_messages_received_while_receiving_unexpected_response(
            self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        stream_item = self.streaming_entry('CHART_EQUITY', 'SUBS')

        failed_add_response = self.success_response(999, 'CHART_EQUITY', 'ADD')
        failed_add_response['response'][0]['content']['code'] = 21

        socket.recv.side_effect = [
            json.dumps(self.success_response(1, 'CHART_EQUITY', 'SUBS')),
            json.dumps(stream_item),
            json.dumps(failed_add_response)]

        await self.client.chart_equity_subs(['GOOG,MSFT'])
        with self.assertRaises(tda.streaming.UnexpectedResponse):
            await self.client.chart_equity_add(['INTC'])

        handler = Mock()
        self.client.add_chart_equity_handler(handler)
        await self.client.handle_message()
        handler.assert_called_once_with(stream_item['data'][0])

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_notify_messages_ignored(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        stream_item = self.streaming_entry('CHART_EQUITY', 'SUBS')

        socket.recv.side_effect = [
            json.dumps(self.success_response(1, 'CHART_EQUITY', 'SUBS')),
            json.dumps({'notify': {'doesnt': 'matter'}})]

        await self.client.chart_equity_subs(['GOOG,MSFT'])

        handler = Mock()
        self.client.add_chart_equity_handler(handler)
        await self.client.handle_message()
        handler.assert_not_called()

    @patch('tda.streaming.websockets.client.connect', autospec=AsyncMock())
    async def test_handle_message_unexpected_response(self, ws_connect):
        socket = await self.login_and_get_socket(ws_connect)

        stream_item = self.streaming_entry('CHART_EQUITY', 'SUBS')

        socket.recv.side_effect = [
            json.dumps(self.success_response(1, 'CHART_EQUITY', 'SUBS')),
            json.dumps(self.success_response(2, 'CHART_EQUITY', 'SUBS'))]

        await self.client.chart_equity_subs(['GOOG,MSFT'])

        with self.assertRaises(tda.streaming.UnexpectedResponse):
            await self.client.handle_message()
