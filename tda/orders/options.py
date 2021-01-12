import datetime

from tda.orders.generic import OrderBuilder


def _parse_expiration_date(expiration_date):
    date = None
    try:
        date = datetime.datetime.strptime(expiration_date, '%m%d%y')
        return datetime.date(year=date.year, month=date.month, day=date.day)
    except ValueError:
        pass

    raise ValueError(
        'expiration date must follow format ' +
        '[Month with leading zero][Day with leading zero]' +
        '[two digit year]')


class OptionSymbol:
    '''
    Construct an option symbol from its constituent parts. Options symbols
    have the following format: ``[Underlying]_[Two digit month][Two digit
    day][Two digit year]['P' or 'C'][Strike price]``. Examples include:

     * ``GOOG_012122P620``: GOOG Jan 21 2022 620 Put
     * ``TSLA_112020C1360``: TSLA Nov 20 2020 1360 Call
     * ``SPY_121622C335``: SPY Dec 16 2022 335 Call

    Note while each of the individual parts is validated by itself, the
    option symbol itself may not represent a traded option:

     * Some underlyings do not support options.
     * Not all dates have valid option expiration dates.
     * Not all strike prices are valid options strikes.

    You can use :meth:`~tda.client.Client.get_option_chain` to obtain real
    option symbols for an underlying, as well as extensive data in pricing,
    bid/ask spread, volume, etc.

    :param underlying_symbol: Symbol of the underlying. Not validated.
    :param expiration_date: Expiration date. Accepts ``datetime.date``,
                            ``datetime.datetime``, or strings with the
                            format ``[Two digit month][Two digit day][Two
                            digit year]``.
    :param contract_type: ``P`` for put or ``C`` for call.
    :param strike_price_as_string: Strike price, represented by a string as
                                   you would see at the end of a real option
                                   symbol.
    '''

    def __init__(self, underlying_symbol, expiration_date, contract_type,
                 strike_price_as_string):
        self.underlying_symbol = underlying_symbol

        if contract_type not in ('C', 'P'):
            raise ValueError('Contract type must be one of \'C\' or \'P\'')
        self.contract_type = contract_type

        if isinstance(expiration_date, str):
            self.expiration_date = _parse_expiration_date(expiration_date)
        elif isinstance(expiration_date, datetime.datetime):
            self.expiration_date = datetime.date(
                year=expiration_date.year,
                month=expiration_date.month,
                day=expiration_date.day)
        elif isinstance(expiration_date, datetime.date):
            self.expiration_date = expiration_date
        else:
            raise ValueError(
                'expiration_date must be a string with format %m%d%y ' +
                '(e.g. 01092020) or one of datetime.date or ' +
                'datetime.datetime')

        assert(isinstance(self.expiration_date, datetime.date))

        strike = None
        try:
            strike = float(strike_price_as_string)
        except ValueError:
            pass
        if (strike is None or not isinstance(strike_price_as_string, str)
                or strike <= 0):
            raise ValueError(
                'Strike price must be a string representing a positive ' +
                'float')
        self.strike_price = strike_price_as_string

    @classmethod
    def parse_symbol(cls, symbol):
        '''
        Parse a string option symbol of the for ``[Underlying]_[Two digit month]
        [Two digit day][Two digit year]['P' or 'C'][Strike price]``.
        '''
        format_error_str = (
            'option symbol must have format ' +
            '[Underlying]_[Expiration][P/C][Strike]')

        # Underlying
        try:
            underlying, rest = symbol.split('_')
        except ValueError:
            underlying, rest = None, None
        if underlying is None:
            raise ValueError('option symbol missing underscore \'_\', ' +
                             format_error_str)

        # Expiration
        type_split = rest.split('P')
        if len(type_split) == 2:
            expiration_date, strike = type_split
            contract_type = 'P'
        else:
            type_split = rest.split('C')
            if len(type_split) == 2:
                expiration_date, strike = type_split
                contract_type = 'C'
            else:
                raise ValueError(
                    r'option must have contract type \'C\' r \'\P\', ' +
                    format_error_str)

        expiration_date = _parse_expiration_date(expiration_date)

        return OptionSymbol(underlying, expiration_date, contract_type, strike)

    def build(self):
        '''
        Returns the option symbol represented by this builder.
        '''
        return '{}_{}{}{}'.format(
            self.underlying_symbol,
            self.expiration_date.strftime('%m%d%y'),
            self.contract_type,
            self.strike_price
        )


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

    return (__base_builder()
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
