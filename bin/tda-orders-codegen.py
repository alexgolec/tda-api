#! env python
import argparse
import json

import tda

from tda.contrib.orders import construct_repeat_order, code_for_builder

def main(token_path, api_key, account_id, order_id):
    client = tda.auth.client_from_token_file(token_path, api_key)

    if account_id is None:
        accounts = client.get_accounts().json()
        if len(accounts) != 1:
            print('More than one account associated with this key. Run with '+
                  '--account_id to specify an account.')
        account_id = accounts[0]['securitiesAccount']['accountId']

    if order_id:
        orders = [client.get_order(order_id, account_id).json()]
    else:
        orders = client.get_orders_by_path(account_id).json()

    for order in orders:
        print(code_for_builder(construct_repeat_order(order)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Utilities for generating code from historical orders')

    required = parser.add_argument_group('required arguments')
    required.add_argument(
            '--token_file', required=True, help='Path to token file')
    required.add_argument('--api_key', required=True)

    parser.add_argument('--account_id', type=int,
            help='Specifies the account ID. Can be unspecified if there is '+
                 'exactly one account associated with this token.')
    parser.add_argument('order_id', type=int, nargs='?',
            help='If set, generate code for only this order ID. If unset, '+
                 'generate code for all historical orders.')

    args = parser.parse_args()

    main(args.token_file, args.api_key, args.account_id, args.order_id)
