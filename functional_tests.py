if __name__ == '__main__':
    import argparse
    import json
    import sys
    import tda
    import unittest

    tda.debug.enable_bug_report_logging()
    import logging
    logging.getLogger('').addHandler(logging.StreamHandler())

    class FunctionalTests(unittest.TestCase):

        @classmethod
        def set_client(cls, client):
            cls.client = client


        @classmethod
        def setUpClass(cls):
            # Ensure we never run over an account with funds or assets under it
            account = cls.client.get_account(args.account_id).json()
            print(json.dumps(account, indent=4))
            balances = account['securitiesAccount']['currentBalances']
            def assert_balances(name):
                if balances[name] != 0:
                    if args.allow_balances:
                        print()
                        print()
                        print()
                        print('###################################################')
                        print()

                        print(f'Account has nonzero \'{name}\'')
                        print()
                        print(f'Functional tests are being run because of ')
                        print(f'--allow_balances.')
                        cont = input('Please type \'continue\' to continue: ')
                        assert cont.lower() == 'continue'

                        print()
                        print('###################################################')
                        print()
                        print()
                        print()

                        return True

                    else:
                        print()
                        print()
                        print()
                        print('###################################################')
                        print()

                        print(f'Account has nonzero \'{name}\'')
                        print()
                        print(f'Functional tests aborted. You can rerun tests AT ')
                        print(f'YOUR OWN RISK by specifying --allow_balances.')

                        print()
                        print('###################################################')
                        print()
                        print()
                        print()

                        return False

            for balance in ('liquidationValue',
                    'longOptionMarketValue',
                    'moneyMarketFund',
                    'cashAvailableForTrading',
                    'cashAvailableForWithdrawal'):
                if assert_balances(balance):
                    break


        def test_something(self):
            pass


    parser = argparse.ArgumentParser('Runs functional tests')
    parser.add_argument('--token', required=True, help='Path to token file')
    parser.add_argument('--account_id', type=int, required=True)
    parser.add_argument('--api_key', type=str, required=True)
    parser.add_argument('--allow_balances', action='store_true', default=False)
    args = parser.parse_args()

    FunctionalTests.set_client(
            tda.auth.client_from_token_file(args.token, args.api_key))

    unittest.main(argv=[sys.argv[0]])
