from enum import Enum

from tda.orders import common


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
        assert isinstance(session, common.Session)
        self._session = session
        return self

    # Duration
    def set_duration(self, duration):
        assert isinstance(duration, common.Duration)
        self._duration = duration
        return self

    # OrderType
    def set_order_type(self, order_type):
        assert isinstance(order_type, common.OrderType)
        self._orderType = order_type
        return self

    # ComplexOrderStrategyType
    def set_complex_order_strategy_type(self, complex_order_strategy_type):
        assert isinstance(
            complex_order_strategy_type, common.ComplexOrderStrategyType)
        self._complexOrderStrategyType = complex_order_strategy_type
        return self

    # Quantity
    def set_quantity(self, quantity):
        assert quantity > 0
        self._quantity = quantity
        return self

    # RequestedDestination
    def set_requested_destination(self, requested_destination):
        assert isinstance(requested_destination, common.Destination)
        self._requestedDestination = requested_destination
        return self

    # StopPrice
    def set_stop_price(self, stop_price):
        self._stopPrice = '{:.2f}'.format(stop_price)
        return self

    # StopPriceLinkBasis
    def set_stop_price_link_basis(self, stop_price_link_basis):
        assert isinstance(stop_price_link_basis, common.StopPriceLinkBasis)
        self._stopPriceLinkBasis = stop_price_link_basis
        return self

    # StopPriceLinkType
    def set_stop_price_link_type(self, stop_price_link_type):
        assert isinstance(stop_price_link_type, common.StopPriceLinkType)
        self._stopPriceLinkType = stop_price_link_type
        return self

    # StopPriceOffset
    def set_stop_price_offset(self, stop_price_offset):
        self._stopPriceOffset = stop_price_offset
        return self

    # StopType
    def set_stop_type(self, stop_type):
        assert isinstance(stop_type, common.StopType)
        self._stopType = stop_type
        return self

    # PriceLinkBasis
    def set_price_link_basis(self, price_link_basis):
        assert isinstance(price_link_basis, common.PriceLinkBasis)
        self._priceLinkBasis = price_link_basis
        return self

    # PriceLinkType
    def set_price_link_type(self, price_link_type):
        assert isinstance(price_link_type, common.PriceLinkType)
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
        assert isinstance(special_instruction, common.SpecialInstruction)
        self._specialInstruction = special_instruction
        return self

    # OrderStrategyType
    def set_order_strategy_type(self, order_strategy_type):
        assert isinstance(order_strategy_type, common.OrderStrategyType)
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
