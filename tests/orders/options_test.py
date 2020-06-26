import unittest

from tda.orders.common import *
from tda.orders.options import *
from tests.test_utils import has_diff, no_duplicates


class OptionTemplatesTest(unittest.TestCase):

    # Buy to open

    def test_option_buy_to_open_market(self):
        self.assertFalse(has_diff({
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }]
        }, option_buy_to_open_market('GOOG_012122P2200', 10).build()))

    def test_option_buy_to_open_limit(self):
        self.assertFalse(has_diff({
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '32.50',
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }]
        }, option_buy_to_open_limit('GOOG_012122P2200', 10, 32.5).build()))

    # Sell to open

    def test_option_sell_to_open_market(self):
        self.assertFalse(has_diff({
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'SELL_TO_OPEN',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }]
        }, option_sell_to_open_market('GOOG_012122P2200', 10).build()))

    def test_option_sell_to_open_limit(self):
        self.assertFalse(has_diff({
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '32.50',
            'orderLegCollection': [{
                'instruction': 'SELL_TO_OPEN',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }]
        }, option_sell_to_open_limit('GOOG_012122P2200', 10, 32.5).build()))

    # Buy to close

    def test_option_sell_to_open_market(self):
        self.assertFalse(has_diff({
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'BUY_TO_CLOSE',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }]
        }, option_buy_to_close_market('GOOG_012122P2200', 10).build()))

    def test_option_buy_to_close_limit(self):
        self.assertFalse(has_diff({
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '32.50',
            'orderLegCollection': [{
                'instruction': 'BUY_TO_CLOSE',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }]
        }, option_buy_to_close_limit('GOOG_012122P2200', 10, 32.5).build()))

    # Sell to close

    def test_option_sell_to_open_market(self):
        self.assertFalse(has_diff({
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'SELL_TO_CLOSE',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }]
        }, option_sell_to_close_market('GOOG_012122P2200', 10).build()))

    def test_option_buy_to_close_limit(self):
        self.assertFalse(has_diff({
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '32.50',
            'orderLegCollection': [{
                'instruction': 'SELL_TO_CLOSE',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }]
        }, option_sell_to_close_limit('GOOG_012122P2200', 10, 32.5).build()))


