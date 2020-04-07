'''Implements additional functionality beyond what's implemented in the client
module.'''

import datetime
import dateutil.parser

from orders import EquityOrderBuilder


class Utils:
    '''Helper for placing orders on equities. Provides easy-to-use
    implementations for common tasks such as market and limit orders.'''

    def __init__(self, client, account_id):
        self.client = client
        self.account_id = account_id

    def get_most_recent_order(
            self,
            *,
            symbol=None,
            quantity=None,
            instruction=None,
            order_type=None,
            lookback_window=datetime.timedelta(seconds=60 * 60 * 24)):
        '''Frustratingly, TDA does not return order IDs when placing orders. As
        a result, we are forced to inspect the list of recent orders to find the
        one which matches the placed order spec.'''
        if quantity is not None and symbol is None:
            raise ValueError(
                'when specifying quantity, must also specify symbol')

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
                   key=lambda order:
                   dateutil.parser.parse(order['enteredTime']))
