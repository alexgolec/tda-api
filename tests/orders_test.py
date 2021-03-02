import unittest

from tda.orders.common import *
from tda.orders.equities import *
from .utils import has_diff, no_duplicates
from . import test_utils


class BuilderTemplates(unittest.TestCase):

    def test_equity_buy_market(self):
        self.assertFalse(has_diff({
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'BUY',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY',
                }
            }]
        }, equity_buy_market('GOOG', 10).build()))

    def test_equity_buy_limit(self):
        self.assertFalse(has_diff({
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'price': '199.99',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'BUY',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY',
                }
            }]
        }, equity_buy_limit('GOOG', 10, 199.99).build()))

    def test_equity_sell_market(self):
        self.assertFalse(has_diff({
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'SELL',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY',
                }
            }]
        }, equity_sell_market('GOOG', 10).build()))

    def test_equity_sell_limit(self):
        self.assertFalse(has_diff({
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'price': '199.99',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'SELL',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY',
                }
            }]
        }, equity_sell_limit('GOOG', 10, 199.99).build()))

    def test_equity_sell_short_market(self):
        self.assertFalse(has_diff({
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'SELL_SHORT',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY',
                }
            }]
        }, equity_sell_short_market('GOOG', 10).build()))

    def test_equity_sell_short_limit(self):
        self.assertFalse(has_diff({
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'price': '199.99',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'SELL_SHORT',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY',
                }
            }]
        }, equity_sell_short_limit('GOOG', 10, 199.99).build()))

    def test_equity_buy_to_cover_market(self):
        self.assertFalse(has_diff({
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'BUY_TO_COVER',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY',
                }
            }]
        }, equity_buy_to_cover_market('GOOG', 10).build()))

    def test_equity_buy_to_cover_limit(self):
        self.assertFalse(has_diff({
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'price': '199.99',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'BUY_TO_COVER',
                'quantity': 10,
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY',
                }
            }]
        }, equity_buy_to_cover_limit('GOOG', 10, 199.99).build()))
