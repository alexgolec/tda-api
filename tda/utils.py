'''Implements additional functionality beyond what's implemented in the client
module.'''

import datetime
import dateutil.parser
import enum
import httpx
import inspect
import re


def class_fullname(o):
    return o.__module__ + '.' + o.__name__


class EnumEnforcer:
    def __init__(self, enforce_enums):
        self.enforce_enums = enforce_enums

    def type_error(self, value, required_enum_type):
        possible_members_message = ''

        if isinstance(value, str):
            possible_members = []
            for member in required_enum_type.__members__:
                fullname = class_fullname(required_enum_type) + '.' + member
                if value in fullname:
                    possible_members.append(fullname)

            # Oxford comma insertion
            if possible_members:
                possible_members_message = 'Did you mean ' + ', '.join(
                    possible_members[:-2] + [' or '.join(
                        possible_members[-2:])]) + '? '

        raise ValueError(
            ('expected type "{}", got type "{}". {}(initialize with ' +
             'enforce_enums=False to disable this checking)').format(
                required_enum_type.__name__,
                type(value).__name__,
                possible_members_message))

    def convert_enum(self, value, required_enum_type):
        if value is None:
            return None

        if isinstance(value, required_enum_type):
            return value.value
        elif self.enforce_enums:
            self.type_error(value, required_enum_type)
        else:
            return value

    def convert_enum_iterable(self, iterable, required_enum_type):
        if iterable is None:
            return None

        if isinstance(iterable, required_enum_type):
            return [iterable.value]

        values = []
        for value in iterable:
            if isinstance(value, required_enum_type):
                values.append(value.value)
            elif self.enforce_enums:
                self.type_error(value, required_enum_type)
            else:
                values.append(value)
        return values

    def set_enforce_enums(self, enforce_enums):
        self.enforce_enums = enforce_enums


class UnsuccessfulOrderException(ValueError):
    '''
    Raised by :meth:`Utils.extract_order_id` when attempting to extract an
    order ID from a :meth:`Client.place_order` response that was not successful.
    '''


class AccountIdMismatchException(ValueError):
    '''
    Raised by :meth:`Utils.extract_order_id` when attempting to extract an
    order ID from a :meth:`Client.place_order` with a different account ID than
    the one with which the :class:`Utils` was initialized.
    '''


class Utils(EnumEnforcer):
    '''Helper for placing orders on equities. Provides easy-to-use
    implementations for common tasks such as market and limit orders.'''

    def __init__(self, client, account_id):
        '''Creates a new ``Utils`` instance. For convenience, this object
        assumes the user wants to work with a single account ID at a time.'''
        super().__init__(True)

        self.client = client
        self.account_id = account_id

    def set_account_id(self, account_id):
        '''Set the account ID used by this ``Utils`` instance.'''
        self.account_id = account_id

    def extract_order_id(self, place_order_response):
        '''Attempts to extract the order ID from a response object returned by
        :meth:`Client.place_order() <tda.client.Client.place_order>`. Return
        ``None`` if the order location is not contained in the response.

        :param place_order_response: Order response as returned by
                                     :meth:`Client.place_order()
                                     <tda.client.Client.place_order>`. Note this
                                     method requires that the order was
                                     successful.

        :raise ValueError: if the order was not succesful or if the order's
                           account ID is not equal to the account ID set in this
                           ``Utils`` object.

        '''
        if place_order_response.is_error:
            raise UnsuccessfulOrderException(
                'order not successful: status {}'.format(place_order_response.status_code))

        try:
            location = place_order_response.headers['Location']
        except KeyError:
            return None

        m = re.match(
            r'https://api.tdameritrade.com/v1/accounts/(\d+)/orders/(\d+)',
            location)

        if m is None:
            return None
        account_id, order_id = int(m.group(1)), int(m.group(2))

        if str(account_id) != str(self.account_id):
            raise AccountIdMismatchException(
                'order request account ID != Utils.account_id')

        return order_id
