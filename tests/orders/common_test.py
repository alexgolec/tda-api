from ..utils import has_diff, no_duplicates
from tda.orders.common import *
from tda.orders.generic import OrderBuilder

import unittest

class MultiOrderTest(unittest.TestCase):

    def test_oco(self):
        self.assertFalse(has_diff({
            'orderStrategyType': 'OCO',
            'childOrderStrategies': [
                {'session': 'NORMAL'},
                {'duration': 'DAY'},
            ]
        }, one_cancels_other(
            OrderBuilder().set_session(Session.NORMAL),
            OrderBuilder().set_duration(Duration.DAY)).build()))

    def test_trigger(self):
        self.assertFalse(has_diff({
            'orderStrategyType': 'TRIGGER',
            'session': 'NORMAL',
            'childOrderStrategies': [
                {'duration': 'DAY'},
            ]
        }, first_triggers_second(
            OrderBuilder().set_session(Session.NORMAL),
            OrderBuilder().set_duration(Duration.DAY)).build()))


