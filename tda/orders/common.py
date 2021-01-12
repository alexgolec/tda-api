from enum import Enum


class __BaseInstrument:
    def __init__(self, asset_type, symbol):
        self._assetType = asset_type
        self._symbol = symbol


class EquityInstrument(__BaseInstrument):
    '''Represents an equity when creating order legs.'''

    def __init__(self, symbol):
        super().__init__('EQUITY', symbol)


class OptionInstrument(__BaseInstrument):
    '''Represents an option when creating order legs.'''

    def __init__(self, symbol):
        super().__init__('OPTION', symbol)


class InvalidOrderException(Exception):
    '''Raised when attempting to build an incomplete order'''
    pass


class Duration(Enum):
    '''
    Length of time over which the trade will be active.
    '''
    #: Cancel the trade at the end of the trading day. Note if the order cannot
    #: be filled all at once, you may see partial executions throughout the day.
    DAY = 'DAY'

    # TODO: Implement order cancellation date

    #: Keep the trade open for six months, or until the end of the cancel date,
    #: whichever is shorter. Note if the order cannot be filled all at once, you
    #: may see partial executions over the lifetime of the order.
    GOOD_TILL_CANCEL = 'GOOD_TILL_CANCEL'

    #: Either execute the order immediately at the specified price, or cancel it
    #: immediately.
    FILL_OR_KILL = 'FILL_OR_KILL'


class Session(Enum):
    '''
    The market session during which the order trade should be executed.
    '''

    #: Normal market hours, from 9:30am to 4:00pm Eastern.
    NORMAL = 'NORMAL'

    #: Premarket session, from 8:00am to 9:30am Eastern.
    AM = 'AM'

    #: After-market session, from 4:00pm to 8:00pm Eastern.
    PM = 'PM'

    #: Orders are active during all trading sessions except the overnight
    #: session. This is the union of ``NORMAL``, ``AM``, and ``PM``.
    SEAMLESS = 'SEAMLESS'


class OrderType(Enum):
    '''
    Type of equity or option order to place.
    '''

    #: Execute the order immediately at the best-available price.
    #: `More Info <https://www.investopedia.com/terms/m/marketorder.asp>`__.
    MARKET = 'MARKET'

    #: Execute the order at your price or better.
    #: `More info <https://www.investopedia.com/terms/l/limitorder.asp>`__.
    LIMIT = 'LIMIT'

    #: Wait until the price reaches the stop price, and then immediately place a
    #: market order.
    #: `More Info <https://www.investopedia.com/terms/l/limitorder.asp>`__.
    STOP = 'STOP'

    #: Wait until the price reaches the stop price, and then immediately place a
    #: limit order at the specified price. `More Info
    #: <https://www.investopedia.com/terms/s/stop-limitorder.asp>`__.
    STOP_LIMIT = 'STOP_LIMIT'

    #: Similar to ``STOP``, except if the price moves in your favor, the stop
    #: price is adjusted in that direction. Places a market order if the stop
    #: condition is met.
    #: `More info <https://www.investopedia.com/terms/t/trailingstop.asp>`__.
    TRAILING_STOP = 'TRAILING_STOP'

    #: Similar to ``STOP_LIMIT``, except if the price moves in your favor, the
    #: stop price is adjusted in that direction. Places a limit order at the
    #: specified price if the stop condition is met.
    #: `More info <https://www.investopedia.com/terms/t/trailingstop.asp>`__.
    TRAILING_STOP_LIMIT = 'TRAILING_STOP_LIMIT'

    #: Place the order at the closing price immediately upon market close.
    #: `More info <https://www.investopedia.com/terms/m/marketonclose.asp>`__
    MARKET_ON_CLOSE = 'MARKET_ON_CLOSE'

    #: Exercise an option.
    EXERCISE = 'EXERCISE'

    #: Place an order for an options spread resulting in a net debit.
    #: `More info <https://www.investopedia.com/ask/answers/042215/
    #: whats-difference-between-credit-spread-and-debt-spread.asp>`__
    NET_DEBIT = 'NET_DEBIT'

    #: Place an order for an options spread resulting in a net credit.
    #: `More info <https://www.investopedia.com/ask/answers/042215/
    #: whats-difference-between-credit-spread-and-debt-spread.asp>`__
    NET_CREDIT = 'NET_CREDIT'

    #: Place an order for an options spread resulting in neither a credit nor a
    #: debit.
    #: `More info <https://www.investopedia.com/ask/answers/042215/
    #: whats-difference-between-credit-spread-and-debt-spread.asp>`__
    NET_ZERO = 'NET_ZERO'


class ComplexOrderStrategyType(Enum):
    '''
    Explicit order strategies for executing multi-leg options orders.
    '''

    #: No complex order strategy. This is the default.
    NONE = 'NONE'

    #: `Covered call <https://tickertape.tdameritrade.com/trading/
    #: selling-covered-call-options-strategy-income-hedging-15135>`__
    COVERED = 'COVERED'

    #: `Vertical spread <https://tickertape.tdameritrade.com/trading/
    #: vertical-credit-spreads-high-probability-15846>`__
    VERTICAL = 'VERTICAL'

    #: `Ratio backspread <https://tickertape.tdameritrade.com/trading/
    #: pricey-stocks-ratio-spreads-15306>`__
    BACK_RATIO = 'BACK_RATIO'

    #: `Calendar spread <https://tickertape.tdameritrade.com/trading/
    #: calendar-spreads-trading-primer-15095>`__
    CALENDAR = 'CALENDAR'

    #: `Diagonal spread <https://tickertape.tdameritrade.com/trading/
    #: love-your-diagonal-spread-15030>`__
    DIAGONAL = 'DIAGONAL'

    #: `Straddle spread <https://tickertape.tdameritrade.com/trading/
    #: straddle-strangle-option-volatility-16208>`__
    STRADDLE = 'STRADDLE'

    #: `Strandle spread <https://tickertape.tdameritrade.com/trading/
    #: straddle-strangle-option-volatility-16208>`__
    STRANGLE = 'STRANGLE'

    COLLAR_SYNTHETIC = 'COLLAR_SYNTHETIC'

    #: `Butterfly spread <https://tickertape.tdameritrade.com/trading/
    #: butterfly-spread-options-15976>`__
    BUTTERFLY = 'BUTTERFLY'

    #: `Condor spread <https://www.investopedia.com/terms/c/
    #: condorspread.asp>`__
    CONDOR = 'CONDOR'

    #: `Iron condor spread <https://tickertape.tdameritrade.com/trading/
    #: iron-condor-options-spread-your-trading-wings-15948>`__
    IRON_CONDOR = 'IRON_CONDOR'

    #: `Roll a vertical spread <https://tickertape.tdameritrade.com/trading/
    #: exit-winning-losing-trades-16685>`__
    VERTICAL_ROLL = 'VERTICAL_ROLL'

    #: `Collar strategy <https://tickertape.tdameritrade.com/trading/
    #: stock-hedge-options-collars-15529>`__
    COLLAR_WITH_STOCK = 'COLLAR_WITH_STOCK'

    #: `Double diagonal spread <https://optionstradingiq.com/
    #: the-ultimate-guide-to-double-diagonal-spreads/>`__
    DOUBLE_DIAGONAL = 'DOUBLE_DIAGONAL'

    #: `Unbalanced butterfy spread  <https://tickertape.tdameritrade.com/
    #: trading/unbalanced-butterfly-strong-directional-bias-15913>`__
    UNBALANCED_BUTTERFLY = 'UNBALANCED_BUTTERFLY'
    UNBALANCED_CONDOR = 'UNBALANCED_CONDOR'
    UNBALANCED_IRON_CONDOR = 'UNBALANCED_IRON_CONDOR'
    UNBALANCED_VERTICAL_ROLL = 'UNBALANCED_VERTICAL_ROLL'

    #: A custom multi-leg order strategy.
    CUSTOM = 'CUSTOM'


class Destination(Enum):
    '''
    Destinations for when you want to request a specific destination for your
    order.
    '''

    INET = 'INET'
    ECN_ARCA = 'ECN_ARCA'
    CBOE = 'CBOE'
    AMEX = 'AMEX'
    PHLX = 'PHLX'
    ISE = 'ISE'
    BOX = 'BOX'
    NYSE = 'NYSE'
    NASDAQ = 'NASDAQ'
    BATS = 'BATS'
    C2 = 'C2'
    AUTO = 'AUTO'


class StopPriceLinkBasis(Enum):
    MANUAL = 'MANUAL'
    BASE = 'BASE'
    TRIGGER = 'TRIGGER'
    LAST = 'LAST'
    BID = 'BID'
    ASK = 'ASK'
    ASK_BID = 'ASK_BID'
    MARK = 'MARK'
    AVERAGE = 'AVERAGE'


class StopPriceLinkType(Enum):
    VALUE = 'VALUE'
    PERCENT = 'PERCENT'
    TICK = 'TICK'


class StopType(Enum):
    STANDARD = 'STANDARD'
    BID = 'BID'
    ASK = 'ASK'
    LAST = 'LAST'
    MARK = 'MARK'


class PriceLinkBasis(Enum):
    MANUAL = 'MANUAL'
    BASE = 'BASE'
    TRIGGER = 'TRIGGER'
    LAST = 'LAST'
    BID = 'BID'
    ASK = 'ASK'
    ASK_BID = 'ASK_BID'
    MARK = 'MARK'
    AVERAGE = 'AVERAGE'


class PriceLinkType(Enum):
    VALUE = 'VALUE'
    PERCENT = 'PERCENT'
    TICK = 'TICK'


class EquityInstruction(Enum):
    '''
    Instructions for opening and closing equity positions.
    '''

    #: Open a long equity position
    BUY = 'BUY'

    #: Close a long equity position
    SELL = 'SELL'

    #: Open a short equity position
    SELL_SHORT = 'SELL_SHORT'

    #: Close a short equity position
    BUY_TO_COVER = 'BUY_TO_COVER'


class OptionInstruction(Enum):
    '''
    Instructions for opening and closing options positions.
    '''
    #: Enter a new long option position
    BUY_TO_OPEN = 'BUY_TO_OPEN'

    #: Exit an existing long option position
    SELL_TO_CLOSE = 'SELL_TO_CLOSE'

    #: Enter a short position in an option
    SELL_TO_OPEN = 'SELL_TO_OPEN'

    #: Exit an existing short position in an option
    BUY_TO_CLOSE = 'BUY_TO_CLOSE'


class SpecialInstruction(Enum):
    '''
    Special instruction for trades.
    '''

    #: Disallow partial order execution.
    #: `More info <https://www.investopedia.com/terms/a/aon.asp>`__.
    ALL_OR_NONE = 'ALL_OR_NONE'

    #: Do not reduce order size in response to cash dividends.
    #: `More info <https://www.investopedia.com/terms/d/dnr.asp>`__.
    DO_NOT_REDUCE = 'DO_NOT_REDUCE'

    #: Combination of ``ALL_OR_NONE`` and ``DO_NOT_REDUCE``.
    ALL_OR_NONE_DO_NOT_REDUCE = 'ALL_OR_NONE_DO_NOT_REDUCE'


class OrderStrategyType(Enum):
    '''
    Rules for composite orders.
    '''

    #: No chaining, only a single order is submitted
    SINGLE = 'SINGLE'

    #: Execution of one order cancels the other
    OCO = 'OCO'

    #: Execution of one order triggers placement of the other
    TRIGGER = 'TRIGGER'


def one_cancels_other(order1, order2):
    '''
    If one of the orders is executed, immediately cancel the other.
    '''
    from tda.orders.generic import OrderBuilder

    return (OrderBuilder()
            .set_order_strategy_type(OrderStrategyType.OCO)
            .add_child_order_strategy(order1)
            .add_child_order_strategy(order2))


def first_triggers_second(first_order, second_order):
    '''
    If ``first_order`` is executed, immediately place ``second_order``.
    '''
    from tda.orders.generic import OrderBuilder

    return (first_order
            .set_order_strategy_type(OrderStrategyType.TRIGGER)
            .add_child_order_strategy(second_order))
