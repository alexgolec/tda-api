import argparse
import json

from tda.auth import client_from_token_file
from tda.contrib.orders import construct_repeat_order, code_for_builder


def latest_order_main(sys_args):
    parser = argparse.ArgumentParser(
            description='Utilities for generating code from historical orders')

    required = parser.add_argument_group('required arguments')
    required.add_argument(
            '--token_file', required=True, help='Path to token file')
    required.add_argument('--api_key', required=True)

    parser.add_argument('--account_id', type=int,
            help='Restrict lookups to a specific account ID')

    args = parser.parse_args(args=sys_args)
    client = client_from_token_file(args.token_file, args.api_key)

    if args.account_id:
        orders = client.get_orders_by_path(args.account_id).json()
        if 'error' in orders:
            print(('TDA returned error: "{}", This is most often caused by ' +
                   'an invalid account ID').format(orders['error']))
            return -1
    else:
        orders = client.get_orders_by_query().json()
        if 'error' in orders:
            print('TDA returned error: "{}"'.format(orders['error']))
            return -1

    if orders:
        order = sorted(orders, key=lambda o: -o['orderId'])[0]
        print('# Order ID', order['orderId'])
        print(code_for_builder(construct_repeat_order(order)))
    else:
        print('No recent orders found')

    return 0
