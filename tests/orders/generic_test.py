import unittest

from tda.orders.generic import *
from tda.orders.common import *
from tests.test_utils import has_diff


class OrderBuilderTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.order_builder = OrderBuilder()

    ##########################################################################
    # Session

    def test_session_success(self):
        self.order_builder.set_session(Session.NORMAL)
        self.assertFalse(has_diff({
            'session': 'NORMAL'
        }, self.order_builder.build()))

        self.order_builder.clear_session()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_session_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_session('NORMAL')

    def test_session_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_session('NORMAL')
        self.assertFalse(has_diff({
            'session': 'NORMAL'
        }, self.order_builder.build()))

    ##########################################################################
    # Duration

    def test_duration_success(self):
        self.order_builder.set_duration(Duration.DAY)
        self.assertFalse(has_diff({
            'duration': 'DAY'
        }, self.order_builder.build()))

        self.order_builder.clear_duration()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_duration_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_duration('DAY')

    def test_duration_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_duration('DAY')
        self.assertFalse(has_diff({
            'duration': 'DAY'
        }, self.order_builder.build()))

    ##########################################################################
    # OrderType

    def test_order_type_success(self):
        self.order_builder.set_order_type(OrderType.MARKET)
        self.assertFalse(has_diff({
            'orderType': 'MARKET'
        }, self.order_builder.build()))

        self.order_builder.clear_order_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_order_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_order_type('MARKET')

    def test_order_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_order_type('MARKET')
        self.assertFalse(has_diff({
            'orderType': 'MARKET'
        }, self.order_builder.build()))

    ##########################################################################
    # ComplexOrderStrategyType

    def test_complex_order_strategy_type_success(self):
        self.order_builder.set_complex_order_strategy_type(
            ComplexOrderStrategyType.IRON_CONDOR)
        self.assertFalse(has_diff({
            'complexOrderStrategyType': 'IRON_CONDOR'
        }, self.order_builder.build()))

        self.order_builder.clear_complex_order_strategy_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test__wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_complex_order_strategy_type('IRON_CONDOR')

    def test__wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_complex_order_strategy_type('IRON_CONDOR')
        self.assertFalse(has_diff({
            'complexOrderStrategyType': 'IRON_CONDOR'
        }, self.order_builder.build()))

    ##########################################################################
    # Quantity

    def test_quantity_success(self):
        self.order_builder.set_quantity(12)
        self.assertFalse(has_diff({
            'quantity': 12
        }, self.order_builder.build()))

        self.order_builder.clear_quantity()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_quantity(-12)

    def test_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_quantity(0)

    ##########################################################################
    # RequestedDestination

    def test_requested_destination_success(self):
        self.order_builder.set_requested_destination(Destination.INET)
        self.assertFalse(has_diff({
            'requestedDestination': 'INET'
        }, self.order_builder.build()))

        self.order_builder.clear_requested_destination()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_requested_destination_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_requested_destination('INET')

    def test_requested_destination_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_requested_destination('INET')
        self.assertFalse(has_diff({
            'requestedDestination': 'INET'
        }, self.order_builder.build()))

    ##########################################################################
    # StopPrice

    def test_stop_price_success(self):
        self.order_builder.set_stop_price(42.90)
        self.assertFalse(has_diff({
            'stopPrice': '42.90'
        }, self.order_builder.build()))

        self.order_builder.clear_stop_price()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_stop_price_negative(self):
        self.order_builder.set_stop_price(-1.31)
        self.assertFalse(has_diff({
            'stopPrice': '-1.31'
        }, self.order_builder.build()))

    def test_stop_price_zero(self):
        self.order_builder.set_stop_price(0)
        self.assertFalse(has_diff({
            'stopPrice': '0.00'
        }, self.order_builder.build()))

    def test_stop_price_do_not_round_up(self):
        self.order_builder.set_stop_price(1.99999)
        self.assertFalse(has_diff({
            'stopPrice': '1.99'
        }, self.order_builder.build()))

    def test_stop_price_do_round_down(self):
        self.order_builder.set_stop_price(2.00001)
        self.assertFalse(has_diff({
            'stopPrice': '2.00'
        }, self.order_builder.build()))

    ##########################################################################
    # StopPriceLinkBasis

    def test_stop_price_link_basis_success(self):
        self.order_builder.set_stop_price_link_basis(StopPriceLinkBasis.ASK)
        self.assertFalse(has_diff({
            'stopPriceLinkBasis': 'ASK'
        }, self.order_builder.build()))

        self.order_builder.clear_stop_price_link_basis()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_stop_price_link_basis_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_stop_price_link_basis('ASK')

    def test_stop_price_link_basis_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_stop_price_link_basis('ASK')
        self.assertFalse(has_diff({
            'stopPriceLinkBasis': 'ASK'
        }, self.order_builder.build()))

    ##########################################################################
    # StopPriceLinkType

    def test_stop_price_link_type_success(self):
        self.order_builder.set_stop_price_link_type(StopPriceLinkType.VALUE)
        self.assertFalse(has_diff({
            'stopPriceLinkType': 'VALUE'
        }, self.order_builder.build()))

        self.order_builder.clear_stop_price_link_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_stop_price_link_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_stop_price_link_type('VALUE')

    def test_stop_price_link_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_stop_price_link_type('VALUE')
        self.assertFalse(has_diff({
            'stopPriceLinkType': 'VALUE'
        }, self.order_builder.build()))

    ##########################################################################
    # StopPriceOffset

    def test_stop_price_offset_success(self):
        self.order_builder.set_stop_price_offset(12.98)
        self.assertFalse(has_diff({
            'stopPriceOffset': 12.98
        }, self.order_builder.build()))

        self.order_builder.clear_stop_price_offset()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    ##########################################################################
    # StopType

    def test_stop_type_success(self):
        self.order_builder.set_stop_type(StopType.MARK)
        self.assertFalse(has_diff({
            'stopType': 'MARK'
        }, self.order_builder.build()))

        self.order_builder.clear_stop_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_stop_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_stop_type('MARK')

    def test_stop_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_stop_type('MARK')
        self.assertFalse(has_diff({
            'stopType': 'MARK'
        }, self.order_builder.build()))

    ##########################################################################
    # PriceLinkBasis

    def test_price_link_basis_success(self):
        self.order_builder.set_price_link_basis(PriceLinkBasis.AVERAGE)
        self.assertFalse(has_diff({
            'priceLinkBasis': 'AVERAGE'
        }, self.order_builder.build()))

        self.order_builder.clear_price_link_basis()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_price_link_basis_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_price_link_basis('AVERAGE')

    def test_price_link_basis_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_price_link_basis('AVERAGE')
        self.assertFalse(has_diff({
            'priceLinkBasis': 'AVERAGE'
        }, self.order_builder.build()))

    ##########################################################################
    # PriceLinkType

    def test_price_link_type_success(self):
        self.order_builder.set_price_link_type(PriceLinkType.PERCENT)
        self.assertFalse(has_diff({
            'priceLinkType': 'PERCENT'
        }, self.order_builder.build()))

        self.order_builder.clear_price_link_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_price_link_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_price_link_type('PERCENT')

    def test_price_link_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_price_link_type('PERCENT')
        self.assertFalse(has_diff({
            'priceLinkType': 'PERCENT'
        }, self.order_builder.build()))

    ##########################################################################
    # Price

    def test_price_success(self):
        self.order_builder.set_price(23.49)
        self.assertFalse(has_diff({
            'price': '23.49'
        }, self.order_builder.build()))

        self.order_builder.clear_price()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_price_negative(self):
        self.order_builder.set_price(-1.23)
        self.assertFalse(has_diff({
            'price': '-1.23'
        }, self.order_builder.build()))

    def test_price_zero(self):
        self.order_builder.set_price(0.0)
        self.assertFalse(has_diff({
            'price': '0.00'
        }, self.order_builder.build()))

    def test_price_do_not_round_up(self):
        self.order_builder.set_price(19.9999999)
        self.assertFalse(has_diff({
            'price': '19.99'
        }, self.order_builder.build()))

    def test_price_do_not_round_down(self):
        self.order_builder.set_price(20.00000001)
        self.assertFalse(has_diff({
            'price': '20.00'
        }, self.order_builder.build()))

    ##########################################################################
    # ActivationPrice

    def test_activation_price_success(self):
        self.order_builder.set_activation_price(54.03)
        self.assertFalse(has_diff({
            'activationPrice': 54.03
        }, self.order_builder.build()))

        self.order_builder.clear_activation_price()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_activation_price_negative(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_activation_price(-3.94)

    def test_activation_price_zero(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_activation_price(0.0)

    ##########################################################################
    # SpecialInstruction

    def test_special_instruction_success(self):
        self.order_builder.set_special_instruction(
            SpecialInstruction.DO_NOT_REDUCE)
        self.assertFalse(has_diff({
            'specialInstruction': 'DO_NOT_REDUCE'
        }, self.order_builder.build()))

        self.order_builder.clear_special_instruction()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_special_instruction_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_special_instruction('DO_NOT_REDUCE')

    def test_special_instruction_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_special_instruction('DO_NOT_REDUCE')
        self.assertFalse(has_diff({
            'specialInstruction': 'DO_NOT_REDUCE'
        }, self.order_builder.build()))

    ##########################################################################
    # OrderStrategyType

    def test_order_strategy_type_success(self):
        self.order_builder.set_order_strategy_type(OrderStrategyType.OCO)
        self.assertFalse(has_diff({
            'orderStrategyType': 'OCO'
        }, self.order_builder.build()))

        self.order_builder.clear_order_strategy_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_order_strategy_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_order_strategy_type('OCO')

    def test_order_strategy_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_order_strategy_type('OCO')
        self.assertFalse(has_diff({
            'orderStrategyType': 'OCO'
        }, self.order_builder.build()))

    ##########################################################################
    # ChildOrderStrategies

    def test_add_child_order_strategy_success(self):
        self.order_builder.add_child_order_strategy(
            OrderBuilder().set_session(Session.NORMAL))
        self.assertFalse(has_diff({
            'childOrderStrategies': [{'session': 'NORMAL'}]
        }, self.order_builder.build()))

        self.order_builder.clear_child_order_strategies()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_add_child_order_strategy_dict(self):
        self.order_builder.add_child_order_strategy(
            {'session': 'NORMAL'})
        self.assertFalse(has_diff({
            'childOrderStrategies': [{'session': 'NORMAL'}]
        }, self.order_builder.build()))

    def test_add_child_order_strategy_invalid_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_child_order_strategy(10)

    ##########################################################################
    # OrderLegCollection

    def test_add_order_leg_success(self):
        self.order_builder.add_order_leg(
            instruction=Instruction.BUY,
            instrument=EquityInstrument('GOOG'),
            quantity=10)
        self.order_builder.add_order_leg(
            instruction=Instruction.SELL_TO_CLOSE,
            instrument=OptionInstrument('GOOG01392981343C124323'),
            quantity=1)
        self.assertFalse(has_diff({
            'orderLegCollection': [{
                'instruction': 'BUY',
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY'
                },
                'quantity': 10,
            }, {
                'instruction': 'SELL_TO_CLOSE',
                'instrument': {
                    'symbol': 'GOOG01392981343C124323',
                    'assetType': 'OPTION'
                },
                'quantity': 1,
            }]
        }, self.order_builder.build()))

        self.order_builder.clear_order_legs()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    def test_add_order_leg_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_order_leg(
                instruction='BUY',
                instrument=EquityInstrument('GOOG'),
                quantity=10)

    def test_add_order_leg_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)

        self.order_builder.add_order_leg(
            instruction='BUY',
            instrument=EquityInstrument('GOOG'),
            quantity=10)
        self.order_builder.add_order_leg(
            instruction='SELL_TO_CLOSE',
            instrument=OptionInstrument('GOOG01392981343C124323'),
            quantity=1)

        self.assertFalse(has_diff({
            'orderLegCollection': [{
                'instruction': 'BUY',
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY'
                },
                'quantity': 10,
            }, {
                'instruction': 'SELL_TO_CLOSE',
                'instrument': {
                    'symbol': 'GOOG01392981343C124323',
                    'assetType': 'OPTION'
                },
                'quantity': 1,
            }]
        }, self.order_builder.build()))

    def test_add_order_leg_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_order_leg(
                instruction=Instruction.BUY,
                instrument=EquityInstrument('GOOG'),
                quantity=0)

    def test_add_order_leg_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_order_leg(
                instruction=Instruction.BUY,
                instrument=EquityInstrument('GOOG'),
                quantity=0)


class OrderBuilderExamplesTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    ##########################################################################
    # Functional tests from here:
    # https://developer.tdameritrade.com/content/place-order-samples
    def test_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_quantity(-12)

    def test_quantity_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_quantity('')
        self.assertFalse(has_diff({
            'quantity': ''
        }, self.order_builder.build()))

    '''

    ##########################################################################
    #

    def test__success(self):
        self.order_builder.set_()
        self.assertFalse(has_diff({
            '': ''
        }, self.order_builder.build()))

    def test__wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_('')

    def test__wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_('')
        self.assertFalse(has_diff({
            '': ''
        }, self.order_builder.build()))

    '''


class OrderBuilderExamplesTest(unittest.TestCase):

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
