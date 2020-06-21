from enum import Enum

from tda.orders.common import InvalidOrderException
from tda.orders.common import InvalidOrderException, Duration, Session


_DEPRECATION_WARNED = False


class EquityOrderBuilder:
    '''Helper class to construct equity orders.'''

    def __init__(self, symbol, quantity):
        '''Create an order for the given symbol and quantity. Note all
        unspecified parameters must be set prior to building the order spec.

        **WARNING:** This class is deprecated in favor of the
        :ref:`tda.orders.generic.OrderBuilder` and the order template helpers.
        It will be removed in a future release.

        :param symbol: Symbol for the order
        :param quantity: Quantity of the order
        '''
        global _DEPRECATION_WARNED
        if not _DEPRECATION_WARNED:
            import sys
            print('WARNING: EquityOrderBuilder has been deprecated. Please ' +
                  'migrate to one of the new order templates or use the ' +
                  'generic OrderBuilder class. You can find documentation on ' +
                  'its replacement heres: https://tda-api.readthedocs.io/en/'+
                  'stable/order-templates.html', file=sys.stderr)
            _DEPRECATION_WARNED = True

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


##########################################################################
# Buy orders


def equity_buy_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    buy market order.
    '''
    from tda.orders.common import Duration, EquityInstruction
    from tda.orders.common import OrderStrategyType, OrderType, Session
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_type(OrderType.MARKET)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.BUY, symbol, quantity))


def equity_buy_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    buy limit order.
    '''
    from tda.orders.common import Duration, EquityInstruction
    from tda.orders.common import OrderStrategyType, OrderType, Session
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.BUY, symbol, quantity))

##########################################################################
# Sell orders


def equity_sell_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    sell market order.
    '''
    from tda.orders.common import Duration, EquityInstruction
    from tda.orders.common import OrderStrategyType, OrderType, Session
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_type(OrderType.MARKET)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.SELL, symbol, quantity))


def equity_sell_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    sell limit order.
    '''
    from tda.orders.common import Duration, EquityInstruction
    from tda.orders.common import OrderStrategyType, OrderType, Session
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.SELL, symbol, quantity))

##########################################################################
# Short sell orders


def equity_sell_short_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    short sell market order.
    '''
    from tda.orders.common import Duration, EquityInstruction
    from tda.orders.common import OrderStrategyType, OrderType, Session
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_type(OrderType.MARKET)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.SELL_SHORT, symbol, quantity))


def equity_sell_short_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    short sell limit order.
    '''
    from tda.orders.common import Duration, EquityInstruction
    from tda.orders.common import OrderStrategyType, OrderType, Session
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.SELL_SHORT, symbol, quantity))

##########################################################################
# Buy to cover orders


def equity_buy_to_cover_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    buy-to-cover market order.
    '''
    from tda.orders.common import Duration, EquityInstruction
    from tda.orders.common import OrderStrategyType, OrderType, Session
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_type(OrderType.MARKET)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.BUY_TO_COVER, symbol, quantity))


def equity_buy_to_cover_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    buy-to-cover limit order.
    '''
    from tda.orders.common import Duration, EquityInstruction
    from tda.orders.common import OrderStrategyType, OrderType, Session
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.BUY_TO_COVER, symbol, quantity))
