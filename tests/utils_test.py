from unittest.mock import MagicMock

import datetime
import json
import unittest

from tda.orders import EquityOrderBuilder
from tda.utils import Utils
from . import test_utils
from .test_utils import no_duplicates, MockResponse


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
        response = MockResponse({}, False)
        with self.assertRaises(ValueError, msg='order not successful'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_extract_order_id_no_location(self):
        response = MockResponse({}, True, headers={})
        self.assertIsNone(self.utils.extract_order_id(response))

    @no_duplicates
    def test_extract_order_id_no_pattern_match(self):
        response = MockResponse({}, True, headers={
            'Location': 'https://api.tdameritrade.com/v1/accounts/12345'})
        self.assertIsNone(self.utils.extract_order_id(response))

    @no_duplicates
    def test_get_order_nonmatching_account_id(self):
        response = MockResponse({}, True, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/456'.format(
                self.account_id + 1)})
        with self.assertRaises(
                ValueError, msg='order request account ID != Utils.account_id'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_get_order_nonmatching_account_id_str(self):
        self.utils = Utils(self.mock_client, str(self.account_id))

        response = MockResponse({}, True, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/456'.format(
                self.account_id + 1)})
        with self.assertRaises(
                ValueError, msg='order request account ID != Utils.account_id'):
            self.utils.extract_order_id(response)

    @no_duplicates
    def test_get_order_success(self):
        order_id = self.account_id + 100
        response = MockResponse({}, True, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/{}'.format(
                self.account_id, order_id)})
        self.assertEqual(order_id, self.utils.extract_order_id(response))

    @no_duplicates
    def test_get_order_success_str_account_id(self):
        self.utils = Utils(self.mock_client, str(self.account_id))

        order_id = self.account_id + 100
        response = MockResponse({}, True, headers={
            'Location':
            'https://api.tdameritrade.com/v1/accounts/{}/orders/{}'.format(
                self.account_id, order_id)})
        self.assertEqual(order_id, self.utils.extract_order_id(response))
