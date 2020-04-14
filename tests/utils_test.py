from unittest.mock import MagicMock

import datetime
import json
import unittest

from tda.orders import EquityOrderBuilder
from tda.utils import Utils
from . import test_utils


class MockResponse:
    def __init__(self, json, ok):
        self._json = json
        self.ok = ok

    def json(self):
        return self._json


class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.account_id = 10000
        self.utils = Utils(self.mock_client, self.account_id)

        self.order_id = 1

        self.maxDiff = None

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

    def test_most_recent_order(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        order = self.utils.get_most_recent_order()
        self.assertEqual(order2, order)

    def test_too_many_order_legs(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.get_most_recent_order()
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'].append(order2['orderLegCollection'][0])
        out_order = self.utils.get_most_recent_order()
        self.assertEqual(order1, out_order)

    def test_non_equity_asset_type(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.get_most_recent_order()
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'][0]['instrument']['assetType'] = 'OPTION'
        out_order = self.utils.get_most_recent_order()
        self.assertEqual(order1, out_order)

    def test_different_symbol(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.get_most_recent_order(symbol='AAPL')
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'][0]['instrument']['symbol'] = 'MSFT'
        out_order = self.utils.get_most_recent_order(symbol='AAPL')
        self.assertEqual(order1, out_order)

    def test_quantity_and_symbol(self):
        msg = 'when specifying quantity, must also specify symbol'
        with self.assertRaises(ValueError, msg=msg):
            out_order = self.utils.get_most_recent_order(quantity=1)

    def test_different_quantity(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.get_most_recent_order(
            symbol='AAPL', quantity=1)
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'][0]['quantity'] = 10
        out_order = self.utils.get_most_recent_order(
            symbol='AAPL', quantity=1)
        self.assertEqual(order1, out_order)

    def test_different_instruction(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.get_most_recent_order(
            instruction=EquityOrderBuilder.Instruction.BUY)
        self.assertEqual(order2, out_order)

        order2['orderLegCollection'][0]['instruction'] = 'SELL'
        out_order = self.utils.get_most_recent_order(
            instruction=EquityOrderBuilder.Instruction.BUY)
        self.assertEqual(order1, out_order)

    def test_different_order_type(self):
        order1 = self.order(
            '2020-01-01T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')
        order2 = self.order(
            '2020-01-02T12:00:00+0000', 'AAPL', 1, 'BUY', 'MARKET')

        self.mock_client.get_orders_by_path = MagicMock(
            return_value=MockResponse([order1, order2], True))

        out_order = self.utils.get_most_recent_order(
            order_type=EquityOrderBuilder.OrderType.MARKET)
        self.assertEqual(order2, out_order)

        order2['orderType'] = 'LIMIT'
        out_order = self.utils.get_most_recent_order(
            order_type=EquityOrderBuilder.OrderType.MARKET)
        self.assertEqual(order1, out_order)
