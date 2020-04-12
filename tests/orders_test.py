import unittest

from tda.orders import Duration, EquityOrderBuilder, InvalidOrderException
from tda.orders import Session
from . import test_utils


class EquityOrderBuilderTest(unittest.TestCase):

    def valid_order(self):
        'Returns a valid MARKET order'
        return EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.MARKET) \
            .set_duration(Duration.DAY) \
            .set_session(Session.NORMAL)

    def test_successful_construction_market(self):
        order = EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.MARKET) \
            .set_duration(Duration.DAY) \
            .set_session(Session.NORMAL) \
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
            .set_duration(Duration.DAY) \
            .set_session(Session.NORMAL) \
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
            .set_duration(Duration.DAY) \
            .set_session(Session.NORMAL)

        with self.assertRaises(
                InvalidOrderException, msg='price must be set'):
            order.build()

        order.set_price(100)
        order.build()

    def test_limit_requires_price(self):
        order = EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.LIMIT) \
            .set_duration(Duration.DAY) \
            .set_session(Session.NORMAL)

        with self.assertRaises(
                InvalidOrderException, msg='price must be set'):
            order.build()

        order.set_price(100)
        order.build()

    def field_required(self, name):
        order = self.valid_order()
        setattr(order, name, None)
        with self.assertRaises(
                InvalidOrderException, msg='{} must be set'.format(name)):
            order.build()

    def test_order_type_required(self):
        self.field_required('order_type')

    def test_session_required(self):
        self.field_required('session')

    def test_duration_required(self):
        self.field_required('duration')

    def test_instruction_required(self):
        self.field_required('instruction')

    def test_match_base(self):
        real_order = test_utils.real_order()
        self.assertTrue(EquityOrderBuilder('CVS', 1).matches(real_order))

    def test_match_order_type(self):
        real_order = test_utils.real_order()
        order = EquityOrderBuilder('CVS', 1) \
            .set_order_type(EquityOrderBuilder.OrderType.MARKET)
        self.assertTrue(order.matches(real_order))
        order.set_order_type(EquityOrderBuilder.OrderType.LIMIT)
        self.assertFalse(order.matches(real_order))

    def test_match_session(self):
        real_order = test_utils.real_order()
        order = EquityOrderBuilder('CVS', 1).set_session(Session.NORMAL)
        self.assertTrue(order.matches(real_order))
        order.set_session(Session.AM)
        self.assertFalse(order.matches(real_order))

    def test_match_duration(self):
        real_order = test_utils.real_order()
        order = EquityOrderBuilder('CVS', 1) \
            .set_duration(Duration.DAY)
        self.assertTrue(order.matches(real_order))
        order.set_duration(Duration.FILL_OR_KILL)
        self.assertFalse(order.matches(real_order))

    def test_match_instruction(self):
        real_order = test_utils.real_order()
        order = EquityOrderBuilder('CVS', 1) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY)
        self.assertTrue(order.matches(real_order))
        order.set_instruction(EquityOrderBuilder.Instruction.SELL)
        self.assertFalse(order.matches(real_order))

    def test_match_symbol(self):
        real_order = test_utils.real_order()
        order = EquityOrderBuilder('CVS', 1)
        self.assertTrue(order.matches(real_order))

        order = EquityOrderBuilder('AAPL', 1)
        self.assertFalse(order.matches(real_order))

    def test_match_quantity(self):
        real_order = test_utils.real_order()
        order = EquityOrderBuilder('CVS', 1)
        self.assertTrue(order.matches(real_order))

        order = EquityOrderBuilder('CVS', 10)
        self.assertFalse(order.matches(real_order))

    def test_match_asset_type(self):
        real_order = test_utils.real_order()
        order = EquityOrderBuilder('CVS', 1)
        self.assertTrue(order.matches(real_order))

        real_order['orderLegCollection'][0]['instrument']['assetType'] = \
            'OPTION'
        self.assertFalse(order.matches(real_order))
