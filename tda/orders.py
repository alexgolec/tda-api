from enum import Enum


class EquityOrderBuilder:
    'Helper class to construct equity orders.'

    class InvalidOrderException(Exception):
        pass

    def __init__(self, symbol, quantity):
        self.symbol = symbol
        self.quantity = quantity

        self.instruction = None
        self.order_type = None
        self.price = None
        self.duration = None
        self.session = None

    def __assert_set(self, name):
        value = getattr(self, name)
        if value is None:
            raise self.InvalidOrderException('{} must be set'.format(name))
        return value

    # Instructions
    class Instruction(Enum):
        BUY = 'BUY'
        SELL = 'SELL'

    def set_instruction(self, instruction):
        assert isinstance(instruction, self.Instruction)
        self.instruction = instruction
        return self

    # Order types
    class OrderType(Enum):
        MARKET = 'MARKET'
        LIMIT = 'LIMIT'

    def set_order_type(self, order_type):
        assert isinstance(order_type, self.OrderType)
        self.order_type = order_type
        return self

    # Price
    def set_price(self, price):
        assert price > 0.0
        self.price = price
        return self

    # Durations
    class Duration(Enum):
        DAY = 'DAY'
        GOOD_TILL_CANCEL = 'GOOD_TILL_CANCEL'
        FILL_OR_KILL = 'FILL_OR_KILL'

    def set_duration(self, duration):
        assert isinstance(duration, self.Duration)
        self.duration = duration
        return self

    # Sessions
    class Session(Enum):
        NORMAL = 'NORMAL'
        AM = 'AM'
        PM = 'PM'
        SEAMESS = 'SEAMLESS'

    def set_session(self, session):
        assert isinstance(session, self.Session)
        self.session = session
        return self

    def build(self):
        spec = {
            'orderType': self.__assert_set('order_type').value,
            'session': self.__assert_set('session').value,
            'duration': self.__assert_set('duration').value,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': self.__assert_set('instruction').value,
                'quantity': self.quantity,
                'instrument': {
                    'symbol': self.symbol,
                    'assetType': 'EQUITY'}
            }]
        }

        if self.order_type == self.OrderType.LIMIT:
            spec['price'] = self.__assert_set('price')
        else:
            assert self.price is None

        return spec

    def matches(self, order):
        '''Returns whether this order matches the given order, based on the set
        fields of this order. Unset fields are ignored.'''
        def matches_path(value, obj, path):
            if value is None:
                return True

            if isinstance(value, Enum):
                value = value.value

            for key in path:
                obj = obj[key]
            return value == obj

        return (matches_path(self.order_type, order, ('orderType',))
                and matches_path(self.session, order, ('session',))
                and matches_path(self.duration, order, ('duration',))
                and matches_path(
                    self.instruction, order,
                    ('orderLegCollection', 0, 'instruction'))
                and matches_path(
                    self.symbol, order,
                    ('orderLegCollection', 0, 'instrument', 'symbol'))
                and matches_path(
                    self.quantity, order,
                    ('orderLegCollection', 0, 'quantity'))
                and matches_path(
                    'EQUITY', order,
                    ('orderLegCollection', 0, 'instrument', 'assetType')))
