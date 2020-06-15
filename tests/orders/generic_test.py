import unittest

from tda.orders.generic import *
from tests.test_utils import has_diff


class TestClient(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    ##########################################################################
    # Functional tests from here:
    # https://developer.tdameritrade.com/content/place-order-samples

    def test_buy_market_stock(self):
        builder = (
            OrderBuilder()
            .set_order_type(OrderType.MARKET)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_order_leg(
                instruction=Instruction.BUY,
                instrument=EquityInstrument('XYZ'),
                quantity=15))

        expected = {
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [
                {
                    'instruction': 'BUY',  # The original says 'Buy'
                    'quantity': 15,
                    'instrument': {
                        'symbol': 'XYZ',
                        'assetType': 'EQUITY'
                    }
                }
            ]
        }

        self.assertFalse(has_diff(expected, builder.build()))

    def test_buy_limit_single_option(self):
        builder = (
            OrderBuilder()
            .set_complex_order_strategy_type(ComplexOrderStrategyType.NONE)
            .set_order_type(OrderType.LIMIT)
            .set_session(Session.NORMAL)
            .set_price(6.45)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_order_leg(
                instruction=Instruction.BUY_TO_OPEN,
                instrument=OptionInstrument('XYZ_032015C49'),
                quantity=10))

        expected = {
            'complexOrderStrategyType': 'NONE',
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'price': '6.45',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [
                {
                    'instruction': 'BUY_TO_OPEN',
                    'quantity': 10,
                    'instrument': {
                        'symbol': 'XYZ_032015C49',
                        'assetType': 'OPTION'
                    }
                }
            ]
        }

        self.assertFalse(has_diff(expected, builder.build()))

    def test_buy_limit_vertical_call_spread(self):
        builder = (
            OrderBuilder()
            .set_order_type(OrderType.NET_DEBIT)
            .set_session(Session.NORMAL)
            .set_price(1.20)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_order_leg(
                instruction=Instruction.BUY_TO_OPEN,
                quantity=10,
                instrument=OptionInstrument('XYZ_011516C40'))
            .add_order_leg(
                instruction=Instruction.SELL_TO_OPEN,
                quantity=10,
                instrument=OptionInstrument('XYZ_011516C42.5')))

        expected = {
            'orderType': 'NET_DEBIT',
            'session': 'NORMAL',
            'price': '1.20',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [
                {
                    'instruction': 'BUY_TO_OPEN',
                    'quantity': 10,
                    'instrument': {
                        'symbol': 'XYZ_011516C40',
                        'assetType': 'OPTION'
                    }
                },
                {
                    'instruction': 'SELL_TO_OPEN',
                    'quantity': 10,
                    'instrument': {
                        'symbol': 'XYZ_011516C42.5',
                        'assetType': 'OPTION'
                    }
                }
            ]
        }

        self.assertFalse(has_diff(expected, builder.build()))

    def test_custom_option_spread(self):
        builder = (
            OrderBuilder()
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .set_order_type(OrderType.MARKET)
            .add_order_leg(
                instrument=OptionInstrument('XYZ_011819P45'),
                instruction=Instruction.SELL_TO_OPEN,
                quantity=1)
            .add_order_leg(
                instrument=OptionInstrument('XYZ_011720P43'),
                instruction=Instruction.BUY_TO_OPEN,
                quantity=2)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.CUSTOM)
            .set_duration(Duration.DAY)
            .set_session(Session.NORMAL))

        expected = {
            'orderStrategyType': 'SINGLE',
            'orderType': 'MARKET',
            'orderLegCollection': [
                {
                    'instrument': {
                        'assetType': 'OPTION',
                        'symbol': 'XYZ_011819P45'
                    },
                    'instruction': 'SELL_TO_OPEN',
                    'quantity': 1
                },
                {
                    'instrument': {
                        'assetType': 'OPTION',
                        'symbol': 'XYZ_011720P43'
                    },
                    'instruction': 'BUY_TO_OPEN',
                    'quantity': 2
                }
            ],
            'complexOrderStrategyType': 'CUSTOM',
            'duration': 'DAY',
            'session': 'NORMAL'
        }

        self.assertFalse(has_diff(expected, builder.build()))

    def test_conditional_order_one_triggers_another(self):
        builder = (
            OrderBuilder()
            .set_order_type(OrderType.LIMIT)
            .set_session(Session.NORMAL)
            .set_price(34.97)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.TRIGGER)
            .add_order_leg(
                instruction=Instruction.BUY,
                quantity=10,
                instrument=EquityInstrument('XYZ'))
            .add_child_order_strategy(
                OrderBuilder()
                .set_order_type(OrderType.LIMIT)
                .set_session(Session.NORMAL)
                .set_price(42.03)
                .set_duration(Duration.DAY)
                .set_order_strategy_type(OrderStrategyType.SINGLE)
                .add_order_leg(
                    instruction=Instruction.SELL,
                    quantity=10,
                    instrument=EquityInstrument('XYZ'))))

        expected = {
            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'price': '34.97',
            'duration': 'DAY',
            'orderStrategyType': 'TRIGGER',
            'orderLegCollection': [
                {
                    'instruction': 'BUY',
                    'quantity': 10,
                    'instrument': {
                        'symbol': 'XYZ',
                        'assetType': 'EQUITY'
                    }
                }
            ],
            'childOrderStrategies': [
                {
                    'orderType': 'LIMIT',
                    'session': 'NORMAL',
                    'price': '42.03',
                    'duration': 'DAY',
                    'orderStrategyType': 'SINGLE',
                    'orderLegCollection': [
                        {
                            'instruction': 'SELL',
                            'quantity': 10,
                            'instrument': {
                                'symbol': 'XYZ',
                                'assetType': 'EQUITY'
                            }
                        }
                    ]
                }
            ]
        }

        self.assertFalse(has_diff(expected, builder.build()))

    def test_conditional_order_one_cancels_another(self):
        builder = (
            OrderBuilder()
            .set_order_strategy_type(OrderStrategyType.OCO)
            .add_child_order_strategy(
                OrderBuilder()
                .set_order_type(OrderType.LIMIT)
                .set_session(Session.NORMAL)
                .set_price(45.97)
                .set_duration(Duration.DAY)
                .set_order_strategy_type(OrderStrategyType.SINGLE)
                .add_order_leg(Instruction.SELL, EquityInstrument('XYZ'), 2)
            )
            .add_child_order_strategy(
                OrderBuilder()
                .set_order_type(OrderType.STOP_LIMIT)
                .set_session(Session.NORMAL)
                .set_price(37.00)
                .set_stop_price(37.03)
                .set_duration(Duration.DAY)
                .set_order_strategy_type(OrderStrategyType.SINGLE)
                .add_order_leg(Instruction.SELL, EquityInstrument('XYZ'), 2)))

        expected = {
            'orderStrategyType': 'OCO',
            'childOrderStrategies': [
                {
                    'orderType': 'LIMIT',
                    'session': 'NORMAL',
                    'price': '45.97',
                    'duration': 'DAY',
                    'orderStrategyType': 'SINGLE',
                    'orderLegCollection': [
                        {
                            'instruction': 'SELL',
                            'quantity': 2,
                            'instrument': {
                                'symbol': 'XYZ',
                                'assetType': 'EQUITY'
                            }
                        }
                    ]
                },
                {
                    'orderType': 'STOP_LIMIT',
                    'session': 'NORMAL',
                    'price': '37.00',
                    'stopPrice': '37.03',
                    'duration': 'DAY',
                    'orderStrategyType': 'SINGLE',
                    'orderLegCollection': [
                        {
                            'instruction': 'SELL',
                            'quantity': 2,
                            'instrument': {
                                'symbol': 'XYZ',
                                'assetType': 'EQUITY'
                            }
                        }
                    ]
                }
            ]
        }

        self.assertFalse(has_diff(expected, builder.build()))

    def test_conditional_order_one_triggers_a_one_cancels_other(self):
        builder = (
            OrderBuilder()
            .set_order_strategy_type(OrderStrategyType.TRIGGER)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.LIMIT)
            .set_price(14.97)
            .add_order_leg(
                instruction=Instruction.BUY,
                quantity=5,
                instrument=EquityInstrument('XYZ'))
            .add_child_order_strategy(
                OrderBuilder()
                .set_order_strategy_type(OrderStrategyType.OCO)
                .add_child_order_strategy(
                    OrderBuilder()
                    .set_order_strategy_type(OrderStrategyType.SINGLE)
                    .set_session(Session.NORMAL)
                    .set_duration(Duration.GOOD_TILL_CANCEL)
                    .set_order_type(OrderType.LIMIT)
                    .set_price(15.27)
                    .add_order_leg(
                        instruction=Instruction.SELL,
                        quantity=5,
                        instrument=EquityInstrument('XYZ')))
                .add_child_order_strategy(
                    OrderBuilder()
                    .set_order_strategy_type(OrderStrategyType.SINGLE)
                    .set_session(Session.NORMAL)
                    .set_duration(Duration.GOOD_TILL_CANCEL)
                    .set_order_type(OrderType.STOP)
                    .set_stop_price(11.27)
                    .add_order_leg(
                        instruction=Instruction.SELL,
                        quantity=5,
                        instrument=EquityInstrument('XYZ')))))

        expected = {
            'orderStrategyType': 'TRIGGER',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderType': 'LIMIT',
            'price': '14.97',
            'orderLegCollection': [
                {
                    'instruction': 'BUY',
                    'quantity': 5,
                    'instrument': {
                        'assetType': 'EQUITY',
                        'symbol': 'XYZ'
                    }
                }
            ],
            'childOrderStrategies': [
                {
                    'orderStrategyType': 'OCO',
                    'childOrderStrategies': [
                        {
                            'orderStrategyType': 'SINGLE',
                            'session': 'NORMAL',
                            'duration': 'GOOD_TILL_CANCEL',
                            'orderType': 'LIMIT',
                            'price': '15.27',
                            'orderLegCollection': [
                                {
                                    'instruction': 'SELL',
                                    'quantity': 5,
                                    'instrument': {
                                        'assetType': 'EQUITY',
                                        'symbol': 'XYZ'
                                    }
                                }
                            ]
                        },
                        {
                            'orderStrategyType': 'SINGLE',
                            'session': 'NORMAL',
                            'duration': 'GOOD_TILL_CANCEL',
                            'orderType': 'STOP',
                            'stopPrice': '11.27',
                            'orderLegCollection': [
                                {
                                    'instruction': 'SELL',
                                    'quantity': 5,
                                    'instrument': {
                                        'assetType': 'EQUITY',
                                        'symbol': 'XYZ'
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertFalse(has_diff(expected, builder.build()))

    def test_sell_trailing_stop_stock(self):
        builder = (
            OrderBuilder()
            .set_complex_order_strategy_type(ComplexOrderStrategyType.NONE)
            .set_order_type(OrderType.TRAILING_STOP)
            .set_session(Session.NORMAL)
            .set_stop_price_link_basis(StopPriceLinkBasis.BID)
            .set_stop_price_link_type(StopPriceLinkType.VALUE)
            .set_stop_price_offset(10)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_order_leg(
                instruction=Instruction.SELL,
                quantity=10,
                instrument=EquityInstrument('XYZ')))

        expected = {
            'complexOrderStrategyType': 'NONE',
            'orderType': 'TRAILING_STOP',
            'session': 'NORMAL',
            'stopPriceLinkBasis': 'BID',
            'stopPriceLinkType': 'VALUE',
            'stopPriceOffset': 10,
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [
                {
                    'instruction': 'SELL',
                    'quantity': 10,
                    'instrument': {
                        'symbol': 'XYZ',
                        'assetType': 'EQUITY'
                    }
                }
            ]
        }

        self.assertFalse(has_diff(expected, builder.build()))
