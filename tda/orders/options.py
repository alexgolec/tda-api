from tda.orders.generic import OrderBuilder


##########################################################################
# Buy to Open

def option_buy_to_open_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    buy-to-open market order.
    '''
    from tda.orders.common import Duration, OptionInstruction, OrderType
    from tda.orders.common import OrderStrategyType, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.MARKET)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_OPEN, symbol, quantity))


def option_buy_to_open_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    buy-to-open limit order.
    '''
    from tda.orders.common import Duration, OptionInstruction, OrderType
    from tda.orders.common import OrderStrategyType, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_OPEN, symbol, quantity)
    )


##########################################################################
# Sell to Open

def option_sell_to_open_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    sell-to-open market order.
    '''
    from tda.orders.common import Duration, OptionInstruction, OrderType
    from tda.orders.common import OrderStrategyType, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.MARKET)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.SELL_TO_OPEN, symbol, quantity))


def option_sell_to_open_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    sell-to-open limit order.
    '''
    from tda.orders.common import Duration, OptionInstruction, OrderType
    from tda.orders.common import OrderStrategyType, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.SELL_TO_OPEN, symbol, quantity)
    )


##########################################################################
# Buy to Close


def option_buy_to_close_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    buy-to-close market order.
    '''
    from tda.orders.common import Duration, OptionInstruction, OrderType
    from tda.orders.common import OrderStrategyType, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.MARKET)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_CLOSE, symbol, quantity))


def option_buy_to_close_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    buy-to-close limit order.
    '''
    from tda.orders.common import Duration, OptionInstruction, OrderType
    from tda.orders.common import OrderStrategyType, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_CLOSE, symbol, quantity)
    )


##########################################################################
# Sell to Close


def option_sell_to_close_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    sell-to-close market order.
    '''
    from tda.orders.common import Duration, OptionInstruction, OrderType
    from tda.orders.common import OrderStrategyType, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.MARKET)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.SELL_TO_CLOSE, symbol, quantity))


def option_sell_to_close_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    sell-to-close limit order.
    '''
    from tda.orders.common import Duration, OptionInstruction, OrderType
    from tda.orders.common import OrderStrategyType, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY)
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.SELL_TO_CLOSE, symbol, quantity)
    )
