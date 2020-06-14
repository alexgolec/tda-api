from enum import Enum

from tda.orders.common import InvalidOrderException, Duration, Session


def _build_object(obj):
    # Literals are passed straight through
    if isinstance(obj, str) or isinstance(obj, int) or isinstance(obj, float):
        return obj

    # Enums are turned into their values
    elif isinstance(obj, Enum):
        return obj.value

    # Dicts and lists are iterated over, with keys intact
    elif isinstance(obj, dict):
        return dict((key, _build_object(value)) for key, value in obj.items())
    elif isinstance(obj, list):
        return [_build_object(i) for i in obj]

    # Objects have their variables translated into keys
    else:
        ret = {}
        for name, value in vars(obj).items():
            if value is None:
                continue

            name = name[1:]
            ret[name] = _build_object(value)
        return ret


class _BaseInstrument:
    def __init__(self, asset_type, symbol):
        self._assetType = asset_type
        self._symbol = symbol

    def asset_type(self):
        return self._assetType


class EquityInstrument(_BaseInstrument):
    def __init__(self, symbol):
        super().__init__('EQUITY', symbol)


class OptionInstrument(_BaseInstrument):
    def __init__(self, symbol):
        super().__init__('OPTION', symbol)


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


class OrderBuilder:
    '''
    Helper class to create arbitrarily complex orders. Note this class simply
    implements the order schema defined in the `documentation
    <https://developer.tdameritrade.com/account-access/apis/post/accounts/
    %7BaccountId%7D/orders-0>`__, with no attempts to validate the result.
    Orders created using this class may be rejected or may never fill. Use at
    your own risk.
    '''

    def __init__(self):
        self._session = None
        self._duration = None
        self._orderType = None
        self._complexOrderStrategyType = None
        self._quantity = None
        self._requestedDestination = None
        self._stopPrice = None
        self._stopPriceLinkBasis = None
        self._stopPriceLinkType = None
        self._stopPriceOffset = None
        self._stopType = None
        self._priceLinkBasis = None
        self._priceLinkType = None
        self._price = None
        self._orderLegCollection = None
        self._activationPrice = None
        self._specialInstruction = None
        self._orderStrategyType = None
        self._childOrderStrategies = None

    class OrderLegCollection:
        def __init__(self):
            self._orderLegType = None
            self._legId = None
            self._instrument = None
            self._instruction = None
            self._quantity = None
            self._quantityType = None

    # Session
    def set_session(self, session):
        assert isinstance(session, Session)
        self._session = session
        return self

    # Duration
    def set_duration(self, duration):
        assert isinstance(duration, Duration)
        self._duration = duration
        return self

    # OrderType
    def set_order_type(self, order_type):
        assert isinstance(order_type, OrderType)
        self._orderType = order_type
        return self

    # ComplexOrderStrategyType
    def set_complex_order_strategy_type(self, complex_order_strategy_type):
        assert isinstance(
            complex_order_strategy_type, ComplexOrderStrategyType)
        self._complexOrderStrategyType = complex_order_strategy_type
        return self

    # Quantity
    def set_quantity(self, quantity):
        assert quantity > 0
        self._quantity = quantity
        return self

    # RequestedDestination
    def set_requested_destination(self, requested_destination):
        assert isinstance(requested_destination, Destination)
        self._requestedDestination = requested_destination
        return self

    # StopPrice
    def set_stop_price(self, stop_price):
        self._stopPrice = '{:.2f}'.format(stop_price)
        return self

    # StopPriceLinkBasis
    def set_stop_price_link_basis(self, stop_price_link_basis):
        assert isinstance(stop_price_link_basis, StopPriceLinkBasis)
        self._stopPriceLinkBasis = stop_price_link_basis
        return self

    # StopPriceLinkType
    def set_stop_price_link_type(self, stop_price_link_type):
        assert isinstance(stop_price_link_type, StopPriceLinkType)
        self._stopPriceLinkType = stop_price_link_type
        return self

    # StopPriceOffset
    def set_stop_price_offset(self, stop_price_offset):
        self._stopPriceOffset = stop_price_offset
        return self

    # StopType
    def set_stop_type(self, stop_type):
        assert isinstance(stop_type, StopType)
        self._stopType = stop_type
        return self

    # PriceLinkBasis
    def set_price_link_basis(self, price_link_basis):
        assert isinstance(price_link_basis, PriceLinkBasis)
        self._priceLinkBasis = price_link_basis
        return self

    # PriceLinkType
    def set_price_link_type(self, price_link_type):
        assert isinstance(price_link_type, PriceLinkType)
        self._priceLinkType = price_link_type
        return self

    # Price
    def set_price(self, price):
        assert price > 0.0
        self._price = '{:.2f}'.format(price)
        return self

    # OrderLegCollection
    def add_order_leg(self, instruction, instrument, quantity):
        assert quantity > 0

        if self._orderLegCollection is None:
            self._orderLegCollection = []
        self._orderLegCollection.append({
            'instruction': instruction,
            'instrument': instrument,
            'quantity': quantity,
        })
        return self

    # ActivationPrice
    def set_activation_price(self, activation_price):
        assert activation_price >= 0.0
        self._activationPrice = activation_price
        return self

    # SpecialInstruction
    def set_special_instruction(self, special_instruction):
        assert isinstance(special_instruction, SpecialInstruction)
        self._specialInstruction = special_instruction
        return self

    # OrderStrategyType
    def set_order_strategy_type(self, order_strategy_type):
        assert isinstance(order_strategy_type, OrderStrategyType)
        self._orderStrategyType = order_strategy_type
        return self

    # ChildOrderStrategies
    def add_child_order_strategy(self, child_order_strategy):
        if self._childOrderStrategies is None:
            self._childOrderStrategies = []
        self._childOrderStrategies.append(child_order_strategy)
        return self

    def build(self):
        return _build_object(self)
