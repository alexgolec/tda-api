import datetime
import unittest

from tda.orders import EquityOrderBuilder


class EquityOrderBuilderTest(unittest.TestCase):

    def valid_order(self):
        'Returns a valid MARKET order'
        return EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.MARKET) \
            .set_duration(EquityOrderBuilder.Duration.DAY) \
            .set_session(EquityOrderBuilder.Session.NORMAL)

    def test_successful_construction_market(self):
        order = EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.MARKET) \
            .set_duration(EquityOrderBuilder.Duration.DAY) \
            .set_session(EquityOrderBuilder.Session.NORMAL) \
            .build()

        self.assertTrue(('orderType', 'MARKET') in order.items())
        self.assertTrue(('session', 'NORMAL') in order.items())
        self.assertTrue(('duration', 'DAY') in order.items())
        self.assertTrue(
            ('instruction', 'BUY')
            in order['orderLegCollection'][0].items())
        self.assertTrue(
            ('quantity', 10)
            in order['orderLegCollection'][0].items())
        self.assertTrue(
            ('symbol', 'AAPL')
            in order['orderLegCollection'][0]['instrument'].items())

    def test_successful_construction_limit(self):
        order = EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.LIMIT) \
            .set_price(100.5) \
            .set_duration(EquityOrderBuilder.Duration.DAY) \
            .set_session(EquityOrderBuilder.Session.NORMAL) \
            .build()

        self.assertTrue(('orderType', 'LIMIT') in order.items())
        self.assertTrue(('session', 'NORMAL') in order.items())
        self.assertTrue(('duration', 'DAY') in order.items())
        self.assertTrue(('price', 100.5) in order.items())
        self.assertTrue(
            ('instruction', 'BUY')
            in order['orderLegCollection'][0].items())
        self.assertTrue(
            ('quantity', 10)
            in order['orderLegCollection'][0].items())
        self.assertTrue(
            ('symbol', 'AAPL')
            in order['orderLegCollection'][0]['instrument'].items())

    def test_limit_requires_price(self):
        order = EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.LIMIT) \
            .set_duration(EquityOrderBuilder.Duration.DAY) \
            .set_session(EquityOrderBuilder.Session.NORMAL)

        with self.assertRaises(
                EquityOrderBuilder.InvalidOrderException,
                msg='price must be set'):
            order.build()

        order.set_price(100)
        order.build()

    def test_limit_requires_price(self):
        order = EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.LIMIT) \
            .set_duration(EquityOrderBuilder.Duration.DAY) \
            .set_session(EquityOrderBuilder.Session.NORMAL)

        with self.assertRaises(
                EquityOrderBuilder.InvalidOrderException,
                msg='price must be set'):
            order.build()

        order.set_price(100)
        order.build()

    def field_required(self, name):
        order = self.valid_order()
        setattr(order, name, None)
        with self.assertRaises(
                EquityOrderBuilder.InvalidOrderException,
                msg='{} must be set'.format(name)):
            order.build()

    def test_order_type_required(self):
        self.field_required('order_type')

    def test_session_required(self):
        self.field_required('session')

    def test_duration_required(self):
        self.field_required('duration')

    def test_instruction_required(self):
        self.field_required('instruction')

    def real_order(self):
        return {
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderType': 'LIMIT',
            'complexOrderStrategyType': 'NONE',
            'quantity': 1.0,
            'filledQuantity': 1.0,
            'remainingQuantity': 0.0,
            'requestedDestination': 'AUTO',
            'destinationLinkName': 'ETMM',
            'price': 58.41,
            'orderLegCollection': [
                {
                    'orderLegType': 'EQUITY',
                    'legId': 1,
                    'instrument': {
                        'assetType': 'EQUITY',
                        'cusip': '126650100',
                        'symbol': 'CVS'
                    },
                    'instruction': 'BUY',
                    'positionEffect': 'OPENING',
                    'quantity': 1.0
                }
            ],
            'orderStrategyType': 'SINGLE',
            'orderId': 100001,
            'cancelable': False,
            'editable': False,
            'status': 'FILLED',
            'enteredTime': '2020-03-30T15:36:12+0000',
            'closeTime': '2020-03-30T15:36:12+0000',
            'tag': 'API_TDAM:App',
            'accountId': 100000,
            'orderActivityCollection': [
                {
                    'activityType': 'EXECUTION',
                    'executionType': 'FILL',
                    'quantity': 1.0,
                    'orderRemainingQuantity': 0.0,
                    'executionLegs': [
                        {
                            'legId': 1,
                            'quantity': 1.0,
                            'mismarkedQuantity': 0.0,
                            'price': 58.1853,
                            'time': '2020-03-30T15:36:12+0000'
                        }
                    ]
                }
            ]
        }

    def test_match_base(self):
        real_order = self.real_order()
        self.assertTrue(EquityOrderBuilder('CVS', 1).matches(real_order))

    def test_match_order_type(self):
        real_order = self.real_order()
        order = EquityOrderBuilder('CVS', 1) \
            .set_order_type(EquityOrderBuilder.OrderType.LIMIT)
        self.assertTrue(order.matches(real_order))
        order.set_order_type(EquityOrderBuilder.OrderType.MARKET)
        self.assertFalse(order.matches(real_order))

    def test_match_session(self):
        real_order = self.real_order()
        order = EquityOrderBuilder('CVS', 1) \
            .set_session(EquityOrderBuilder.Session.NORMAL)
        self.assertTrue(order.matches(real_order))
        order.set_session(EquityOrderBuilder.Session.AM)
        self.assertFalse(order.matches(real_order))

    def test_match_duration(self):
        real_order = self.real_order()
        order = EquityOrderBuilder('CVS', 1) \
            .set_duration(EquityOrderBuilder.Duration.DAY)
        self.assertTrue(order.matches(real_order))
        order.set_duration(EquityOrderBuilder.Duration.FILL_OR_KILL)
        self.assertFalse(order.matches(real_order))

    def test_match_instruction(self):
        real_order = self.real_order()
        order = EquityOrderBuilder('CVS', 1) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY)
        self.assertTrue(order.matches(real_order))
        order.set_instruction(EquityOrderBuilder.Instruction.SELL)
        self.assertFalse(order.matches(real_order))

    def test_match_symbol(self):
        real_order = self.real_order()
        order = EquityOrderBuilder('CVS', 1)
        self.assertTrue(order.matches(real_order))

        order = EquityOrderBuilder('AAPL', 1)
        self.assertFalse(order.matches(real_order))

    def test_match_quantity(self):
        real_order = self.real_order()
        order = EquityOrderBuilder('CVS', 1)
        self.assertTrue(order.matches(real_order))

        order = EquityOrderBuilder('CVS', 10)
        self.assertFalse(order.matches(real_order))

    def test_match_asset_type(self):
        real_order = self.real_order()
        order = EquityOrderBuilder('CVS', 1)
        self.assertTrue(order.matches(real_order))

        real_order['orderLegCollection'][0]['instrument']['assetType'] = \
            'OPTION'
        self.assertFalse(order.matches(real_order))
