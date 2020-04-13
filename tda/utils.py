'''Implements additional functionality beyond what's implemented in the client
module.'''

import datetime
import dateutil.parser

from .orders import EquityOrderBuilder


class EnumEnforcer:
    def __init__(self, enforce_enums):
        self.enforce_enums = enforce_enums

    def type_error(self, value, required_enum_type):
        raise ValueError(
            ('expected type "{}", got type "{}" (initialize with ' +
             'enforce_enums=True to disable this checking)').format(
                required_enum_type.__name__,
                type(value).__name__))

    def convert_enum(self, value, required_enum_type):
        if value is None:
            return None

        if isinstance(value, required_enum_type):
            return value.value
        elif self.enforce_enums:
            self.type_error(value, required_enum_type)
        else:
            return value

    def convert_enum_iterable(self, iterable, required_enum_type):
        if iterable is None:
            return None

        values = []
        for value in iterable:
            if isinstance(value, required_enum_type):
                values.append(value.value)
            elif self.enforce_enums:
                self.type_error(value, required_enum_type)
            else:
                values.append(value)
        return values

    def set_enforce_enums(self, enforce_enums):
        self.enforce_enums = enforce_enums


class Utils(EnumEnforcer):
    '''Helper for placing orders on equities. Provides easy-to-use
    implementations for common tasks such as market and limit orders.'''

    def __init__(self, client, account_id):
        '''Creates a new ``Utils`` instance. For convenience, this object
        assumes the user wants to work with a single account ID at a time.'''
        super().__init__(True)

        self.client = client
        self.account_id = account_id

    def set_account_id(self, account_id):
        '''Set the account ID used by this ``Utils`` instance.'''
        self.account_id = account_id

    def get_most_recent_order(
            self,
            *,
            symbol=None,
            quantity=None,
            instruction=None,
            order_type=None,
            lookback_window=datetime.timedelta(seconds=60 * 60 * 24)):
        '''
        When placing orders, the TDA API does seem to ever return the order ID
        of the newly placed order. This means if we want to cancel, modify, or
        even monitor its status, we have to take a guess as to which order we
        just placed. This method simplifies things by returning the most
        recently-placed order with the given order signature.

        **Note:** This method cannot guarantee that the calling process was the
        one which placed an order. This means that if there are multiple sources
        of orders, this method may return an order which was placed by another
        process.

        :param symbol: Limit search to orders for this symbol.
        :param quantity: Limit search to orders of this quantity.
        :param instruction: Limit search to orders with this instruction. See
                            :class:`tda.orders.EquityOrderBuilder.Instruction`
        :param order_type: Limit search to orders with this order type. See
                           :class:`tda.orders.EquityOrderBuilder.OrderType`
        :param lookback_window: Limit search to orders entered less than this
                                long ago. Note the TDA API does not provide
                                orders older than 60 days.
        '''
        if quantity is not None and symbol is None:
            raise ValueError(
                'when specifying quantity, must also specify symbol')

        instruction = self.convert_enum(
            instruction, EquityOrderBuilder.Instruction)
        order_type = self.convert_enum(
            order_type, EquityOrderBuilder.OrderType)

        earliest_datetime = datetime.datetime.now() - lookback_window

        resp = self.client.get_orders_by_path(
            self.account_id, from_entered_datetime=earliest_datetime)
        assert resp.ok

        order_spec = EquityOrderBuilder(symbol, quantity)
        if instruction:
            order_spec.set_instruction(
                EquityOrderBuilder.Instruction[instruction])
        if order_type:
            order_spec.set_order_type(
                EquityOrderBuilder.OrderType[order_type])

        def filter_orders(order):
            # Multi-leg orders are not supported
            if len(order['orderLegCollection']) != 1:
                return False

            leg = order['orderLegCollection'][0]
            instrument = leg['instrument']

            # Only return equity orders
            if instrument['assetType'] != 'EQUITY':
                return False

            return order_spec.matches(order)

        return max(filter(filter_orders, resp.json()),
                   default=None,
                   key=lambda order: dateutil.parser.parse(
                       order['enteredTime']))
