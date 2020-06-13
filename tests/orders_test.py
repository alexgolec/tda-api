import unittest

from tda.orders import Duration, EquityOrderBuilder, InvalidOrderException
from tda.orders import Session
from tests.test_utils import no_duplicates
from . import test_utils


class EquityOrderBuilderTest(unittest.TestCase):

    def valid_order(self):
        'Returns a valid MARKET order'
        return EquityOrderBuilder('AAPL', 10) \
            .set_instruction(EquityOrderBuilder.Instruction.BUY) \
            .set_order_type(EquityOrderBuilder.OrderType.MARKET) \
            .set_duration(Duration.DAY) \
            .set_session(Session.NORMAL)

    @no_duplicates
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

    @no_duplicates
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

    @no_duplicates
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

    @no_duplicates
    def test_order_type_required(self):
        self.field_required('order_type')

    @no_duplicates
    def test_session_required(self):
        self.field_required('session')

    @no_duplicates
    def test_duration_required(self):
        self.field_required('duration')

    @no_duplicates
    def test_instruction_required(self):
        self.field_required('instruction')
