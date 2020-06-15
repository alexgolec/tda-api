from enum import Enum


class __BaseInstrument:
    def __init__(self, asset_type, symbol):
        self._assetType = asset_type
        self._symbol = symbol

    def asset_type(self):
        return self._assetType


class EquityInstrument(__BaseInstrument):
    def __init__(self, symbol):
        super().__init__('EQUITY', symbol)


class OptionInstrument(__BaseInstrument):
    def __init__(self, symbol):
        super().__init__('OPTION', symbol)


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


class OrderType(Enum):
    '''
    Type of equity or option order to place.
    '''
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP = 'STOP'
    STOP_LIMIT = 'STOP_LIMIT'
    TRAILING_STOP = 'TRAILING_STOP'
    MARKET_ON_CLOSE = 'MARKET_ON_CLOSE'
    EXERCISE = 'EXERCISE'
    TRAILING_STOP_LIMIT = 'TRAILING_STOP_LIMIT'
    NET_DEBIT = 'NET_DEBIT'
    NET_CREDIT = 'NET_CREDIT'
    NET_ZERO = 'NET_ZERO'


class ComplexOrderStrategyType(Enum):
    '''
    Explicit order strategies for executing multi-leg options orders. In
    contrast to placing individual orders, which are placed and executed in
    sequence, multi-leg orders are typically executed all at once. This often
    means less market risk and lower transaction costs.
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


class Instruction(Enum):
    '''
    Instructions for opening and closing various equity and option positions.
    See the documentation for each to see which ones can be applied to which
    asset class.
    '''

    #: Open a long equity position
    BUY = 'BUY'

    #: Close a long equity position
    SELL = 'SELL'

    #: Open a short equity position
    SELL_SHORT = 'SELL_SHORT'

    #: Close a short equity position
    BUY_TO_COVER = 'BUY_TO_COVER'

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

    #: Disallow partial orders
    ALL_OR_NONE = 'ALL_OR_NONE'

    #: Do not reduce order size in response to cash dividends
    DO_NOT_REDUCE = 'DO_NOT_REDUCE'

    #: Combination of ``ALL_OR_NONE`` and ``DO_NOT_REDUCE``
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
