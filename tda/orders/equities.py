from enum import Enum

from tda.orders.common import Duration, EquityInstruction
from tda.utils import EnumEnforcer
from tda.orders.common import (OrderStrategyType, OrderType, Session, StopType,
                               StopPriceLinkType, StopPriceLinkBasis)
from tda.orders.generic import OrderBuilder

enforcer = EnumEnforcer(False)


##########################################################################

STOP_TYPES = ['MARK', 'LAST', 'BID', 'ASK', 'STANDARD']
STOP_PRICE_LINK_BASIS = ['MANUAL', 'BASE', 'TRIGGER', 'LAST', 'BID', 'ASK', 'ASK_BID', 'MARK', 'AVERAGE']
STOP_PRICE_LINK_TYPE = ['VALUE', 'PERCENT', 'TICK']

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


def equity_sell_stop(symbol, quantity, stop_price, stop_type='MARK'):
    """
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    sell stop order
    """

    stop_type = enforcer.convert_enum(stop_type, StopType)
    assert stop_type in STOP_TYPES, f'Stop Type must be one of {STOP_TYPES}'
    
    return (OrderBuilder()
            .set_order_type(OrderType.STOP)
            .set_quantity(int(quantity))
            .set_session(Session.NORMAL)
            .set_stop_price(round(float(stop_price), 2))
            .set_stop_type(stop_type)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.SELL, symbol, quantity))


def equity_sell_stop_limit(symbol, quantity, limit_price, stop_price, 
                           stop_type='MARK'):
    """
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    sell stop limit order
    """

    stop_type = enforcer.convert_enum(stop_type, StopType)
    assert stop_type in STOP_TYPES, f'Stop Type must be one of {STOP_TYPES}'
    
    return (OrderBuilder()
            .set_order_type(OrderType.STOP_LIMIT)
            .set_quantity(int(quantity))
            .set_session(Session.NORMAL)
            .set_price(round(float(limit_price), 2))
            .set_stop_price(round(float(stop_price), 2))
            .set_stop_type(stop_type)
            .set_duration(Duration.DAY)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.SELL, symbol, quantity))


def equity_sell_trailing_stop(symbol, quantity, trail_offset, trail_offset_type='PERCENT',
                              stop_type='MARK', stop_price_link_basis='MARK'):
    """
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    sell trailing stop order
    """
    trail_offset_type = enforcer.convert_enum(trail_offset_type, StopPriceLinkType)
    stop_type = enforcer.convert_enum(stop_type, StopType)
    stop_price_link_basis = enforcer.convert_enum(stop_price_link_basis, StopType)
    
    assert trail_offset_type in STOP_PRICE_LINK_TYPE, \
        f'offset type must be one of {STOP_PRICE_LINK_TYPE}'
    assert stop_type in STOP_TYPES, f'offset type must be one of {STOP_TYPES}'
    assert stop_price_link_basis in STOP_PRICE_LINK_BASIS, \
        f'offset type must be one of {STOP_PRICE_LINK_BASIS}'
    
    if trail_offset_type == 'PERCENT' and (float(trail_offset) < 1 or (float(trail_offset)) > 99):
        raise ValueError('When using percent, trailing offset must be >=1 and <=99')
    
    return (OrderBuilder()
            .set_order_type(OrderType.TRAILING_STOP)
            .set_quantity(int(quantity))
            .set_session(Session.NORMAL)
            .set_stop_type(stop_type)
            .set_duration(Duration.DAY)
            .set_stop_price_offset(round(float(trail_offset), 2))
            .set_stop_price_link_basis(stop_price_link_basis)
            .set_stop_price_link_type(trail_offset_type)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_equity_leg(EquityInstruction.SELL, symbol, quantity))


def equity_sell_trailing_stop_limit(symbol, quantity, trail_offset, limit_price,
                                    trail_offset_type='PERCENT', stop_type='MARK',
                                    stop_price_link_basis='MARK'):
    """
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for an equity
    sell trailing stop limit order
    """
    trail_offset_type = enforcer.convert_enum(trail_offset_type, StopPriceLinkType)
    stop_type = enforcer.convert_enum(stop_type, StopType)
    stop_price_link_basis = enforcer.convert_enum(stop_price_link_basis, StopType)

    assert trail_offset_type in STOP_PRICE_LINK_TYPE, \
        f'offset type must be one of {STOP_PRICE_LINK_TYPE}'
    assert stop_type in STOP_TYPES, f'offset type must be one of {STOP_TYPES}'
    assert stop_price_link_basis in STOP_PRICE_LINK_BASIS,\
        f'offset type must be one of {STOP_PRICE_LINK_BASIS}'

    if trail_offset_type == 'PERCENT' and (float(trail_offset) < 1 or float(trail_offset) > 99):
        raise ValueError('When using percent, trailing offset must be >=1 and <=99')

    return (OrderBuilder()
            .set_order_type(OrderType.TRAILING_STOP)
            .set_quantity(int(quantity))
            .set_price(round(float(limit_price), 2))
            .set_session(Session.NORMAL)
            .set_stop_type(stop_type)
            .set_duration(Duration.DAY)
            .set_stop_price_offset(round(float(trail_offset), 2))
            .set_stop_price_link_basis(stop_price_link_basis)
            .set_stop_price_link_type(trail_offset_type)
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
