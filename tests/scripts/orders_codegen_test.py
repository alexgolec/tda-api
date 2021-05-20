import unittest
from unittest.mock import call, MagicMock, patch

from ..utils import AnyStringWith, no_duplicates
from tda.scripts.orders_codegen import latest_order_main

class LatestOrderTest(unittest.TestCase):

    def setUp(self):
        self.args = []

    def add_arg(self, arg):
        self.args.append(arg)

    def main(self):
        return latest_order_main(self.args)

    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_success_no_account_id(
            self,
            mock_code_for_builder,
            mock_construct_repeat_order,
            mock_client_from_token_file,
            mock_print):
        self.add_arg('--token_file')
        self.add_arg('filename.json')
        self.add_arg('--api_key')
        self.add_arg('api-key')

        orders = [
                {'orderId': 201},
                {'orderId': 101},
                {'orderId': 301},
                {'orderId': 401},
        ]

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_orders_by_query.return_value.json.return_value = orders

        self.assertEqual(self.main(), 0)

        mock_construct_repeat_order.assert_called_once_with(orders[3])
        mock_print.assert_has_calls([
                call('# Order ID', 401),
                call(mock_code_for_builder.return_value)])


    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_no_account_id_no_such_order(
            self,
            mock_code_for_builder,
            mock_construct_repeat_order,
            mock_client_from_token_file,
            mock_print):
        self.add_arg('--token_file')
        self.add_arg('filename.json')
        self.add_arg('--api_key')
        self.add_arg('api-key')

        orders = []

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_orders_by_query.return_value.json.return_value = orders

        self.assertEqual(self.main(), 0)

        mock_construct_repeat_order.assert_not_called()
        mock_print.assert_called_once_with('No recent orders found')


    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_no_account_error(
            self,
            mock_code_for_builder,
            mock_construct_repeat_order,
            mock_client_from_token_file,
            mock_print):
        self.add_arg('--token_file')
        self.add_arg('filename.json')
        self.add_arg('--api_key')
        self.add_arg('api-key')

        orders = {'error': 'invalid'}

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_orders_by_query.return_value.json.return_value = orders

        self.assertEqual(self.main(), -1)

        mock_construct_repeat_order.assert_not_called()
        mock_print.assert_called_once_with(
                AnyStringWith('TDA returned error: "invalid"'))


    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_success_account_id(
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
        self.add_arg('123456')

        orders = [
                {'orderId': 201},
                {'orderId': 101},
                {'orderId': 301},
                {'orderId': 401},
        ]

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_orders_by_path.return_value.json.return_value = orders

        self.assertEqual(self.main(), 0)

        mock_construct_repeat_order.assert_called_once_with(orders[3])
        mock_print.assert_has_calls([
                call('# Order ID', 401),
                call(mock_code_for_builder.return_value)])


    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_account_id_no_orders(
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
        self.add_arg('123456')

        orders = []

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_orders_by_path.return_value.json.return_value = orders

        self.assertEqual(self.main(), 0)

        mock_construct_repeat_order.assert_not_called
        mock_print.assert_called_once_with('No recent orders found')


    @no_duplicates
    @patch('builtins.print')
    @patch('tda.scripts.orders_codegen.client_from_token_file')
    @patch('tda.scripts.orders_codegen.construct_repeat_order')
    @patch('tda.scripts.orders_codegen.code_for_builder')
    def test_account_id_error(
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
        self.add_arg('123456')

        orders = {'error': 'invalid'}

        mock_client = MagicMock()
        mock_client_from_token_file.return_value = mock_client
        mock_client.get_orders_by_path.return_value.json.return_value = orders

        self.assertEqual(self.main(), -1)

        mock_construct_repeat_order.assert_not_called
        mock_print.assert_called_once_with(
                AnyStringWith('TDA returned error: "invalid"'))
