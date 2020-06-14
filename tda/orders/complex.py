from tda.orders.common import InvalidOrderException, Duration, Session


def _build_object(obj):
    ret = {}
    for name, value in vars(obj).items():
        if value is None:
            continue

        name = name[1:]
        ret[name] = value
    return ret

class ComplexOrderBuilder:
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
    def set_session(self):
        pass

    def build(self):
        return _build_object(self)

class BaseInstrument:
    def __init__(self, asset_type, symbol):
        self._assetType = asset_type
        self._symbol = None

class EquityInstrument(BaseInstrument):
    def __init__(self, symbol):
        super().__init__('EQUITY', symbol)

class OptionInstrument(BaseInstrument):
    def __init__(self, symbol):
        super().__init__('OPTION', symbol)
