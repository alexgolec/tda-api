from enum import Enum

from unittest.mock import MagicMock
from tda.utils import (
    Utils,
    EnumEnforcer,
    AccountIdMismatchException, 
    UnsuccessfulOrderException,
    UnrecognizedValueException,
    EnumRequiredException,
)
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


class FooEnum(Enum):
    FOO = "something"
    BAR = "somethingelse"
    BAZ = "anotherthing"


class AlphabetEnum(Enum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5


class EnumEnforcerTest(unittest.TestCase):

    def setUp(self):
        self.enforcers = {
            'strict':  EnumEnforcer(True),
            'value': EnumEnforcer(True, True),
            'permissive': EnumEnforcer(False),
            'alt_permissive': EnumEnforcer(False, True),
        }

    def assert_enforcers_return_or_raise(self, method, args, kwargs, return_mapping):
        '''Assert that, when the EnumEnforcer ``method`` is called with the given 
        ``args`` and ``kwargs``, each enforcer named in ``return_mapping`` returns 
        the value or raises the exception type in ``return_mapping[name]``. For the
        sake of simplicity, iterables must be lists for this method to check them.'''
        for name, ret_val in return_mapping.items():
            identifier = (
                "Test of EnumEnforcer '{enforcer}': {method}(*{args}, **{kwargs}) "
                "Expected: {ret_val}"
            ).format(
                enforcer=name, 
                method=method.__name__, 
                args=args, 
                kwargs=kwargs, 
                ret_val=ret_val,
            )
            with self.subTest(description=identifier):
                if isinstance(ret_val, type) and issubclass(ret_val, Exception):
                    with self.assertRaises(ret_val):
                        method(self.enforcers[name], *args, **kwargs)
                elif isinstance(ret_val, list):
                    self.assertListEqual(
                        method(self.enforcers[name], *args, **kwargs), 
                        ret_val
                    )
                else:
                    self.assertEqual(
                        method(self.enforcers[name], *args, **kwargs),
                        ret_val
                    )


    def test_convert_enum_valid_foo_member(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum,
            args=(FooEnum.FOO, FooEnum),
            kwargs={},
            return_mapping={
                'strict': FooEnum.FOO.value,
                'value': FooEnum.FOO.value,
                'permissive': FooEnum.FOO.value,
                'alt_permissive': FooEnum.FOO.value,
            }
        )

    def test_convert_enum_valid_alph_member(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum,
            args=(AlphabetEnum.C, AlphabetEnum),
            kwargs={},
            return_mapping={
                'strict': 3,
                'value': 3,
                'permissive': 3,
                'alt_permissive': 3,
            }
        )

    def test_convert_enum_wrong_type(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum,
            args=(AlphabetEnum.C, FooEnum),
            kwargs={},
            return_mapping={
                'strict': EnumRequiredException,
                'value': UnrecognizedValueException,
                'permissive': AlphabetEnum.C,
                'alt_permissive': AlphabetEnum.C,
            }
        )

    def test_convert_enum_with_valid_value(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum,
            args=('somethingelse', FooEnum),
            kwargs={},
            return_mapping={
                'strict': EnumRequiredException,
                'value': 'somethingelse',
                'permissive': 'somethingelse',
                'alt_permissive': 'somethingelse',
            }
        )
    
    def test_convert_enum_with_invalid_value(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum,
            args=('I am not valid.', FooEnum),
            kwargs={},
            return_mapping={
                'strict': EnumRequiredException,
                'value': UnrecognizedValueException,
                'permissive': 'I am not valid.',
                'alt_permissive': 'I am not valid.',
            }
        )

    def test_convert_enum_uses_allowed_values(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum,
            args=(2, AlphabetEnum),
            kwargs={'allowed_values': set([5])},
            return_mapping={
                'strict': EnumRequiredException,
                'value': UnrecognizedValueException,
                'permissive': 2,
                'alt_permissive': 2,
            }
        )

    def test_convert_enum_iterable_with_valid_members(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum_iterable,
            args=([FooEnum.BAZ, FooEnum.FOO, FooEnum.BAR], FooEnum),
            kwargs={},
            return_mapping={
                'strict': ['anotherthing', 'something', 'somethingelse'],
                'value': ['anotherthing', 'something', 'somethingelse'],
                'permissive': ['anotherthing', 'something', 'somethingelse'],
                'alt_permissive': ['anotherthing', 'something', 'somethingelse'],
            }
        )
    
    def test_convert_enum_iterable_with_wrong_member(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum_iterable,
            args=([FooEnum.BAZ, AlphabetEnum.A, FooEnum.BAR], FooEnum),
            kwargs={},
            return_mapping={
                'strict': EnumRequiredException,
                'value': UnrecognizedValueException,
                'permissive': ['anotherthing', AlphabetEnum.A, 'somethingelse'],
                'alt_permissive': ['anotherthing', AlphabetEnum.A, 'somethingelse'],
            }
        )

    def test_convert_enum_iterable_with_valid_values(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum_iterable,
            args=([3, 2], AlphabetEnum),
            kwargs={},
            return_mapping={
                'strict': EnumRequiredException,
                'value': [3, 2],
                'permissive': [3, 2],
                'alt_permissive': [3, 2],
            }
        )

    def test_convert_enum_iterable_with_invalid_values(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum_iterable,
            args=([71, 2], AlphabetEnum),
            kwargs={},
            return_mapping={
                'strict': EnumRequiredException,
                'value': UnrecognizedValueException,
                'permissive': [71, 2],
                'alt_permissive': [71, 2],
            }
        )

    def test_convert_enum_iterable_with_lone_member(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum_iterable,
            args=(AlphabetEnum.A, AlphabetEnum),
            kwargs={},
            return_mapping={
                'strict': [1],
                'value': [1],
                'permissive': [1],
                'alt_permissive': [1],
            }
        )

    def test_convert_enum_iterable_with_lone_value(self):
        self.assert_enforcers_return_or_raise(
            method=EnumEnforcer.convert_enum_iterable,
            args=(2, AlphabetEnum),
            kwargs={},
            return_mapping={
                'strict': TypeError,
                'value': TypeError,
                'permissive': TypeError,
                'alt_permissive': TypeError,
            }
        )
