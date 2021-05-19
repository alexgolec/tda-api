import unittest
from unittest.mock import call, MagicMock, patch

from ..utils import AnyStringWith, no_duplicates
from tda.scripts.orders_codegen import main, pprint

class OrdersCodeGenTest(unittest.TestCase):

    def setUp(self):
        self.args = []

    def add_arg(self, arg):
        self.args.append(arg)

    def main(self):
        return main(self.args)

    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_success_order_and_account(
            self,
            mock_code_for_builder,
            mock_construct_repeat_order,
            mock_client_from_token_file,
            mock_print):
        self.add_arg('--token_file')
        self.add_arg('filename.json')
        self.add_arg('--api_key')
        self.add_arg('api-key')
        self.add_arg('--account_id')
        self.add_arg('100')
        self.add_arg('--order_id')
        self.add_arg('101')

        order = {
                'order': True,
                'orderId': 101,
        }

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_order.return_value.json.return_value = order

        self.assertEqual(self.main(), 0)

        mock_client.get_order.assert_called_once_with(101, 100)

        mock_construct_repeat_order.assert_called_once_with(order)
        mock_print.assert_has_calls([
                call('# Order ID', 101),
                call(mock_code_for_builder.return_value)])

        mock_client.get_accounts.assert_not_called()
        #mock_client.get_order.assert_not_called()
        mock_client.get_orders_by_query.assert_not_called()
        mock_client.get_orders_by_path.assert_not_called()

    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_success_order_and_no_account(
            self,
            mock_code_for_builder,
            mock_construct_repeat_order,
            mock_client_from_token_file,
            mock_print):
        self.add_arg('--token_file')
        self.add_arg('filename.json')
        self.add_arg('--api_key')
        self.add_arg('api-key')
        self.add_arg('--order_id')
        self.add_arg('101')

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client

        mock_client.get_accounts.return_value.json.return_value = [{
            'securitiesAccount': {'accountId': 200}
        }, {
            'securitiesAccount': {'accountId': 100}
        }]

        mock_client.get_order.return_value.json.side_effect = [
                {'error': True},
                {'order': True, 'orderId': 101}
        ]

        self.assertEqual(self.main(), 0)

        mock_client.get_accounts.assert_called_once()
        mock_client.get_order.assert_has_calls(
                [call(101, 200), call(101, 100)],
                any_order=True)

        mock_construct_repeat_order.assert_called_once_with(
                {'order': True, 'orderId': 101})
        mock_print.assert_has_calls([
            call('# Order ID', 101),
            call(mock_code_for_builder.return_value)])

        #mock_client.get_accounts.assert_not_called()
        #mock_client.get_order.assert_not_called()
        #mock_client.get_orders_by_query.assert_not_called()
        mock_client.get_orders_by_path.assert_not_called()


    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_order_and_no_account_no_such_order(
            self,
            mock_code_for_builder,
            mock_construct_repeat_order,
            mock_client_from_token_file,
            mock_print):
        self.add_arg('--token_file')
        self.add_arg('filename.json')
        self.add_arg('--api_key')
        self.add_arg('api-key')
        self.add_arg('--order_id')
        self.add_arg('101')

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client

        mock_client.get_accounts.return_value.json.return_value = [{
            'securitiesAccount': {'accountId': 200}
        }, {
            'securitiesAccount': {'accountId': 100}
        }]

        mock_client.get_order.return_value.json.side_effect = [
                {'error': True},
                {'error': True}
        ]

        self.assertEqual(self.main(), -1)

        mock_client.get_accounts.assert_called_once()
        mock_client.get_orders_by_query.assert_not_called()
        mock_client.get_order.assert_has_calls(
                [call(101, 200), call(101, 100)],
                any_order=True)
        mock_print.assert_called_once_with(
                'Failed to find order for order_id', 101)

        #mock_client.get_accounts.assert_not_called()
        #mock_client.get_order.assert_not_called()
        #mock_client.get_orders_by_query.assert_not_called()
        mock_client.get_orders_by_path.assert_not_called()


    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_success_no_order_id_no_account_id(
            self,
            mock_code_for_builder,
            mock_construct_repeat_order,
            mock_client_from_token_file,
            mock_print):
        self.add_arg('--token_file')
        self.add_arg('filename.json')
        self.add_arg('--api_key')
        self.add_arg('api-key')

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_orders_by_query.return_value.json.return_value = [
            {'order': 200, 'orderId': 200},
            {'order': 100, 'orderId': 100},
            {'order': 300, 'orderId': 300},
        ]

        mock_construct_repeat_order.side_effect = [
            {'repeat': 100},
            {'repeat': 200},
            {'repeat': 300},
        ]
        mock_code_for_builder.side_effect = [
                'order_100', 'order_200', 'order_300']

        self.assertEqual(self.main(), 0)

        mock_client.get_orders_by_query.assert_called_once()
        mock_construct_repeat_order.assert_has_calls([
            call({'order': 100, 'orderId': 100}),
            call({'order': 200, 'orderId': 200}),
            call({'order': 300, 'orderId': 300}),
        ])
        mock_code_for_builder.assert_has_calls([
            call({'repeat': 100}),
            call({'repeat': 200}),
            call({'repeat': 300}),
        ])

        mock_print.assert_has_calls([
            call('# Order ID', 100),
            call('order_100'),
            call('# Order ID', 200),
            call('order_200'),
            call('# Order ID', 300),
            call('order_300'),
        ])

        mock_client.get_accounts.assert_not_called()
        mock_client.get_order.assert_not_called()
        #mock_client.get_orders_by_query.assert_not_called()
        mock_client.get_orders_by_path.assert_not_called()



    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_success_no_order_id_account_id(
            self,
            mock_code_for_builder,
            mock_construct_repeat_order,
            mock_client_from_token_file,
            mock_print):
        self.add_arg('--token_file')
        self.add_arg('filename.json')
        self.add_arg('--api_key')
        self.add_arg('api-key')
        self.add_arg('--account_id')
        self.add_arg('100')

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_orders_by_path.return_value.json.return_value = [
                {'order': 200, 'orderId': 200},
                {'order': 100, 'orderId': 100},
                {'order': 300, 'orderId': 300},
        ]

        mock_construct_repeat_order.side_effect = [
                {'repeat': 100},
                {'repeat': 200},
                {'repeat': 300},
        ]
        mock_code_for_builder.side_effect = [
                'order_100', 'order_200', 'order_300']

        self.assertEqual(self.main(), 0)

        mock_client.get_orders_by_path.assert_called_once()
        mock_construct_repeat_order.assert_has_calls([
            call({'order': 100, 'orderId': 100}),
            call({'order': 200, 'orderId': 200}),
            call({'order': 300, 'orderId': 300}),
        ])
        mock_code_for_builder.assert_has_calls([
            call({'repeat': 100}),
            call({'repeat': 200}),
            call({'repeat': 300}),
        ])

        mock_print.assert_has_calls([
            call('# Order ID', 100),
            call('order_100'),
            call('# Order ID', 200),
            call('order_200'),
            call('# Order ID', 300),
            call('order_300'),
        ])

        mock_client.get_accounts.assert_not_called()
        mock_client.get_order.assert_not_called()
        mock_client.get_orders_by_query.assert_not_called()
        #mock_client.get_orders_by_path.assert_not_called()
