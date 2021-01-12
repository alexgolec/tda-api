from enum import Enum

from tda.orders import common
from tda.utils import EnumEnforcer


def _build_object(obj):
    # Literals are passed straight through
    if isinstance(obj, str) or isinstance(obj, int) or isinstance(obj, float):
        return obj

    # Note enums are not handled because call callers convert their enums to
    # values.

    # Dicts and lists are iterated over, with keys intact
    elif isinstance(obj, dict):
        return dict((key, _build_object(value)) for key, value in obj.items())
    elif isinstance(obj, list):
        return [_build_object(i) for i in obj]

    # Objects have their variables translated into keys
    else:
        ret = {}
        for name, value in vars(obj).items():
            if value is None or name[0] != '_':
                continue

            name = name[1:]
            ret[name] = _build_object(value)
        return ret


def truncate_float(flt):
    if abs(flt) < 1 and flt != 0.0:
        return '{:.4f}'.format(float(int(flt * 10000)) / 10000.0)
    else:
        return '{:.2f}'.format(float(int(flt * 100)) / 100.0)


class OrderBuilder(EnumEnforcer):
    '''
    Helper class to create arbitrarily complex orders. Note this class simply
    implements the order schema defined in the `documentation
    <https://developer.tdameritrade.com/account-access/apis/post/accounts/
    %7BaccountId%7D/orders-0>`__, with no attempts to validate the result.
    Orders created using this class may be rejected or may never fill. Use at
    your own risk.
    '''

    def __init__(self, *, enforce_enums=True):
        super().__init__(enforce_enums)

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

    # Session
    def set_session(self, session):
        '''
        Set the order session. See :class:`~tda.orders.common.Session` for
        details.
        '''
        session = self.convert_enum(session, common.Session)
        self._session = session
        return self

    def clear_session(self):
        '''
        Clear the order session.
        '''
        self._session = None
        return self

    # Duration
    def set_duration(self, duration):
        '''
        Set the order duration. See :class:`~tda.orders.common.Duration` for
        details.
        '''
        duration = self.convert_enum(duration, common.Duration)
        self._duration = duration
        return self

    def clear_duration(self):
        '''
        Clear the order duration.
        '''
        self._duration = None
        return self

    # OrderType
    def set_order_type(self, order_type):
        '''
        Set the order type. See :class:`~tda.orders.common.OrderType` for
        details.
        '''
        order_type = self.convert_enum(order_type, common.OrderType)
        self._orderType = order_type
        return self

    def clear_order_type(self):
        '''
        Clear the order type.
        '''
        self._orderType = None
        return self

    # ComplexOrderStrategyType
    def set_complex_order_strategy_type(self, complex_order_strategy_type):
        '''
        Set the complex order strategy type. See
        :class:`~tda.orders.common.ComplexOrderStrategyType` for details.
        '''
        complex_order_strategy_type = self.convert_enum(
            complex_order_strategy_type, common.ComplexOrderStrategyType)
        self._complexOrderStrategyType = complex_order_strategy_type
        return self

    def clear_complex_order_strategy_type(self):
        '''
        Clear the complex order strategy type.
        '''
        self._complexOrderStrategyType = None
        return self

    # Quantity
    def set_quantity(self, quantity):
        '''
        Exact semantics unknown. See :ref:`undocumented_quantity` for a
        discussion.
        '''
        if quantity <= 0:
            raise ValueError('quantity must be positive')
        self._quantity = quantity
        return self

    def clear_quantity(self):
        '''
        Clear the order-level quantity. Note this does not affect order legs.
        '''
        self._quantity = None
        return self

    # RequestedDestination
    def set_requested_destination(self, requested_destination):
        '''
        Set the requested destination. See
        :class:`~tda.orders.common.Destination` for details.
        '''
        requested_destination = self.convert_enum(
            requested_destination, common.Destination)
        self._requestedDestination = requested_destination
        return self

    def clear_requested_destination(self):
        '''
        Clear the requested destination.
        '''
        self._requestedDestination = None
        return self

    # StopPrice
    def set_stop_price(self, stop_price):
        '''
        Set the stop price. Note price can be passed as either a `float` or an
        `str`. See :ref:`number_truncation`.
        '''
        if isinstance(stop_price, str):
            self._stopPrice = stop_price
        else:
            self._stopPrice = truncate_float(stop_price)
        return self

    def clear_stop_price(self):
        '''
        Clear the stop price.
        '''
        self._stopPrice = None
        return self

    # StopPriceLinkBasis
    def set_stop_price_link_basis(self, stop_price_link_basis):
        '''
        Set the stop price link basis. See
        :class:`~tda.orders.common.StopPriceLinkBasis` for details.
        '''
        stop_price_link_basis = self.convert_enum(
            stop_price_link_basis, common.StopPriceLinkBasis)
        self._stopPriceLinkBasis = stop_price_link_basis
        return self

    def clear_stop_price_link_basis(self):
        '''
        Clear the stop price link basis.
        '''
        self._stopPriceLinkBasis = None
        return self

    # StopPriceLinkType
    def set_stop_price_link_type(self, stop_price_link_type):
        '''
        Set the stop price link type. See
        :class:`~tda.orders.common.StopPriceLinkType` for details.
        '''
        stop_price_link_type = self.convert_enum(
            stop_price_link_type, common.StopPriceLinkType)
        self._stopPriceLinkType = stop_price_link_type
        return self

    def clear_stop_price_link_type(self):
        '''
        Clear the stop price link type.
        '''
        self._stopPriceLinkType = None
        return self

    # StopPriceOffset
    def set_stop_price_offset(self, stop_price_offset):
        '''
        Set the stop price offset.
        '''
        self._stopPriceOffset = stop_price_offset
        return self

    def clear_stop_price_offset(self):
        '''
        Clear the stop price offset.
        '''
        self._stopPriceOffset = None
        return self

    # StopType
    def set_stop_type(self, stop_type):
        '''
        Set the stop type. See
        :class:`~tda.orders.common.StopType` for more details.
        '''
        stop_type = self.convert_enum(stop_type, common.StopType)
        self._stopType = stop_type
        return self

    def clear_stop_type(self):
        '''
        Clear the stop type.
        '''
        self._stopType = None
        return self

    # PriceLinkBasis
    def set_price_link_basis(self, price_link_basis):
        '''
        Set the price link basis. See
        :class:`~tda.orders.common.PriceLinkBasis` for details.
        '''
        price_link_basis = self.convert_enum(
            price_link_basis, common.PriceLinkBasis)
        self._priceLinkBasis = price_link_basis
        return self

    def clear_price_link_basis(self):
        '''
        Clear the price link basis.
        '''
        self._priceLinkBasis = None
        return self

    # PriceLinkType
    def set_price_link_type(self, price_link_type):
        '''
        Set the price link type. See
        :class:`~tda.orders.common.PriceLinkType` for more details.
        '''
        price_link_type = self.convert_enum(
            price_link_type, common.PriceLinkType)
        self._priceLinkType = price_link_type
        return self

    def clear_price_link_type(self):
        '''
        Clear the price link basis.
        '''
        self._priceLinkType = None
        return self

    # Price
    def set_price(self, price):
        '''
        Set the order price. Note price can be passed as either a `float` or an
        `str`. See :ref:`number_truncation`.
        '''
        if isinstance(price, str):
            self._price = price
        else:
            self._price = truncate_float(price)
        return self

    def clear_price(self):
        '''
        Clear the order price
        '''
        self._price = None
        return self

    # ActivationPrice
    def set_activation_price(self, activation_price):
        '''
        Set the activation price.
        '''
        if activation_price <= 0.0:
            raise ValueError('activation price must be positive')
        self._activationPrice = activation_price
        return self

    def clear_activation_price(self):
        '''
        Clear the activation price.
        '''
        self._activationPrice = None
        return self

    # SpecialInstruction
    def set_special_instruction(self, special_instruction):
        '''
        Set the special instruction. See
        :class:`~tda.orders.common.SpecialInstruction` for details.
        '''
        special_instruction = self.convert_enum(
            special_instruction, common.SpecialInstruction)
        self._specialInstruction = special_instruction
        return self

    def clear_special_instruction(self):
        '''
        Clear the special instruction.
        '''
        self._specialInstruction = None
        return self

    # OrderStrategyType
    def set_order_strategy_type(self, order_strategy_type):
        '''
        Set the order strategy type. See
        :class:`~tda.orders.common.OrderStrategyType` for more details.
        '''
        order_strategy_type = self.convert_enum(
            order_strategy_type, common.OrderStrategyType)
        self._orderStrategyType = order_strategy_type
        return self

    def clear_order_strategy_type(self):
        '''
        Clear the order strategy type.
        '''
        self._orderStrategyType = None
        return self

    # ChildOrderStrategies
    def add_child_order_strategy(self, child_order_strategy):
        if (not isinstance(child_order_strategy, OrderBuilder)
                and not isinstance(child_order_strategy, dict)):
            raise ValueError('child order must be OrderBuilder or dict')

        if self._childOrderStrategies is None:
            self._childOrderStrategies = []

        self._childOrderStrategies.append(child_order_strategy)
        return self

    def clear_child_order_strategies(self):
        self._childOrderStrategies = None
        return self

    # OrderLegCollection
    def __add_order_leg(self, instruction, instrument, quantity):
        # instruction is assumed to have been verified

        if quantity <= 0:
            raise ValueError('quantity must be positive')

        if self._orderLegCollection is None:
            self._orderLegCollection = []

        self._orderLegCollection.append({
            'instruction': instruction,
            'instrument': instrument,
            'quantity': quantity,
        })

        return self

    def add_equity_leg(self, instruction, symbol, quantity):
        '''
        Add an equity order leg.

        :param instruction: Instruction for the leg. See
                            :class:`~tda.orders.common.EquityInstruction` for
                            valid options.
        :param symbol: Equity symbol
        :param quantity: Number of shares for the order
        '''
        instruction = self.convert_enum(instruction, common.EquityInstruction)
        return self.__add_order_leg(
            instruction, common.EquityInstrument(symbol), quantity)

    def add_option_leg(self, instruction, symbol, quantity):
        '''
        Add an option order leg.

        :param instruction: Instruction for the leg. See
                            :class:`~tda.orders.common.OptionInstruction` for
                            valid options.
        :param symbol: Option symbol
        :param quantity: Number of contracts for the order
        '''
        instruction = self.convert_enum(instruction, common.OptionInstruction)
        return self.__add_order_leg(
            instruction, common.OptionInstrument(symbol), quantity)

    def clear_order_legs(self):
        '''
        Clear all order legs.
        '''
        self._orderLegCollection = None
        return self

    # Build

    def build(self):
        return _build_object(self)
