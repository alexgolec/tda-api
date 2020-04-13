from enum import Enum


class InvalidOrderException(Exception):
    '''Raised when attempting to build an incomplete order'''
    pass


class Duration(Enum):
    DAY = 'DAY'
    GOOD_TILL_CANCEL = 'GOOD_TILL_CANCEL'
    FILL_OR_KILL = 'FILL_OR_KILL'


class Session(Enum):
    NORMAL = 'NORMAL'
    AM = 'AM'
    PM = 'PM'
    SEAMESS = 'SEAMLESS'


class EquityOrderBuilder:
    '''Helper class to construct equity orders.'''

    def __init__(self, symbol, quantity):
        '''Create an order for the given symbol and quantity. Note all
        unspecified parameters must be set prior to building the order spec.

        :param symbol: Symbol for the order
        :param quantity: Quantity of the order
        '''
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
            raise InvalidOrderException('{} must be set'.format(name))
        return value

    # Instructions
    class Instruction(Enum):
        '''Order instruction'''
        BUY = 'BUY'
        SELL = 'SELL'

    def set_instruction(self, instruction):
        '''Set the order instruction'''
        assert isinstance(instruction, self.Instruction)
        self.instruction = instruction
        return self

    # Order types
    class OrderType(Enum):
        '''Order type'''
        MARKET = 'MARKET'
        LIMIT = 'LIMIT'

    def set_order_type(self, order_type):
        '''Set the order type'''
        assert isinstance(order_type, self.OrderType)
        self.order_type = order_type
        return self

    # Price
    def set_price(self, price):
        '''Set the order price. Must be set for ``LIMIT`` orders.'''
        assert price > 0.0
        self.price = price
        return self

    # Durations
    def set_duration(self, duration):
        '''Set the order duration'''
        assert isinstance(duration, Duration)
        self.duration = duration
        return self

    # Sessions
    def set_session(self, session):
        '''Set the order's session'''
        assert isinstance(session, Session)
        self.session = session
        return self

    def build(self):
        '''Build the order spec.

        :raise InvalidOrderException: if the order is not fully specified
        '''
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
        '''Takes a real object, as might be returned from the TD Ameritrade API,
        and indicates whether this order object matches it. Returns true if the
        given order if the given order *could have* been placed by calling
        :meth:`Client.place_order()<tda.client.Client.place_order>` with this
        order.

        This method may be called on incomplete orders builders (builders whose
        :meth:`build` method would fail if called. In such a case, unset values
        are ignored and have no effect on filtering.'''
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
