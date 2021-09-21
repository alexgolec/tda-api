if __name__ == '__main__':
    import argparse
    import asyncio
    import json
    import sys
    import tda
    import unittest

    from tda.streaming import StreamClient

    tda.debug.enable_bug_report_logging()
    import logging
    logging.getLogger('').addHandler(logging.StreamHandler())

    class FunctionalTests(unittest.TestCase):

        @classmethod
        def set_client(cls, client):
            cls.client = client


        @classmethod
        def setUpClass(cls):
            cls.account_id = args.account_id

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


        def test_streaming(self):
            print()
            print('##########################################################')
            print()
            print('Testing stream connection and handling...')

            stream_client = StreamClient(self.client, account_id=self.account_id)
            async def read_stream():
                await stream_client.login()
                await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

                stream_client.add_nasdaq_book_handler(
                        lambda msg: print(json.dumps(msg, indent=4)))
                await stream_client.nasdaq_book_subs(['GOOG'])

                # Handle one message and then declare victory
                await stream_client.handle_message()

            asyncio.run(read_stream())

            print()
            print('##########################################################')
            print()


    parser = argparse.ArgumentParser('Runs functional tests')
    parser.add_argument('--token', required=True, help='Path to token file')
    parser.add_argument('--account_id', type=int, required=True)
    parser.add_argument('--api_key', type=str, required=True)
    parser.add_argument('--allow_balances', action='store_true', default=False)
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger('').setLevel(logging.DEBUG)

    FunctionalTests.set_client(
            tda.auth.client_from_token_file(args.token, args.api_key))

    unittest.main(argv=[sys.argv[0]])
