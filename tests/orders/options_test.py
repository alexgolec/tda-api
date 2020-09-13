import datetime
import unittest

from tda.orders.common import *
from tda.orders.options import *
from ..utils import has_diff, no_duplicates


class OptionSymbolTest(unittest.TestCase):

    @no_duplicates
    def test_parse_success_put(self):
        op = OptionSymbol.parse_symbol('GOOG_012122P2200')
        self.assertEqual(op.underlying_symbol, 'GOOG')
        self.assertEqual(
                op.expiration_date, datetime.date(
                    year=2022, month=1, day=21))
        self.assertEqual(op.contract_type, 'P')
        self.assertEqual(op.strike_price, '2200')

        self.assertEqual('GOOG_012122P2200', op.build())

    @no_duplicates
    def test_parse_success_call(self):
        op = OptionSymbol.parse_symbol('GOOG_012122C2200')
        self.assertEqual(op.underlying_symbol, 'GOOG')
        self.assertEqual(
                op.expiration_date, datetime.date(
                    year=2022, month=1, day=21))
        self.assertEqual(op.contract_type, 'C')
        self.assertEqual(op.strike_price, '2200')

        self.assertEqual('GOOG_012122C2200', op.build())

    @no_duplicates
    def test_parse_success_decimal_point_in_strike(self):
        op = OptionSymbol.parse_symbol('GOOG_012122C2200.25')
        self.assertEqual(op.underlying_symbol, 'GOOG')
        self.assertEqual(
                op.expiration_date, datetime.date(
                    year=2022, month=1, day=21))
        self.assertEqual(op.contract_type, 'C')
        self.assertEqual(op.strike_price, '2200.25')

        self.assertEqual('GOOG_012122C2200.25', op.build())

    @no_duplicates
    def test_parse_missing_underscore(self):
        with self.assertRaisesRegex(ValueError, 'missing underscore'):
            op = OptionSymbol.parse_symbol('GOOG012122C2200')

    @no_duplicates
    def test_parse_invalid_datetime(self):
        with self.assertRaisesRegex(
                ValueError, 'expiration date must follow format'):
            op = OptionSymbol.parse_symbol('GOOG_142122C2200')

    @no_duplicates
    def test_parse_invalid_contract_type(self):
        with self.assertRaisesRegex(
                ValueError, 'option must have contract type'):
            op = OptionSymbol.parse_symbol('GOOG_012122X2200')

    @no_duplicates
    def test_parse_invalid_strike_price(self):
        with self.assertRaisesRegex(ValueError, 'positive float'):
            op = OptionSymbol.parse_symbol('GOOG_012122C-2200')

    @no_duplicates
    def test_init_success_call(self):
        op = OptionSymbol('GOOG', '121520', 'C', '2200')
        self.assertEqual(op.underlying_symbol, 'GOOG')
        self.assertEqual(
                op.expiration_date, datetime.date(
                    year=2020, month=12, day=15))
        self.assertEqual(op.contract_type, 'C')
        self.assertEqual(op.strike_price, '2200')

        self.assertEqual('GOOG_121520C2200', op.build())

    @no_duplicates
    def test_init_success_put(self):
        op = OptionSymbol('GOOG', '121520', 'P', '2200')
        self.assertEqual(op.underlying_symbol, 'GOOG')
        self.assertEqual(
                op.expiration_date, datetime.date(
                    year=2020, month=12, day=15))
        self.assertEqual(op.contract_type, 'P')
        self.assertEqual(op.strike_price, '2200')

        self.assertEqual('GOOG_121520P2200', op.build())

    @no_duplicates
    def test_init_success_datetime(self):
        op = OptionSymbol(
                'GOOG', datetime.datetime(year=2020, month=12, day=15),
                'P', '2200')
        self.assertEqual(op.underlying_symbol, 'GOOG')
        self.assertEqual(
                op.expiration_date, datetime.date(
                    year=2020, month=12, day=15))
        self.assertEqual(op.contract_type, 'P')
        self.assertEqual(op.strike_price, '2200')

        self.assertEqual('GOOG_121520P2200', op.build())

    @no_duplicates
    def test_init_success_date(self):
        op = OptionSymbol(
                'GOOG', datetime.date(year=2020, month=12, day=15),
                'P', '2200')
        self.assertEqual(op.underlying_symbol, 'GOOG')
        self.assertEqual(
                op.expiration_date, datetime.date(
                    year=2020, month=12, day=15))
        self.assertEqual(op.contract_type, 'P')
        self.assertEqual(op.strike_price, '2200')

        self.assertEqual('GOOG_121520P2200', op.build())

    @no_duplicates
    def test_init_success_decimal_in_strike(self):
        op = OptionSymbol('GOOG', '121520', 'P', '2200.25')
        self.assertEqual(op.underlying_symbol, 'GOOG')
        self.assertEqual(
                op.expiration_date, datetime.date(
                    year=2020, month=12, day=15))
        self.assertEqual(op.contract_type, 'P')
        self.assertEqual(op.strike_price, '2200.25')

        self.assertEqual('GOOG_121520P2200.25', op.build())

    @no_duplicates
    def test_init_invalid_date(self):
        with self.assertRaisesRegex(
                ValueError, 'expiration date must follow format'):
            OptionSymbol('GOOG', '901520', 'C', '2200')

    @no_duplicates
    def test_init_invalid_date_type(self):
        with self.assertRaisesRegex(
                ValueError, 'expiration_date must be a string with format'):
            OptionSymbol('GOOG', ('tuple', 'tuple'), 'C', '2200')

    @no_duplicates
    def test_init_contract_type(self):
        with self.assertRaisesRegex(
                ValueError, 'Contract type must be one of'):
            OptionSymbol('GOOG', '121520', 'K', '2200')

    @no_duplicates
    def test_init_negative_strike(self):
        with self.assertRaisesRegex(
                ValueError, 'string representing a positive float'):
            OptionSymbol('GOOG', '121520', 'C', '-2200')

    @no_duplicates
    def test_init_invalid_strike(self):
        with self.assertRaisesRegex(
                ValueError, 'string representing a positive float'):
            OptionSymbol('GOOG', '121520', 'C', '23fwe')


class OptionTemplatesTest(unittest.TestCase):

    # Buy to open

    @no_duplicates
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

    @no_duplicates
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

    @no_duplicates
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

    @no_duplicates
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

    @no_duplicates
    def test_option_buy_to_close_market(self):
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

    @no_duplicates
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

    @no_duplicates
    def test_option_sell_to_close_market(self):
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

    @no_duplicates
    def test_option_sell_to_close_limit(self):
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



class VerticalTemplatesTest(unittest.TestCase):

    @no_duplicates
    def test_bull_call_vertical_open(self):
        self.assertFalse(has_diff({
            'orderType': 'NET_DEBIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '30.60',
            'complexOrderStrategyType': 'VERTICAL',
            'quantity': 3,
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122C2200',
                    'assetType': 'OPTION',
                }
            }, {
                'instruction': 'SELL_TO_OPEN',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122C2400',
                    'assetType': 'OPTION',
                }
            }]
        }, bull_call_vertical_open(
            'GOOG_012122C2200',
            'GOOG_012122C2400',
            3, 30.6).build()))

    @no_duplicates
    def test_bull_call_vertical_close(self):
        self.assertFalse(has_diff({
            'orderType': 'NET_CREDIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '30.60',
            'complexOrderStrategyType': 'VERTICAL',
            'quantity': 3,
            'orderLegCollection': [{
                'instruction': 'SELL_TO_CLOSE',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122C2200',
                    'assetType': 'OPTION',
                }
            }, {
                'instruction': 'BUY_TO_CLOSE',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122C2400',
                    'assetType': 'OPTION',
                }
            }]
        }, bull_call_vertical_close(
            'GOOG_012122C2200',
            'GOOG_012122C2400',
            3, 30.6).build()))

    @no_duplicates
    def test_bear_call_vertical_open(self):
        self.assertFalse(has_diff({
            'orderType': 'NET_CREDIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '30.60',
            'complexOrderStrategyType': 'VERTICAL',
            'quantity': 3,
            'orderLegCollection': [{
                'instruction': 'SELL_TO_OPEN',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122C2200',
                    'assetType': 'OPTION',
                }
            }, {
                'instruction': 'BUY_TO_OPEN',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122C2400',
                    'assetType': 'OPTION',
                }
            }]
        }, bear_call_vertical_open(
            'GOOG_012122C2200',
            'GOOG_012122C2400',
            3, 30.6).build()))

    @no_duplicates
    def test_bear_call_vertical_close(self):
        self.assertFalse(has_diff({
            'orderType': 'NET_DEBIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '30.60',
            'complexOrderStrategyType': 'VERTICAL',
            'quantity': 3,
            'orderLegCollection': [{
                'instruction': 'BUY_TO_CLOSE',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122C2200',
                    'assetType': 'OPTION',
                }
            }, {
                'instruction': 'SELL_TO_CLOSE',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122C2400',
                    'assetType': 'OPTION',
                }
            }]
        }, bear_call_vertical_close(
            'GOOG_012122C2200',
            'GOOG_012122C2400',
            3, 30.6).build()))

    @no_duplicates
    def test_bull_put_vertical_open(self):
        self.assertFalse(has_diff({
            'orderType': 'NET_CREDIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '30.60',
            'complexOrderStrategyType': 'VERTICAL',
            'quantity': 3,
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }, {
                'instruction': 'SELL_TO_OPEN',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122P2400',
                    'assetType': 'OPTION',
                }
            }]
        }, bull_put_vertical_open(
            'GOOG_012122P2200',
            'GOOG_012122P2400',
            3, 30.6).build()))

    @no_duplicates
    def test_bull_put_vertical_close(self):
        self.assertFalse(has_diff({
            'orderType': 'NET_DEBIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '30.60',
            'complexOrderStrategyType': 'VERTICAL',
            'quantity': 3,
            'orderLegCollection': [{
                'instruction': 'SELL_TO_CLOSE',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }, {
                'instruction': 'BUY_TO_CLOSE',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122P2400',
                    'assetType': 'OPTION',
                }
            }]
        }, bull_put_vertical_close(
            'GOOG_012122P2200',
            'GOOG_012122P2400',
            3, 30.6).build()))

    @no_duplicates
    def test_bear_put_vertical_open(self):
        self.assertFalse(has_diff({
            'orderType': 'NET_DEBIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '30.60',
            'complexOrderStrategyType': 'VERTICAL',
            'quantity': 3,
            'orderLegCollection': [{
                'instruction': 'SELL_TO_OPEN',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }, {
                'instruction': 'BUY_TO_OPEN',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122P2400',
                    'assetType': 'OPTION',
                }
            }]
        }, bear_put_vertical_open(
            'GOOG_012122P2200',
            'GOOG_012122P2400',
            3, 30.6).build()))

    @no_duplicates
    def test_bear_put_vertical_close(self):
        self.assertFalse(has_diff({
            'orderType': 'NET_CREDIT',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'price': '30.60',
            'complexOrderStrategyType': 'VERTICAL',
            'quantity': 3,
            'orderLegCollection': [{
                'instruction': 'BUY_TO_CLOSE',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122P2200',
                    'assetType': 'OPTION',
                }
            }, {
                'instruction': 'SELL_TO_CLOSE',
                'quantity': 3,
                'instrument': {
                    'symbol': 'GOOG_012122P2400',
                    'assetType': 'OPTION',
                }
            }]
        }, bear_put_vertical_close(
            'GOOG_012122P2200',
            'GOOG_012122P2400',
            3, 30.6).build()))


