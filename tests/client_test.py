import datetime
import os
import pytz
import unittest
from unittest.mock import ANY, MagicMock, Mock, patch

from tda.client import Client
from tests.test_utils import no_duplicates

# Constants

API_KEY = '1234567890'
ACCOUNT_ID = 100000
ORDER_ID = 200000
SAVED_ORDER_ID = 300000
CUSIP = '000919239'
MARKET = 'EQUITY'
INDEX = '$SPX.X'
SYMBOL = 'AAPL'
TRANSACTION_ID = 400000
WATCHLIST_ID = 5000000

MIN_ISO = '1900-01-01T00:00:00+0000'

NOW_DATETIME = datetime.datetime(2020, 1, 2, 3, 4, 5)
NOW_DATE = datetime.date(2020, 1, 2)
NOW_DATETIME_ISO = '2020-01-02T03:04:05+0000'
NOW_DATE_ISO = '2020-01-02'


class mockdatetime(datetime.datetime):
    @classmethod
    def utcnow(cls):
        return NOW_DATETIME


EARLIER_DATETIME = datetime.datetime(2001, 1, 2, 3, 4, 5,
                                     tzinfo=pytz.timezone('America/New_York'))
EARLIER_ISO = '2001-01-02T03:04:05-0456'
EARLIER_MILLIS = 978422405000
EARLIER_DATE_STR = '2001-01-02'


class TestClient(unittest.TestCase):

    def setUp(self):
        self.mock_session = MagicMock()
        self.client = Client(API_KEY, self.mock_session)

    def make_url(self, path):
        path = path.format(
            accountId=ACCOUNT_ID,
            orderId=ORDER_ID,
            savedOrderId=SAVED_ORDER_ID,
            cusip=CUSIP,
            market=MARKET,
            index=INDEX,
            symbol=SYMBOL,
            transactionId=TRANSACTION_ID,
            watchlistId=WATCHLIST_ID)
        return 'https://api.tdameritrade.com' + path

    # get_order

    @no_duplicates
    def test_get_order(self):
        self.client.get_order(ORDER_ID, ACCOUNT_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders/{orderId}'),
            params={})

    @no_duplicates
    def test_get_order_str(self):
        self.client.get_order(str(ORDER_ID), str(ACCOUNT_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders/{orderId}'),
            params={})

    # cancel_order

    @no_duplicates
    def test_cancel_order(self):
        self.client.cancel_order(ORDER_ID, ACCOUNT_ID)
        self.mock_session.delete.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders/{orderId}'))

    @no_duplicates
    def test_cancel_order_str(self):
        self.client.cancel_order(str(ORDER_ID), str(ACCOUNT_ID))
        self.mock_session.delete.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders/{orderId}'))

    # get_orders_by_path

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_vanilla(self):
        self.client.get_orders_by_path(ACCOUNT_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_vanilla_str(self):
        self.client.get_orders_by_path(str(ACCOUNT_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_from_not_datetime(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_orders_by_path(
                ACCOUNT_ID, from_entered_datetime='2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type 'datetime.datetime' for " +
                         "from_entered_datetime, got 'builtins.str'")

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_to_not_datetime(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_orders_by_path(
                ACCOUNT_ID, to_entered_datetime='2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type 'datetime.datetime' for " +
                         "to_entered_datetime, got 'builtins.str'")

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_max_results(self):
        self.client.get_orders_by_path(ACCOUNT_ID, max_results=100)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'maxResults': 100,
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_from_entered_datetime(self):
        self.client.get_orders_by_path(
            ACCOUNT_ID, from_entered_datetime=EARLIER_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': EARLIER_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_to_entered_datetime(self):
        self.client.get_orders_by_path(
            ACCOUNT_ID, to_entered_datetime=EARLIER_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': EARLIER_ISO,
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_status_and_statuses(self):
        self.assertRaises(ValueError, lambda: self.client.get_orders_by_path(
            ACCOUNT_ID, to_entered_datetime=EARLIER_DATETIME,
            status='EXPIRED', statuses=[Client.Order.Status.FILLED]))

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_status(self):
        self.client.get_orders_by_path(
            ACCOUNT_ID, status=Client.Order.Status.FILLED)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'status': 'FILLED'
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_status_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_orders_by_path(ACCOUNT_ID, status='FILLED')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'status': 'FILLED'
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_statuses(self):
        self.client.get_orders_by_path(
            ACCOUNT_ID, statuses=[
                Client.Order.Status.FILLED,
                Client.Order.Status.EXPIRED])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'status': 'FILLED,EXPIRED'
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_path_statuses_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_orders_by_path(
            ACCOUNT_ID, statuses=['FILLED', 'EXPIRED'])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'status': 'FILLED,EXPIRED'
            })

    # get_orders_by_query

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_vanilla(self):
        self.client.get_orders_by_query()
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_max_results(self):
        self.client.get_orders_by_query(max_results=100)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'maxResults': 100,
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_from_entered_datetime(self):
        self.client.get_orders_by_query(from_entered_datetime=EARLIER_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/orders'), params={
                'fromEnteredTime': EARLIER_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_to_entered_datetime(self):
        self.client.get_orders_by_query(to_entered_datetime=EARLIER_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': EARLIER_ISO,
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_status_and_statuses(self):
        with self.assertRaises(
                ValueError, msg='at most one of status or statuses may be set'):
            self.client.get_orders_by_query(
                to_entered_datetime=EARLIER_DATETIME,
                status='EXPIRED', statuses=[
                    Client.Order.Status.FILLED,
                    Client.Order.Status.EXPIRED])

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_status(self):
        self.client.get_orders_by_query(status=Client.Order.Status.FILLED)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'status': 'FILLED'
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_status_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_orders_by_query(status='FILLED')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'status': 'FILLED'
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_statuses(self):
        self.client.get_orders_by_query(statuses=[
            Client.Order.Status.FILLED,
            Client.Order.Status.EXPIRED])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'status': 'FILLED,EXPIRED'
            })

    @no_duplicates
    @patch('tda.client.datetime.datetime', mockdatetime)
    def test_get_orders_by_query_statuses_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_orders_by_query(statuses=['FILLED', 'EXPIRED'])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/orders'), params={
                'fromEnteredTime': MIN_ISO,
                'toEnteredTime': NOW_DATETIME_ISO,
                'status': 'FILLED,EXPIRED'
            })

    # place_order

    @no_duplicates
    def test_place_order(self):
        order_spec = {'order': 'spec'}
        self.client.place_order(ACCOUNT_ID, order_spec)
        self.mock_session.post.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), json=order_spec)

    @no_duplicates
    def test_place_order_str(self):
        order_spec = {'order': 'spec'}
        self.client.place_order(str(ACCOUNT_ID), order_spec)
        self.mock_session.post.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders'), json=order_spec)

    # replace_order

    @no_duplicates
    def test_replace_order(self):
        order_spec = {'order': 'spec'}
        self.client.replace_order(ACCOUNT_ID, ORDER_ID, order_spec)
        self.mock_session.put.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders/{orderId}'),
            json=order_spec)

    @no_duplicates
    def test_replace_order_str(self):
        order_spec = {'order': 'spec'}
        self.client.replace_order(str(ACCOUNT_ID), str(ORDER_ID), order_spec)
        self.mock_session.put.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/orders/{orderId}'),
            json=order_spec)

    # create_saved_order

    @no_duplicates
    def test_create_saved_order(self):
        order_spec = {'order': 'spec'}
        self.client.create_saved_order(ACCOUNT_ID, order_spec)
        self.mock_session.post.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/savedorders'),
            json=order_spec)

    @no_duplicates
    def test_create_saved_order_str(self):
        order_spec = {'order': 'spec'}
        self.client.create_saved_order(str(ACCOUNT_ID), order_spec)
        self.mock_session.post.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/savedorders'),
            json=order_spec)

    # delete_saved_order

    @no_duplicates
    def test_delete_saved_order(self):
        self.client.delete_saved_order(ACCOUNT_ID, SAVED_ORDER_ID)
        self.mock_session.delete.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/savedorders/{savedOrderId}'))

    @no_duplicates
    def test_delete_saved_order_str(self):
        self.client.delete_saved_order(str(ACCOUNT_ID), str(SAVED_ORDER_ID))
        self.mock_session.delete.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/savedorders/{savedOrderId}'))

    # delete_saved_order

    @no_duplicates
    def test_get_saved_order(self):
        self.client.get_saved_order(ACCOUNT_ID, SAVED_ORDER_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url(
                '/v1/accounts/{accountId}/savedorders/{savedOrderId}'),
            params={})

    @no_duplicates
    def test_get_saved_order_str(self):
        self.client.get_saved_order(str(ACCOUNT_ID), str(SAVED_ORDER_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url(
                '/v1/accounts/{accountId}/savedorders/{savedOrderId}'),
            params={})

    # get_saved_orders_by_path

    @no_duplicates
    def test_get_saved_orders_by_path(self):
        self.client.get_saved_orders_by_path(ACCOUNT_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/savedorders'), params={})

    @no_duplicates
    def test_get_saved_orders_by_path_str(self):
        self.client.get_saved_orders_by_path(str(ACCOUNT_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/savedorders'), params={})

    # replace_saved_order

    @no_duplicates
    def test_replace_saved_order(self):
        order_spec = {'order': 'spec'}
        self.client.replace_saved_order(ACCOUNT_ID, SAVED_ORDER_ID, order_spec)
        self.mock_session.put.assert_called_once_with(
            self.make_url(
                '/v1/accounts/{accountId}/savedorders/{savedOrderId}'),
            json=order_spec)

    @no_duplicates
    def test_replace_saved_order_str(self):
        order_spec = {'order': 'spec'}
        self.client.replace_saved_order(
            str(ACCOUNT_ID), str(SAVED_ORDER_ID), order_spec)
        self.mock_session.put.assert_called_once_with(
            self.make_url(
                '/v1/accounts/{accountId}/savedorders/{savedOrderId}'),
            json=order_spec)

    # get_account

    @no_duplicates
    def test_get_account(self):
        self.client.get_account(ACCOUNT_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}'), params={})

    @no_duplicates
    def test_get_account_str(self):
        self.client.get_account(str(ACCOUNT_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}'), params={})

    @no_duplicates
    def test_get_account_fields(self):
        self.client.get_account(ACCOUNT_ID, fields=[
            Client.Account.Fields.POSITIONS,
            Client.Account.Fields.ORDERS])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}'),
            params={'fields': 'positions,orders'})

    @no_duplicates
    def test_get_account_fields_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_account(ACCOUNT_ID, fields=['positions', 'orders'])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}'),
            params={'fields': 'positions,orders'})

    # get_accounts

    @no_duplicates
    def test_get_accounts(self):
        self.client.get_accounts()
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts'), params={})

    @no_duplicates
    def test_get_accounts_fields(self):
        self.client.get_accounts(fields=[
            Client.Account.Fields.POSITIONS,
            Client.Account.Fields.ORDERS])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts'),
            params={'fields': 'positions,orders'})

    @no_duplicates
    def test_get_accounts_fields_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_accounts(fields=['positions', 'orders'])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts'),
            params={'fields': 'positions,orders'})

    # search_instruments

    @no_duplicates
    def test_search_instruments(self):
        self.client.search_instruments(
            ['AAPL', 'MSFT'], Client.Instrument.Projection.FUNDAMENTAL)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/instruments'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL,MSFT',
                'projection': 'fundamental'})

    @no_duplicates
    def test_search_instruments_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.search_instruments(['AAPL', 'MSFT'], 'fundamental')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/instruments'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL,MSFT',
                'projection': 'fundamental'})

    # get_instrument

    @no_duplicates
    def test_get_instrument(self):
        self.client.get_instrument(CUSIP)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/instruments/{cusip}'),
            params={'apikey': API_KEY})

    @no_duplicates
    def test_get_instrument_cusip_must_be_string(self):
        msg = 'CUSIPs must be passed as strings to preserve leading zeroes'
        with self.assertRaises(ValueError, msg=msg):
            self.client.get_instrument(123456)

    # get_hours_for_multiple_markets

    @no_duplicates
    def test_get_hours_for_multiple_markets_datetime(self):
        self.client.get_hours_for_multiple_markets([
            Client.Markets.EQUITY,
            Client.Markets.BOND], NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/hours'), params={
                'apikey': API_KEY,
                'markets': 'EQUITY,BOND',
                'date': NOW_DATE_ISO})

    @no_duplicates
    def test_get_hours_for_multiple_markets_date(self):
        self.client.get_hours_for_multiple_markets([
            Client.Markets.EQUITY,
            Client.Markets.BOND], NOW_DATE)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/hours'), params={
                'apikey': API_KEY,
                'markets': 'EQUITY,BOND',
                'date': NOW_DATE_ISO})

    @no_duplicates
    def test_get_hours_for_multiple_markets_str(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_hours_for_multiple_markets([
                Client.Markets.EQUITY,
                Client.Markets.BOND], '2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type in (datetime.date, datetime.datetime) for " +
                         "date, got 'builtins.str'")

    @no_duplicates
    def test_get_hours_for_multiple_markets_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_hours_for_multiple_markets(
            ['EQUITY', 'BOND'], NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/hours'), params={
                'apikey': API_KEY,
                'markets': 'EQUITY,BOND',
                'date': NOW_DATE_ISO})

    # get_hours_for_single_market

    @no_duplicates
    def test_get_hours_for_single_market_datetime(self):
        self.client.get_hours_for_single_market(
            Client.Markets.EQUITY, NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{market}/hours'), params={
                'apikey': API_KEY,
                'date': NOW_DATE_ISO})

    @no_duplicates
    def test_get_hours_for_single_market_date(self):
        self.client.get_hours_for_single_market(
            Client.Markets.EQUITY, NOW_DATE)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{market}/hours'), params={
                'apikey': API_KEY,
                'date': NOW_DATE_ISO})

    @no_duplicates
    def test_get_hours_for_single_market_str(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_hours_for_single_market(
                Client.Markets.EQUITY, '2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type in (datetime.date, datetime.datetime) for " +
                         "date, got 'builtins.str'")

    @no_duplicates
    def test_get_hours_for_single_market_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_hours_for_single_market('EQUITY', NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{market}/hours'), params={
                'apikey': API_KEY,
                'date': NOW_DATE_ISO})

    # get_movers

    @no_duplicates
    def test_get_movers(self):
        self.client.get_movers(
            INDEX, Client.Movers.Direction.UP, Client.Movers.Change.PERCENT)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{index}/movers'), params={
                'apikey': API_KEY,
                'direction': 'up',
                'change': 'percent'})

    @no_duplicates
    def test_get_movers_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_movers(INDEX, 'up', 'percent')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{index}/movers'), params={
                'apikey': API_KEY,
                'direction': 'up',
                'change': 'percent'})

    # get_option_chain

    @no_duplicates
    def test_get_option_chain_vanilla(self):
        self.client.get_option_chain('AAPL')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL'})

    @no_duplicates
    def test_get_option_chain_contract_type(self):
        self.client.get_option_chain(
            'AAPL', contract_type=Client.Options.ContractType.PUT)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'contractType': 'PUT'})

    @no_duplicates
    def test_get_option_chain_contract_type_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_option_chain('AAPL', contract_type='PUT')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'contractType': 'PUT'})

    @no_duplicates
    def test_get_option_chain_strike_count(self):
        self.client.get_option_chain('AAPL', strike_count=100)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'strikeCount': 100})

    @no_duplicates
    def test_get_option_chain_include_quotes(self):
        self.client.get_option_chain('AAPL', include_quotes=True)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'includeQuotes': True})

    @no_duplicates
    def test_get_option_chain_strategy(self):
        self.client.get_option_chain(
            'AAPL', strategy=Client.Options.Strategy.STRANGLE)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'strategy': 'STRANGLE'})

    @no_duplicates
    def test_get_option_chain_strategy_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_option_chain('AAPL', strategy='STRANGLE')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'strategy': 'STRANGLE'})

    @no_duplicates
    def test_get_option_chain_interval(self):
        self.client.get_option_chain('AAPL', interval=10.0)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'interval': 10.0})

    @no_duplicates
    def test_get_option_chain_strike(self):
        self.client.get_option_chain('AAPL', strike=123)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'strike': 123})

    @no_duplicates
    def test_get_option_chain_strike_range(self):
        self.client.get_option_chain(
            'AAPL', strike_range=Client.Options.StrikeRange.IN_THE_MONEY)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'range': 'ITM'})

    @no_duplicates
    def test_get_option_chain_strike_range_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_option_chain('AAPL', strike_range='ITM')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'range': 'ITM'})

    @no_duplicates
    def test_get_option_chain_from_date_datetime(self):
        self.client.get_option_chain(
            'AAPL', strike_from_date=NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'fromDate': NOW_DATE_ISO})

    @no_duplicates
    def test_get_option_chain_from_date_date(self):
        self.client.get_option_chain('AAPL', strike_from_date=NOW_DATE)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'fromDate': NOW_DATE_ISO})

    @no_duplicates
    def test_get_option_chain_from_date_str(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_option_chain('AAPL', strike_from_date='2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type in (datetime.date, datetime.datetime) for " +
                         "strike_from_date, got 'builtins.str'")

    @no_duplicates
    def test_get_option_chain_to_date_datetime(self):
        self.client.get_option_chain('AAPL', strike_to_date=NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'toDate': NOW_DATE_ISO})

    @no_duplicates
    def test_get_option_chain_to_date_date(self):
        self.client.get_option_chain('AAPL', strike_to_date=NOW_DATE)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'toDate': NOW_DATE_ISO})

    @no_duplicates
    def test_get_option_chain_to_date_str(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_option_chain('AAPL', strike_to_date='2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type in (datetime.date, datetime.datetime) for " +
                         "strike_to_date, got 'builtins.str'")

    @no_duplicates
    def test_get_option_chain_volatility(self):
        self.client.get_option_chain('AAPL', volatility=40.0)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'volatility': 40.0})

    @no_duplicates
    def test_get_option_chain_underlying_price(self):
        self.client.get_option_chain('AAPL', underlying_price=234.0)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'underlyingPrice': 234.0})

    @no_duplicates
    def test_get_option_chain_interest_rate(self):
        self.client.get_option_chain('AAPL', interest_rate=0.07)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'interestRate': 0.07})

    @no_duplicates
    def test_get_option_chain_days_to_expiration(self):
        self.client.get_option_chain('AAPL', days_to_expiration=12)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'daysToExpiration': 12})

    @no_duplicates
    def test_get_option_chain_exp_month(self):
        self.client.get_option_chain(
            'AAPL', exp_month=Client.Options.ExpirationMonth.JANUARY)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'expMonth': 'JAN'})

    @no_duplicates
    def test_get_option_chain_exp_month_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_option_chain('AAPL', exp_month='JAN')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'expMonth': 'JAN'})

    @no_duplicates
    def test_get_option_chain_option_type(self):
        self.client.get_option_chain(
            'AAPL', option_type=Client.Options.Type.STANDARD)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'optionType': 'S'})

    @no_duplicates
    def test_get_option_chain_option_type_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_option_chain('AAPL', option_type='S')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/chains'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL',
                'optionType': 'S'})

    # get_price_history

    @no_duplicates
    def test_get_price_history_vanilla(self):
        self.client.get_price_history(SYMBOL)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY})

    @no_duplicates
    def test_get_price_history_period_type(self):
        self.client.get_price_history(
            SYMBOL, period_type=Client.PriceHistory.PeriodType.MONTH)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'periodType': 'month'})

    @no_duplicates
    def test_get_price_history_period_type_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_price_history(SYMBOL, period_type='month')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'periodType': 'month'})

    @no_duplicates
    def test_get_price_history_num_periods(self):
        self.client.get_price_history(
            SYMBOL, period=Client.PriceHistory.Period.TEN_DAYS)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'period': 10})

    @no_duplicates
    def test_get_price_history_num_periods_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_price_history(SYMBOL, period=10)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'period': 10})

    @no_duplicates
    def test_get_price_history_frequency_type(self):
        self.client.get_price_history(
            SYMBOL,
            frequency_type=Client.PriceHistory.FrequencyType.DAILY)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'frequencyType': 'daily'})

    @no_duplicates
    def test_get_price_history_frequency_type_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_price_history(SYMBOL, frequency_type='daily')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'frequencyType': 'daily'})

    @no_duplicates
    def test_get_price_history_frequency(self):
        self.client.get_price_history(
            SYMBOL,
            frequency=Client.PriceHistory.Frequency.EVERY_FIVE_MINUTES)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'frequency': 5})

    @no_duplicates
    def test_get_price_history_frequency_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_price_history(SYMBOL, frequency=5)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'frequency': 5})

    @no_duplicates
    def test_get_price_history_start_datetime(self):
        self.client.get_price_history(
            SYMBOL, start_datetime=EARLIER_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'startDate': EARLIER_MILLIS})

    @no_duplicates
    def test_get_price_history_start_datetime_str(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_price_history(SYMBOL, start_datetime='2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type 'datetime.datetime' for " +
                         "start_datetime, got 'builtins.str'")

    @no_duplicates
    def test_get_price_history_end_datetime(self):
        self.client.get_price_history(SYMBOL, end_datetime=EARLIER_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'endDate': EARLIER_MILLIS})

    @no_duplicates
    def test_get_price_history_end_datetime_str(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_price_history(SYMBOL, end_datetime='2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type 'datetime.datetime' for " +
                         "end_datetime, got 'builtins.str'")

    @no_duplicates
    def test_get_price_history_need_extended_hours_data(self):
        self.client.get_price_history(SYMBOL, need_extended_hours_data=True)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/pricehistory'), params={
                'apikey': API_KEY,
                'needExtendedHoursData': True})

    # get_quote

    @no_duplicates
    def test_get_quote(self):
        self.client.get_quote(SYMBOL)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/{symbol}/quotes'), params={
                'apikey': API_KEY})

    # get_quotes

    @no_duplicates
    def test_get_quotes(self):
        self.client.get_quotes(['AAPL', 'MSFT'])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/marketdata/quotes'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL,MSFT'})

    # get_transaction

    @no_duplicates
    def test_get_transaction(self):
        self.client.get_transaction(ACCOUNT_ID, TRANSACTION_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url(
                '/v1/accounts/{accountId}/transactions/{transactionId}'),
            params={'apikey': API_KEY})

    @no_duplicates
    def test_get_transaction_str(self):
        self.client.get_transaction(str(ACCOUNT_ID), str(TRANSACTION_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url(
                '/v1/accounts/{accountId}/transactions/{transactionId}'),
            params={'apikey': API_KEY})

    # get_transactions

    @no_duplicates
    def test_get_transactions(self):
        self.client.get_transactions(ACCOUNT_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY})

    @no_duplicates
    def test_get_transactions_str(self):
        self.client.get_transactions(str(ACCOUNT_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY})

    @no_duplicates
    def test_get_transactions_type(self):
        self.client.get_transactions(
            ACCOUNT_ID,
            transaction_type=Client.Transactions.TransactionType.DIVIDEND)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY,
                'type': 'DIVIDEND'})

    @no_duplicates
    def test_get_transactions_type_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_transactions(ACCOUNT_ID, transaction_type='DIVIDEND')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY,
                'type': 'DIVIDEND'})

    @no_duplicates
    def test_get_transactions_symbol(self):
        self.client.get_transactions(ACCOUNT_ID, symbol='AAPL')
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY,
                'symbol': 'AAPL'})

    @no_duplicates
    def test_get_transactions_start_date_datetime(self):
        self.client.get_transactions(ACCOUNT_ID, start_date=NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY,
                'startDate': NOW_DATE_ISO})

    @no_duplicates
    def test_get_transactions_start_date_date(self):
        self.client.get_transactions(ACCOUNT_ID, start_date=NOW_DATE)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY,
                'startDate': NOW_DATE_ISO})

    @no_duplicates
    def test_get_transactions_start_date_str(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_transactions(ACCOUNT_ID, start_date='2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type in (datetime.date, datetime.datetime) for " +
                         "start_date, got 'builtins.str'")

    @no_duplicates
    def test_get_transactions_end_date(self):
        self.client.get_transactions(ACCOUNT_ID, end_date=NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY,
                'endDate': NOW_DATE_ISO})

    @no_duplicates
    def test_get_transactions_end_date_datetime(self):
        self.client.get_transactions(ACCOUNT_ID, end_date=NOW_DATETIME)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/transactions'), params={
                'apikey': API_KEY,
                'endDate': NOW_DATE_ISO})

    @no_duplicates
    def test_get_transactions_end_date_str(self):
        with self.assertRaises(ValueError) as cm:
            self.client.get_transactions(ACCOUNT_ID, end_date='2020-01-01')
        self.assertEqual(str(cm.exception),
                         "expected type in (datetime.date, datetime.datetime) for " +
                         "end_date, got 'builtins.str'")

    # get_preferences

    @no_duplicates
    def test_get_preferences(self):
        self.client.get_preferences(ACCOUNT_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/preferences'), params={
                'apikey': API_KEY})

    @no_duplicates
    def test_get_preferences_str(self):
        self.client.get_preferences(str(ACCOUNT_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/preferences'), params={
                'apikey': API_KEY})

    # get_streamer_subscription_keys

    @no_duplicates
    def test_get_streamer_subscription_keys(self):
        self.client.get_streamer_subscription_keys([1000, 2000, 3000])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/userprincipals/streamersubscriptionkeys'),
            params={
                'apikey': API_KEY,
                'accountIds': '1000,2000,3000'})

    @no_duplicates
    def test_get_streamer_subscription_keys_str(self):
        self.client.get_streamer_subscription_keys(['1000', '2000', '3000'])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/userprincipals/streamersubscriptionkeys'),
            params={
                'apikey': API_KEY,
                'accountIds': '1000,2000,3000'})

    # get_user_principals

    @no_duplicates
    def test_get_user_principals_vanilla(self):
        self.client.get_user_principals()
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/userprincipals'), params={
                'apikey': API_KEY})

    @no_duplicates
    def test_get_user_principals_fields(self):
        self.client.get_user_principals(
            fields=[
                Client.UserPrincipals.Fields.STREAMER_SUBSCRIPTION_KEYS,
                Client.UserPrincipals.Fields.PREFERENCES])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/userprincipals'), params={
                'apikey': API_KEY,
                'fields': 'streamerSubscriptionKeys,preferences'})

    @no_duplicates
    def test_get_user_principals_fields_unchecked(self):
        self.client.set_enforce_enums(False)
        self.client.get_user_principals(
            fields=['streamerSubscriptionKeys', 'preferences'])
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/userprincipals'), params={
                'apikey': API_KEY,
                'fields': 'streamerSubscriptionKeys,preferences'})

    # update_preferences

    @no_duplicates
    def test_update_preferences(self):
        preferences = {'wantMoney': True}
        self.client.update_preferences(ACCOUNT_ID, preferences)
        self.mock_session.put.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/preferences'),
            json=preferences)

    @no_duplicates
    def test_update_preferences_str(self):
        preferences = {'wantMoney': True}
        self.client.update_preferences(str(ACCOUNT_ID), preferences)
        self.mock_session.put.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/preferences'),
            json=preferences)

    # create_watchlist

    @no_duplicates
    def test_create_watchlist(self):
        watchlist = {'AAPL': True}
        self.client.create_watchlist(ACCOUNT_ID, watchlist)
        self.mock_session.post.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists'),
            json=watchlist)

    @no_duplicates
    def test_create_watchlist_str(self):
        watchlist = {'AAPL': True}
        self.client.create_watchlist(str(ACCOUNT_ID), watchlist)
        self.mock_session.post.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists'),
            json=watchlist)

    # delete_watchlist

    @no_duplicates
    def test_delete_watchlist(self):
        watchlist = {'AAPL': True}
        self.client.delete_watchlist(ACCOUNT_ID, WATCHLIST_ID)
        self.mock_session.delete.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists/{watchlistId}'))

    @no_duplicates
    def test_delete_watchlist_str(self):
        watchlist = {'AAPL': True}
        self.client.delete_watchlist(str(ACCOUNT_ID), str(WATCHLIST_ID))
        self.mock_session.delete.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists/{watchlistId}'))

    # get_watchlist

    @no_duplicates
    def test_get_watchlist(self):
        self.client.get_watchlist(ACCOUNT_ID, WATCHLIST_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists/{watchlistId}'),
            params={})

    @no_duplicates
    def test_get_watchlist_str(self):
        self.client.get_watchlist(str(ACCOUNT_ID), str(WATCHLIST_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists/{watchlistId}'),
            params={})

    # get_watchlists_for_multiple_accounts

    @no_duplicates
    def test_get_watchlists_for_multiple_accounts(self):
        self.client.get_watchlists_for_multiple_accounts()
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/watchlists'), params={})

    # get_watchlists_for_single_account

    @no_duplicates
    def test_get_watchlists_for_single_account(self):
        self.client.get_watchlists_for_single_account(ACCOUNT_ID)
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists'), params={})

    @no_duplicates
    def test_get_watchlists_for_single_account_str(self):
        self.client.get_watchlists_for_single_account(str(ACCOUNT_ID))
        self.mock_session.get.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists'), params={})

    # replace_watchlist

    @no_duplicates
    def test_replace_watchlist(self):
        watchlist = {'AAPL': True}
        self.client.replace_watchlist(ACCOUNT_ID, WATCHLIST_ID, watchlist)
        self.mock_session.put.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists/{watchlistId}'),
            json=watchlist)

    @no_duplicates
    def test_replace_watchlist_str(self):
        watchlist = {'AAPL': True}
        self.client.replace_watchlist(
            str(ACCOUNT_ID), str(WATCHLIST_ID), watchlist)
        self.mock_session.put.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists/{watchlistId}'),
            json=watchlist)

    # update_watchlist

    @no_duplicates
    def test_update_watchlist(self):
        watchlist = {'AAPL': True}
        self.client.update_watchlist(ACCOUNT_ID, WATCHLIST_ID, watchlist)
        self.mock_session.patch.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists/{watchlistId}'),
            json=watchlist)

    @no_duplicates
    def test_update_watchlist_str(self):
        watchlist = {'AAPL': True}
        self.client.update_watchlist(
            str(ACCOUNT_ID), str(WATCHLIST_ID), watchlist)
        self.mock_session.patch.assert_called_once_with(
            self.make_url('/v1/accounts/{accountId}/watchlists/{watchlistId}'),
            json=watchlist)
