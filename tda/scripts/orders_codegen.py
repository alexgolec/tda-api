import argparse

from tda.auth import client_from_token_file
from tda.contrib.orders import construct_repeat_order, code_for_builder

def main(sys_args):
    parser = argparse.ArgumentParser(
            description='Utilities for generating code from historical orders')

    required = parser.add_argument_group('required arguments')
    required.add_argument(
            '--token_file', required=True, help='Path to token file')
    required.add_argument('--api_key', required=True)

    parser.add_argument('--account_id', type=int,
            help='Restrict lookups to a specific account ID')
    parser.add_argument('--order_id', type=int,
            help='If set, generate code for only this order ID. If unset, '+
                 'generate code for all historical orders.')

    args = parser.parse_args(args=sys_args)

    client = client_from_token_file(args.token_file, args.api_key)

    order_id = args.order_id
    account_id = args.account_id

    if order_id:
        if account_id:
            orders = [client.get_order(order_id, account_id).json()]
        else:
            accounts = client.get_accounts().json()
            for account in accounts:
                account_id = account['securitiesAccount']['accountId']
                order = client.get_order(order_id, account_id).json()
                if 'error' not in order:
                    orders = [order]
                    break
            else:
                print('Failed to find order for order_id', order_id)
                return -1
    else:
        if account_id:
            orders = client.get_orders_by_path(account_id).json()
        else:
            orders = client.get_orders_by_query().json()

    for order in sorted(orders, key=lambda order: order['orderId']):
        print('# Order ID', order['orderId'])
        print(code_for_builder(construct_repeat_order(order)))

    return 0
