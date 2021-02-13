'''Implements additional functionality beyond what's implemented in the client
module.'''

import datetime
import dateutil.parser
import httpx
import re


class EnumEnforcer:
    '''Ensures values passed to the enum conversion methods are members of the 
    correct enum type with ``enforce_enums=True``. With ``allow_values=True``, 
    allows directly passing member values instead, but rejects values which are not 
    defined in the relevant enumeration. With `enforce_enums=False`, any value is 
    allowed (and `allow_values` is ignored).

    :param enforce_enums: True to enable parameter validation, False otherwise.
    :param allow_values: True to allow direct passing of enumerated values, False to
        only allow members of the appropriate enum. Ignored with ``enforce_enums=False``.
    '''
    def __init__(self, enforce_enums, allow_values=False):
        self.enforce_enums = enforce_enums
        self.allow_values = allow_values

    def _raise_unrecognized_value(self, value, enum_type):
        error_str = ('Value "{actual}" is not is not enumerated in {enum}. Check the '
                     'official TD Ameritrade API documentation to see what values are '
                     'allowed. If the value you need is missing from {enum}, you can '
                     'disable parameter validation by initializing {subclass} with '
                     'enforce_enums=False. However, if an allowed value is truly not '
                     'enumerated in {enum}, please submit an issue to {repo_url} '
                     'including the name of the enum, a link to the relevant '
                     'official documentation, and the missing value.')
        raise UnrecognizedValueException(
            error_str.format(
                actual=value,
                enum=enum_type.__name__,
                subclass=self.__class__.__name__,
                repo_url="https://github.com/alexgolec/tda-api",
            )
        )

    def _raise_enum_required(self, value, required_enum_type):
        error_str = ('Expected type {expected}, got type "{actual}". Initialize '
                     '{subclass} with allow_values=True to allow direct usage of '
                     'enumerated values, or use enforce_enums=False to disable '
                     'validation altogether. Check the official TD Ameritrade API '
                     'documentation to see what values are allowed. If an allowed '
                     'value is truly not enumerated in {expected}, please submit an '
                     'issue to {repo_url} including the name of the enum, a link to '
                     'the relevant official documentation, and the missing value.')
        raise EnumRequiredException(
            error_str.format(
                expected=required_enum_type.__name__, 
                actual=type(value).__name__,
                subclass=self.__class__.__name__,
                repo_url="https://github.com/alexgolec/tda-api"
            )
        )

    def convert_enum(self, value, required_enum_type, allowed_values=None):
        '''Validate the given ``value`` using ``required_enum_type``.

        With ``self.enforce_enums=True``, check that the given ``value`` is a member of 
        the required type, and return its value if so. 
        
        With ``self.allow_values=True``, also allows ``value`` to be an enumerated value 
        in the required enum type, returning ``value`` back unchanged if so.
        
        With ``self.enforce_enums=False``, if ``value`` is a member of the expected enum,
        returns ``value.value``, otherwise, returns ``value`` unchanged.

        :param value: The object in question.
        :param required_enum_type: The expected enum type.
        :param allowed_values: The set of values which are allowed with 
            ``self.allow_values=True``, or None to use the set of all values enumerated
            in ``required_enum_type``. Providing this set is useful to avoid repeated
            recomputation of allowed values. Ignored if value validation is turned off.
        :raise EnumRequiredException: if ``value`` is not a member of the required enum
            type, ``self.enforce_enums=True``, and ``self.allow_values=False``.
        :raise UnrecognizedValueException: if ``value`` is not a member of the required 
            enum type nor one of its enumerated values, and ``self.enforce_enums=True``,
            and ``self.allow_values=True``.
        :return: either ``value`` or ``value.value`` as appropriate.
        '''
        if value is None:
            return None
        if isinstance(value, required_enum_type):
            return value.value
        if self.enforce_enums:
            if self.allow_values:
                if allowed_values is None:
                    allowed_values = set(member.value for member in required_enum_type)
                if value in allowed_values:
                    return value
                self._raise_unrecognized_value(value, required_enum_type)
            self._raise_enum_required(value, required_enum_type)
        return value

    def convert_enum_iterable(self, iterable, required_enum_type):
        '''Return the ``iterable`` of parameters with all elements converted as needed
           by :meth:`EnumEnforcer.convert_enum_iterable`. 
           
        If ``iterable`` is a member of the appropriate enum (not an iterable), returns a
        list containg ``iterable`` as its only element. This does not work when passing
        values directly--even a single value must be contained in an iterable.
        '''
        if iterable is None:
            return None
        if isinstance(iterable, required_enum_type):
            return [iterable.value]
        allowed_values = set(member.value for member in required_enum_type)
        return [
            self.convert_enum(value, required_enum_type, allowed_values=allowed_values) 
            for value in iterable
        ]

    def set_enforce_enums(self, enforce_enums):
        self.enforce_enums = enforce_enums

class UnrecognizedValueException(ValueError):
    '''
    Raised by :meth:`EnumEnforcer.convert_enum` when a parameter is passed which is
    not enumerated in the required enum type, and value validation is enabled.

    Inherits from ``ValueError``.
    '''


class EnumRequiredException(TypeError, ValueError):
    '''
    Raised by :meth:`EnumEnforcer.convert_enum` when a parameter is passed which is
    not a member of the required enum type and enum-only enforcement is enabled.

    Inherits from both ``TypeError`` and ``ValueError`` for backwards compatibility.
    '''


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
