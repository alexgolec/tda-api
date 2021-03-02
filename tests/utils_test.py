from unittest.mock import MagicMock
from tda.utils import AccountIdMismatchException, Utils
from tda.utils import UnsuccessfulOrderException
from . import test_utils
from .utils import no_duplicates, MockResponse

import unittest

class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.account_id = 10000
        self.utils = Utils(self.mock_client, self.account_id)

        self.order_id = 1

        self.maxDiff = None

    ##########################################################################
    # extract_order_id tests

    @no_duplicates
    def test_extract_order_id_order_not_ok(self):
        response = MockResponse({}, 403)
        with self.assertRaises(
                UnsuccessfulOrderException, msg='order not successful'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_extract_order_id_no_location(self):
        response = MockResponse({}, 200, headers={})
        self.assertIsNone(self.utils.extract_order_id(response))

    @no_duplicates
    def test_extract_order_id_no_pattern_match(self):
        response = MockResponse({}, 200, headers={
            'Location': 'https://api.tdameritrade.com/v1/accounts/12345'})
        self.assertIsNone(self.utils.extract_order_id(response))

    @no_duplicates
    def test_get_order_nonmatching_account_id(self):
        response = MockResponse({}, 200, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/456'.format(
                self.account_id + 1)})
        with self.assertRaises(
                AccountIdMismatchException,
                msg='order request account ID != Utils.account_id'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_get_order_nonmatching_account_id_str(self):
        self.utils = Utils(self.mock_client, str(self.account_id))

        response = MockResponse({}, 200, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/456'.format(
                self.account_id + 1)})
        with self.assertRaises(
                AccountIdMismatchException,
                msg='order request account ID != Utils.account_id'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_get_order_success_200(self):
        order_id = self.account_id + 100
        response = MockResponse({}, 200, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/{}'.format(
                self.account_id, order_id)})
        self.assertEqual(order_id, self.utils.extract_order_id(response))

    @no_duplicates
    def test_get_order_success_201(self):
        order_id = self.account_id + 100
        response = MockResponse({}, 201, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/{}'.format(
                self.account_id, order_id)})
        self.assertEqual(order_id, self.utils.extract_order_id(response))

    @no_duplicates
    def test_get_order_success_str_account_id(self):
        self.utils = Utils(self.mock_client, str(self.account_id))

        order_id = self.account_id + 100
        response = MockResponse({}, 200, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/{}'.format(
                self.account_id, order_id)})
        self.assertEqual(order_id, self.utils.extract_order_id(response))
