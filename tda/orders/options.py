from tda.orders.generic import OrderBuilder


def __base_builder():
    from tda.orders.common import Duration, Session

    return (OrderBuilder()
            .set_session(Session.NORMAL)
            .set_duration(Duration.DAY))


################################################################################
# Single options

# Buy to Open

def option_buy_to_open_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    buy-to-open market order.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.MARKET)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_OPEN, symbol, quantity))


def option_buy_to_open_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    buy-to-open limit order.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_OPEN, symbol, quantity)
    )


# Sell to Open

def option_sell_to_open_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    sell-to-open market order.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.MARKET)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.SELL_TO_OPEN, symbol, quantity))


def option_sell_to_open_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    sell-to-open limit order.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.SELL_TO_OPEN, symbol, quantity)
    )


# Buy to Close


def option_buy_to_close_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    buy-to-close market order.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.MARKET)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_CLOSE, symbol, quantity))


def option_buy_to_close_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    buy-to-close limit order.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType

    return (__base_builder
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.BUY_TO_CLOSE, symbol, quantity)
    )


# Sell to Close


def option_sell_to_close_market(symbol, quantity):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    sell-to-close market order.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.MARKET)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.SELL_TO_CLOSE, symbol, quantity))


def option_sell_to_close_limit(symbol, quantity, price):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` for a
    sell-to-close limit order.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.LIMIT)
            .set_price(price)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(OptionInstruction.SELL_TO_CLOSE, symbol, quantity)
    )


################################################################################
# Verticals

# Bull Call

def bull_call_vertical_open(
        long_call_symbol, short_call_symbol, quantity, net_debit):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` that opens a 
    bull call vertical position. See :ref:`vertical_spreads` for details.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType
    from tda.orders.common import ComplexOrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.NET_DEBIT)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.VERTICAL)
            .set_price(net_debit)
            .set_quantity(quantity)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(
                OptionInstruction.BUY_TO_OPEN, long_call_symbol, quantity)
            .add_option_leg(
                OptionInstruction.SELL_TO_OPEN, short_call_symbol, quantity))

def bull_call_vertical_close(
        long_call_symbol, short_call_symbol, quantity, net_credit):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` that closes a
    bull call vertical position. See :ref:`vertical_spreads` for details.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType
    from tda.orders.common import ComplexOrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.NET_CREDIT)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.VERTICAL)
            .set_price(net_credit)
            .set_quantity(quantity)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(
                OptionInstruction.SELL_TO_CLOSE, long_call_symbol, quantity)
            .add_option_leg(
                OptionInstruction.BUY_TO_CLOSE, short_call_symbol, quantity))


# Bear Call

def bear_call_vertical_open(
        short_call_symbol, long_call_symbol, quantity, net_credit):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` that opens a
    bear call vertical position. See :ref:`vertical_spreads` for details.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType
    from tda.orders.common import ComplexOrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.NET_CREDIT)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.VERTICAL)
            .set_price(net_credit)
            .set_quantity(quantity)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(
                OptionInstruction.SELL_TO_OPEN, short_call_symbol, quantity)
            .add_option_leg(
                OptionInstruction.BUY_TO_OPEN, long_call_symbol, quantity))

def bear_call_vertical_close(
        short_call_symbol, long_call_symbol, quantity, net_debit):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` that closes a
    bear call vertical position. See :ref:`vertical_spreads` for details.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType
    from tda.orders.common import ComplexOrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.NET_DEBIT)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.VERTICAL)
            .set_price(net_debit)
            .set_quantity(quantity)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(
                OptionInstruction.BUY_TO_CLOSE, short_call_symbol, quantity)
            .add_option_leg(
                OptionInstruction.SELL_TO_CLOSE, long_call_symbol, quantity))


# Bull Put

def bull_put_vertical_open(
        long_put_symbol, short_put_symbol, quantity, net_credit):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` that opens a
    bull put vertical position. See :ref:`vertical_spreads` for details.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType
    from tda.orders.common import ComplexOrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.NET_CREDIT)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.VERTICAL)
            .set_price(net_credit)
            .set_quantity(quantity)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(
                OptionInstruction.BUY_TO_OPEN, long_put_symbol, quantity)
            .add_option_leg(
                OptionInstruction.SELL_TO_OPEN, short_put_symbol, quantity))

def bull_put_vertical_close(
        long_put_symbol, short_put_symbol, quantity, net_debit):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` that closes a
    bull put vertical position. See :ref:`vertical_spreads` for details.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType
    from tda.orders.common import ComplexOrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.NET_DEBIT)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.VERTICAL)
            .set_price(net_debit)
            .set_quantity(quantity)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(
                OptionInstruction.SELL_TO_CLOSE, long_put_symbol, quantity)
            .add_option_leg(
                OptionInstruction.BUY_TO_CLOSE, short_put_symbol, quantity))


# Bear Pull

def bear_put_vertical_open(
        short_put_symbol, long_put_symbol, quantity, net_debit):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` that opens a
    bear put vertical position. See :ref:`vertical_spreads` for details.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType
    from tda.orders.common import ComplexOrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.NET_DEBIT)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.VERTICAL)
            .set_price(net_debit)
            .set_quantity(quantity)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(
                OptionInstruction.SELL_TO_OPEN, short_put_symbol, quantity)
            .add_option_leg(
                OptionInstruction.BUY_TO_OPEN, long_put_symbol, quantity))

def bear_put_vertical_close(
        short_put_symbol, long_put_symbol, quantity, net_credit):
    '''
    Returns a pre-filled :class:`~tda.orders.generic.OrderBuilder` that closes a
    bear put vertical position. See :ref:`vertical_spreads` for details.
    '''
    from tda.orders.common import OptionInstruction, OrderType, OrderStrategyType
    from tda.orders.common import ComplexOrderStrategyType

    return (__base_builder()
            .set_order_type(OrderType.NET_CREDIT)
            .set_complex_order_strategy_type(ComplexOrderStrategyType.VERTICAL)
            .set_price(net_credit)
            .set_quantity(quantity)
            .set_order_strategy_type(OrderStrategyType.SINGLE)
            .add_option_leg(
                OptionInstruction.BUY_TO_CLOSE, short_put_symbol, quantity)
            .add_option_leg(
                OptionInstruction.SELL_TO_CLOSE, long_put_symbol, quantity))
