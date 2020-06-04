from unittest.mock import MagicMock

import datetime
import json
import unittest

from tda.orders import EquityOrderBuilder
from tda.utils import Utils
from . import test_utils
from .test_utils import no_duplicates, MockResponse


class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.account_id = 10000
        self.utils = Utils(self.mock_client, self.account_id)

        self.order_id = 1

        self.maxDiff = None

    ##########################################################################
    # extract_order_id tests

    @no_duplicates
    def test_extract_order_id_order_not_ok(self):
        response = MockResponse({}, False)
        with self.assertRaises(ValueError, msg='order not successful'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_extract_order_id_no_location(self):
        response = MockResponse({}, True, headers={})
        self.assertIsNone(self.utils.extract_order_id(response))

    @no_duplicates
    def test_extract_order_id_no_pattern_match(self):
        response = MockResponse({}, True, headers={
            'Location': 'https://api.tdameritrade.com/v1/accounts/12345'})
        self.assertIsNone(self.utils.extract_order_id(response))

    @no_duplicates
    def test_get_order_nonmatching_account_id(self):
        response = MockResponse({}, True, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/456'.format(
                self.account_id + 1)})
        with self.assertRaises(
                ValueError, msg='order request account ID != Utils.account_id'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_get_order_nonmatching_account_id_str(self):
        self.utils = Utils(self.mock_client, str(self.account_id))

        response = MockResponse({}, True, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/456'.format(
                self.account_id + 1)})
        with self.assertRaises(
                ValueError, msg='order request account ID != Utils.account_id'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_get_order_success(self):
        order_id = self.account_id + 100
        response = MockResponse({}, True, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/{}'.format(
                self.account_id, order_id)})
        self.assertEqual(order_id, self.utils.extract_order_id(response))

    @no_duplicates
    def test_get_order_success_str_account_id(self):
        self.utils = Utils(self.mock_client, str(self.account_id))

        order_id = self.account_id + 100
        response = MockResponse({}, True, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/{}'.format(
                self.account_id, order_id)})
        self.assertEqual(order_id, self.utils.extract_order_id(response))

    ##########################################################################
    # find_most_recent_order tests

    def order(self, time, symbol, quantity, instruction, order_type):
        order = test_utils.real_order()
        order['orderId'] = self.order_id
        order['enteredTime'] = time
        order['closeTime'] = time
        order['accountId'] = self.account_id
        order['orderType'] = order_type
        order['orderLegCollection'][0]['quantity'] = quantity
        order['orderLegCollection'][0]['instruction'] = instruction
        order['orderLegCollection'][0]['instrument']['symbol'] = symbol
        order['orderActivityCollection'][0]['executionLegs'][0]['time'] = time
        order['orderActivityCollection'][0]['quantity'] = quantity
        order['orderActivityCollection'][0]['executionLegs'][0]['quantity'] \
            = quantity

        self.order_id += 1

        return order

    @no_duplicates
    def test_most_recent_order(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        order = self.utils.find_most_recent_order()
        self.assertEqual(order2, order)

    @no_duplicates
    def test_too_many_order_legs(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.find_most_recent_order()
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'].append(order2['orderLegCollection'][0])
        out_order = self.utils.find_most_recent_order()
        self.assertEqual(order1, out_order)

    @no_duplicates
    def test_non_equity_asset_type(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.find_most_recent_order()
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'][0]['instrument']['assetType'] = 'OPTION'
        out_order = self.utils.find_most_recent_order()
        self.assertEqual(order1, out_order)

    @no_duplicates
    def test_different_symbol(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.find_most_recent_order(symbol='AAPL')
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'][0]['instrument']['symbol'] = 'MSFT'
        out_order = self.utils.find_most_recent_order(symbol='AAPL')
        self.assertEqual(order1, out_order)

    @no_duplicates
    def test_quantity_and_symbol(self):
        msg = 'when specifying quantity, must also specify symbol'
        with self.assertRaises(ValueError, msg=msg):
            out_order = self.utils.find_most_recent_order(quantity=1)

    @no_duplicates
    def test_different_quantity(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.find_most_recent_order(
            symbol='AAPL', quantity=1)
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'][0]['quantity'] = 10
        out_order = self.utils.find_most_recent_order(
            symbol='AAPL', quantity=1)
        self.assertEqual(order1, out_order)

    @no_duplicates
    def test_different_instruction(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.find_most_recent_order(
            instruction=EquityOrderBuilder.Instruction.BUY)
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'][0]['instruction'] = 'SELL'
        out_order = self.utils.find_most_recent_order(
            instruction=EquityOrderBuilder.Instruction.BUY)
        self.assertEqual(order1, out_order)

    @no_duplicates
    def test_different_order_type(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.find_most_recent_order(
            order_type=EquityOrderBuilder.OrderType.MARKET)
        self.assertEqual(order2, out_order)

        order2['orderType'] = 'LIMIT'
        out_order = self.utils.find_most_recent_order(
            order_type=EquityOrderBuilder.OrderType.MARKET)
        self.assertEqual(order1, out_order)
