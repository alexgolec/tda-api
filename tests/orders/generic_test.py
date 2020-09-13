import unittest

from tda.orders.generic import *
from tda.orders.common import *
from ..utils import has_diff, no_duplicates


class OrderBuilderTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.order_builder = OrderBuilder()

    ##########################################################################
    # Session

    @no_duplicates
    def test_session_success(self):
        self.order_builder.set_session(Session.NORMAL)
        self.assertFalse(has_diff({
            'session': 'NORMAL'
        }, self.order_builder.build()))

        self.order_builder.clear_session()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_session_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_session('NORMAL')

    @no_duplicates
    def test_session_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_session('NORMAL')
        self.assertFalse(has_diff({
            'session': 'NORMAL'
        }, self.order_builder.build()))

    ##########################################################################
    # Duration

    @no_duplicates
    def test_duration_success(self):
        self.order_builder.set_duration(Duration.DAY)
        self.assertFalse(has_diff({
            'duration': 'DAY'
        }, self.order_builder.build()))

        self.order_builder.clear_duration()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_duration_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_duration('DAY')

    @no_duplicates
    def test_duration_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_duration('DAY')
        self.assertFalse(has_diff({
            'duration': 'DAY'
        }, self.order_builder.build()))

    ##########################################################################
    # OrderType

    @no_duplicates
    def test_order_type_success(self):
        self.order_builder.set_order_type(OrderType.MARKET)
        self.assertFalse(has_diff({
            'orderType': 'MARKET'
        }, self.order_builder.build()))

        self.order_builder.clear_order_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_order_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_order_type('MARKET')

    @no_duplicates
    def test_order_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_order_type('MARKET')
        self.assertFalse(has_diff({
            'orderType': 'MARKET'
        }, self.order_builder.build()))

    ##########################################################################
    # ComplexOrderStrategyType

    @no_duplicates
    def test_complex_order_strategy_type_success(self):
        self.order_builder.set_complex_order_strategy_type(
            ComplexOrderStrategyType.IRON_CONDOR)
        self.assertFalse(has_diff({
            'complexOrderStrategyType': 'IRON_CONDOR'
        }, self.order_builder.build()))

        self.order_builder.clear_complex_order_strategy_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test__wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_complex_order_strategy_type('IRON_CONDOR')

    @no_duplicates
    def test__wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_complex_order_strategy_type('IRON_CONDOR')
        self.assertFalse(has_diff({
            'complexOrderStrategyType': 'IRON_CONDOR'
        }, self.order_builder.build()))

    ##########################################################################
    # Quantity

    @no_duplicates
    def test_quantity_success(self):
        self.order_builder.set_quantity(12)
        self.assertFalse(has_diff({
            'quantity': 12
        }, self.order_builder.build()))

        self.order_builder.clear_quantity()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_quantity(-12)

    @no_duplicates
    def test_quantity_zero(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_quantity(0)

    ##########################################################################
    # RequestedDestination

    @no_duplicates
    def test_requested_destination_success(self):
        self.order_builder.set_requested_destination(Destination.INET)
        self.assertFalse(has_diff({
            'requestedDestination': 'INET'
        }, self.order_builder.build()))

        self.order_builder.clear_requested_destination()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_requested_destination_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_requested_destination('INET')

    @no_duplicates
    def test_requested_destination_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_requested_destination('INET')
        self.assertFalse(has_diff({
            'requestedDestination': 'INET'
        }, self.order_builder.build()))

    ##########################################################################
    # StopPrice

    @no_duplicates
    def test_stop_price_success(self):
        self.order_builder.set_stop_price(42.90)
        self.assertFalse(has_diff({
            'stopPrice': '42.90'
        }, self.order_builder.build()))

        self.order_builder.clear_stop_price()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_stop_price_as_string(self):
        self.order_builder.set_stop_price('invalid')
        self.assertFalse(has_diff({
            'stopPrice': 'invalid'
        }, self.order_builder.build()))

    @no_duplicates
    def test_stop_price_negative(self):
        self.order_builder.set_stop_price(-1.31)
        self.assertFalse(has_diff({
            'stopPrice': '-1.31'
        }, self.order_builder.build()))

    @no_duplicates
    def test_stop_price_zero(self):
        self.order_builder.set_stop_price(0)
        self.assertFalse(has_diff({
            'stopPrice': '0.00'
        }, self.order_builder.build()))

    @no_duplicates
    def test_stop_price_do_not_round_up(self):
        self.order_builder.set_stop_price(1.99999)
        self.assertFalse(has_diff({
            'stopPrice': '1.99'
        }, self.order_builder.build()))

    @no_duplicates
    def test_stop_price_do_round_down(self):
        self.order_builder.set_stop_price(2.00001)
        self.assertFalse(has_diff({
            'stopPrice': '2.00'
        }, self.order_builder.build()))

    ##########################################################################
    # StopPriceLinkBasis

    @no_duplicates
    def test_stop_price_link_basis_success(self):
        self.order_builder.set_stop_price_link_basis(StopPriceLinkBasis.ASK)
        self.assertFalse(has_diff({
            'stopPriceLinkBasis': 'ASK'
        }, self.order_builder.build()))

        self.order_builder.clear_stop_price_link_basis()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_stop_price_link_basis_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_stop_price_link_basis('ASK')

    @no_duplicates
    def test_stop_price_link_basis_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_stop_price_link_basis('ASK')
        self.assertFalse(has_diff({
            'stopPriceLinkBasis': 'ASK'
        }, self.order_builder.build()))

    ##########################################################################
    # StopPriceLinkType

    @no_duplicates
    def test_stop_price_link_type_success(self):
        self.order_builder.set_stop_price_link_type(StopPriceLinkType.VALUE)
        self.assertFalse(has_diff({
            'stopPriceLinkType': 'VALUE'
        }, self.order_builder.build()))

        self.order_builder.clear_stop_price_link_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_stop_price_link_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_stop_price_link_type('VALUE')

    @no_duplicates
    def test_stop_price_link_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_stop_price_link_type('VALUE')
        self.assertFalse(has_diff({
            'stopPriceLinkType': 'VALUE'
        }, self.order_builder.build()))

    ##########################################################################
    # StopPriceOffset

    @no_duplicates
    def test_stop_price_offset_success(self):
        self.order_builder.set_stop_price_offset(12.98)
        self.assertFalse(has_diff({
            'stopPriceOffset': 12.98
        }, self.order_builder.build()))

        self.order_builder.clear_stop_price_offset()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    ##########################################################################
    # StopType

    @no_duplicates
    def test_stop_type_success(self):
        self.order_builder.set_stop_type(StopType.MARK)
        self.assertFalse(has_diff({
            'stopType': 'MARK'
        }, self.order_builder.build()))

        self.order_builder.clear_stop_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_stop_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_stop_type('MARK')

    @no_duplicates
    def test_stop_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_stop_type('MARK')
        self.assertFalse(has_diff({
            'stopType': 'MARK'
        }, self.order_builder.build()))

    ##########################################################################
    # PriceLinkBasis

    @no_duplicates
    def test_price_link_basis_success(self):
        self.order_builder.set_price_link_basis(PriceLinkBasis.AVERAGE)
        self.assertFalse(has_diff({
            'priceLinkBasis': 'AVERAGE'
        }, self.order_builder.build()))

        self.order_builder.clear_price_link_basis()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_price_link_basis_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_price_link_basis('AVERAGE')

    @no_duplicates
    def test_price_link_basis_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_price_link_basis('AVERAGE')
        self.assertFalse(has_diff({
            'priceLinkBasis': 'AVERAGE'
        }, self.order_builder.build()))

    ##########################################################################
    # PriceLinkType

    @no_duplicates
    def test_price_link_type_success(self):
        self.order_builder.set_price_link_type(PriceLinkType.PERCENT)
        self.assertFalse(has_diff({
            'priceLinkType': 'PERCENT'
        }, self.order_builder.build()))

        self.order_builder.clear_price_link_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_price_link_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_price_link_type('PERCENT')

    @no_duplicates
    def test_price_link_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_price_link_type('PERCENT')
        self.assertFalse(has_diff({
            'priceLinkType': 'PERCENT'
        }, self.order_builder.build()))

    ##########################################################################
    # Price

    @no_duplicates
    def test_price_success(self):
        self.order_builder.set_price(23.49)
        self.assertFalse(has_diff({
            'price': '23.49'
        }, self.order_builder.build()))

        self.order_builder.clear_price()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_price_success_as_string(self):
        self.order_builder.set_price('invalid')
        self.assertFalse(has_diff({
            'price': 'invalid'
        }, self.order_builder.build()))

    @no_duplicates
    def test_price_negative(self):
        self.order_builder.set_price(-1.23)
        self.assertFalse(has_diff({
            'price': '-1.23'
        }, self.order_builder.build()))

    @no_duplicates
    def test_price_zero(self):
        self.order_builder.set_price(0.0)
        self.assertFalse(has_diff({
            'price': '0.00'
        }, self.order_builder.build()))

    @no_duplicates
    def test_price_do_not_round_up(self):
        self.order_builder.set_price(19.9999999)
        self.assertFalse(has_diff({
            'price': '19.99'
        }, self.order_builder.build()))

    @no_duplicates
    def test_price_do_not_round_down(self):
        self.order_builder.set_price(20.00000001)
        self.assertFalse(has_diff({
            'price': '20.00'
        }, self.order_builder.build()))

    ##########################################################################
    # ActivationPrice

    @no_duplicates
    def test_activation_price_success(self):
        self.order_builder.set_activation_price(54.03)
        self.assertFalse(has_diff({
            'activationPrice': 54.03
        }, self.order_builder.build()))

        self.order_builder.clear_activation_price()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_activation_price_negative(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_activation_price(-3.94)

    @no_duplicates
    def test_activation_price_zero(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_activation_price(0.0)

    ##########################################################################
    # SpecialInstruction

    @no_duplicates
    def test_special_instruction_success(self):
        self.order_builder.set_special_instruction(
            SpecialInstruction.DO_NOT_REDUCE)
        self.assertFalse(has_diff({
            'specialInstruction': 'DO_NOT_REDUCE'
        }, self.order_builder.build()))

        self.order_builder.clear_special_instruction()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_special_instruction_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_special_instruction('DO_NOT_REDUCE')

    @no_duplicates
    def test_special_instruction_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_special_instruction('DO_NOT_REDUCE')
        self.assertFalse(has_diff({
            'specialInstruction': 'DO_NOT_REDUCE'
        }, self.order_builder.build()))

    ##########################################################################
    # OrderStrategyType

    @no_duplicates
    def test_order_strategy_type_success(self):
        self.order_builder.set_order_strategy_type(OrderStrategyType.OCO)
        self.assertFalse(has_diff({
            'orderStrategyType': 'OCO'
        }, self.order_builder.build()))

        self.order_builder.clear_order_strategy_type()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_order_strategy_type_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_order_strategy_type('OCO')

    @no_duplicates
    def test_order_strategy_type_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_order_strategy_type('OCO')
        self.assertFalse(has_diff({
            'orderStrategyType': 'OCO'
        }, self.order_builder.build()))

    ##########################################################################
    # ChildOrderStrategies

    @no_duplicates
    def test_add_child_order_strategy_success(self):
        self.order_builder.add_child_order_strategy(
            OrderBuilder().set_session(Session.NORMAL))
        self.assertFalse(has_diff({
            'childOrderStrategies': [{'session': 'NORMAL'}]
        }, self.order_builder.build()))

        self.order_builder.clear_child_order_strategies()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_add_child_order_strategy_dict(self):
        self.order_builder.add_child_order_strategy(
            {'session': 'NORMAL'})
        self.assertFalse(has_diff({
            'childOrderStrategies': [{'session': 'NORMAL'}]
        }, self.order_builder.build()))

    @no_duplicates
    def test_add_child_order_strategy_invalid_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_child_order_strategy(10)

    ##########################################################################
    # OrderLegCollection

    @no_duplicates
    def test_add_equity_leg_success(self):
        self.order_builder.add_equity_leg(EquityInstruction.BUY, 'GOOG', 10)
        self.order_builder.add_equity_leg(
            EquityInstruction.SELL_SHORT, 'MSFT', 1)
        self.assertFalse(has_diff({
            'orderLegCollection': [{
                'instruction': 'BUY',
                'instrument': {
                    'symbol': 'GOOG',
                    'assetType': 'EQUITY'
                },
                'quantity': 10,
            }, {
                'instruction': 'SELL_SHORT',
                'instrument': {
                    'symbol': 'MSFT',
                    'assetType': 'EQUITY'
                },
                'quantity': 1,
            }]
        }, self.order_builder.build()))

        self.order_builder.clear_order_legs()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_add_equity_leg_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_equity_leg('BUY', 'GOOG', 10)

    @no_duplicates
    def test_add_equity_leg_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)

        self.order_builder.add_equity_leg('BUY', 'GOOG', 10)
        self.order_builder.add_equity_leg('SELL_TO_CLOSE', 'MSFT', 1)

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
                    'symbol': 'MSFT',
                    'assetType': 'EQUITY'
                },
                'quantity': 1,
            }]
        }, self.order_builder.build()))

    @no_duplicates
    def test_add_equity_leg_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_equity_leg(
                EquityInstruction.BUY, 'GOOG', -1)

    @no_duplicates
    def test_add_equity_leg_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_equity_leg(
                EquityInstruction.BUY, 'GOOG', 0)

    @no_duplicates
    def test_add_option_leg_success(self):
        self.order_builder.add_option_leg(
            OptionInstruction.BUY_TO_OPEN, 'GOOG31433C1342', 10)
        self.order_builder.add_option_leg(
            OptionInstruction.BUY_TO_CLOSE, 'MSFT439132P35', 1)
        self.assertFalse(has_diff({
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'instrument': {
                    'symbol': 'GOOG31433C1342',
                    'assetType': 'OPTION'
                },
                'quantity': 10,
            }, {
                'instruction': 'BUY_TO_CLOSE',
                'instrument': {
                    'symbol': 'MSFT439132P35',
                    'assetType': 'OPTION'
                },
                'quantity': 1,
            }]
        }, self.order_builder.build()))

        self.order_builder.clear_order_legs()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_add_option_leg_wrong_type(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_option_leg(
                'BUY_TO_OPEN', 'GOOG31433C1342', 10)

    @no_duplicates
    def test_add_option_leg_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)

        self.order_builder.add_option_leg('BUY_TO_OPEN', 'GOOG31433C1342', 10)
        self.order_builder.add_option_leg('BUY_TO_CLOSE', 'MSFT439132P35', 1)
        self.assertFalse(has_diff({
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'instrument': {
                    'symbol': 'GOOG31433C1342',
                    'assetType': 'OPTION'
                },
                'quantity': 10,
            }, {
                'instruction': 'BUY_TO_CLOSE',
                'instrument': {
                    'symbol': 'MSFT439132P35',
                    'assetType': 'OPTION'
                },
                'quantity': 1,
            }]
        }, self.order_builder.build()))

        self.order_builder.clear_order_legs()
        self.assertFalse(has_diff({}, self.order_builder.build()))

    @no_duplicates
    def test_add_option_leg_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_option_leg(
                OptionInstruction.BUY_TO_OPEN, 'GOOG31433C1342', -1)

    @no_duplicates
    def test_add_option_leg_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.order_builder.add_option_leg(
                OptionInstruction.BUY_TO_OPEN, 'GOOG31433C1342', 0)


class OrderBuilderExamplesTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    ##########################################################################
    # Functional tests from here:
    # https://developer.tdameritrade.com/content/place-order-samples
    @no_duplicates
    def test_quantity_negative(self):
        with self.assertRaises(ValueError):
            self.order_builder.set_quantity(-12)

    @no_duplicates
    def test_quantity_wrong_type_no_check(self):
        self.order_builder = OrderBuilder(enforce_enums=False)
        self.order_builder.set_quantity('')
        self.assertFalse(has_diff({
            'quantity': ''
        }, self.order_builder.build()))


class OrderBuilderExamplesTest(unittest.TestCase):

    @no_duplicates
    def setUp(self):
        self.maxDiff = None

    ##########################################################################
    # Functional tests from here:
    # https://developer.tdameritrade.com/content/place-order-samples

    @no_duplicates
    def test_buy_market_stock(self):
        builder = (
            OrderBuilder()
            .set_order_type(OrderType.MARKET)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.BUY, 'XYZ', 15))

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

    @no_duplicates
    def test_buy_limit_single_option(self):
        builder = (
            OrderBuilder()
            .set_complex_order_strategy_type(ComplexOrderStrategyType.NONE)
            .set_order_type(OrderType.LIMIT)
            .set_session(Session.NORMAL)
            .set_price(6.45)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_OPEN, 'XYZ_032015C49', 10))

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

    @no_duplicates
    def test_buy_limit_vertical_call_spread(self):
        builder = (
            OrderBuilder()
            .set_order_type(OrderType.NET_DEBIT)
            .set_session(Session.NORMAL)
            .set_price(1.20)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_OPEN, 'XYZ_011516C40', 10)
            .add_option_leg(
                OptionInstruction.SELL_TO_OPEN, 'XYZ_011516C42.5', 10))

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

    @no_duplicates
    def test_custom_option_spread(self):
        builder = (
            OrderBuilder()
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .set_order_type(OrderType.MARKET)
            .add_option_leg(OptionInstruction.SELL_TO_OPEN, 'XYZ_011819P45', 1)
            .add_option_leg(OptionInstruction.BUY_TO_OPEN, 'XYZ_011720P43', 2)
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

    @no_duplicates
    def test_conditional_order_one_triggers_another(self):
        builder = (
            OrderBuilder()
            .set_order_type(OrderType.LIMIT)
            .set_session(Session.NORMAL)
            .set_price(34.97)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.TRIGGER)
            .add_equity_leg(EquityInstruction.BUY, 'XYZ', 10)
            .add_child_order_strategy(
                OrderBuilder()
                .set_order_type(OrderType.LIMIT)
                .set_session(Session.NORMAL)
                .set_price(42.03)
                .set_duration(Duration.DAY)
                .set_order_strategy_type(OrderStrategyType.SINGLE)
                .add_equity_leg(EquityInstruction.SELL, 'XYZ', 10)))

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

    @no_duplicates
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
                .add_equity_leg(EquityInstruction.SELL, 'XYZ', 2)
            )
            .add_child_order_strategy(
                OrderBuilder()
                .set_order_type(OrderType.STOP_LIMIT)
                .set_session(Session.NORMAL)
                .set_price(37.00)
                .set_stop_price(37.03)
                .set_duration(Duration.DAY)
                .set_order_strategy_type(OrderStrategyType.SINGLE)
                .add_equity_leg(EquityInstruction.SELL, 'XYZ', 2)))

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

    @no_duplicates
    def test_conditional_order_one_triggers_a_one_cancels_other(self):
        builder = (
            OrderBuilder()
            .set_order_strategy_type(OrderStrategyType.TRIGGER)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.LIMIT)
            .set_price(14.97)
            .add_equity_leg(EquityInstruction.BUY, 'XYZ', 5)
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
                    .add_equity_leg(EquityInstruction.SELL, 'XYZ', 5))
                .add_child_order_strategy(
                    OrderBuilder()
                    .set_order_strategy_type(OrderStrategyType.SINGLE)
                    .set_session(Session.NORMAL)
                    .set_duration(Duration.GOOD_TILL_CANCEL)
                    .set_order_type(OrderType.STOP)
                    .set_stop_price(11.27)
                    .add_equity_leg(EquityInstruction.SELL, 'XYZ', 5))))

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

    @no_duplicates
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
            .add_equity_leg(EquityInstruction.SELL, 'XYZ', 10))

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


class TruncateFloatTest(unittest.TestCase):

    def test_zero(self):
        self.assertEqual('0.00', truncate_float(0))

    def test_zero_float(self):
        self.assertEqual('0.00', truncate_float(0.0))

    # positive numbers

    def test_integer(self):
        self.assertEqual('12.00', truncate_float(12))

    def test_integer_as_float(self):
        self.assertEqual('12.00', truncate_float(12.0))

    def test_three_digits(self):
        self.assertEqual('12.12', truncate_float(12.123))

    def test_three_digits_truncate_not_round(self):
        self.assertEqual('12.12', truncate_float(12.129))

    def test_less_than_one(self):
        self.assertEqual('0.1212', truncate_float(.12121))

    # same as above, except with negative numbers

    def test_negative_integer(self):
        self.assertEqual('-12.00', truncate_float(-12))

    def test_negative_integer_as_float(self):
        self.assertEqual('-12.00', truncate_float(-12.0))

    def test_negative_three_digits(self):
        self.assertEqual('-12.12', truncate_float(-12.123))

    def test_negative_three_digits_truncate_not_round(self):
        self.assertEqual('-12.12', truncate_float(-12.129))

    def test_negative_less_than_one(self):
        self.assertEqual('-0.1212', truncate_float(-.12121))
