'''Defines the basic client and methods for creating one. This client is
completely unopinionated, and provides an easy-to-use wrapper around the TD
Ameritrade HTTP API.'''

from enum import Enum
from requests_oauthlib import OAuth2Session

import datetime
import json
import logging
import pickle
import tda
import time

from .utils import EnumEnforcer


def get_logger():
    return logging.getLogger(__name__)


##########################################################################
# Client

class Client(EnumEnforcer):
    # This docstring will appears as documentation for __init__
    '''A basic, completely unopinionated client. This client provides the most
    direct access to the API possible. All methods return the raw response which
    was returned by the underlying API call, and the user is responsible for
    checking status codes. For methods which support responses, they can be
    found in the response object's ``json()`` method.'''

    def __init__(self, api_key, session, *, enforce_enums=True):
        '''Create a new client with the given API key and session. Set
        `enforce_enums=False` to disable strict input type checking.'''
        super().__init__(enforce_enums)

        self.api_key = api_key
        self.session = session

        # Logging-related fields
        self.logger = get_logger()
        self.request_number = 0

        tda.LOG_REDACTOR.register(api_key, 'API_KEY')

    # XXX: This class's tests perform monkey patching to inject synthetic values
    # of utcnow(). To avoid being confused by this, capture these values here so
    # we can use them later.
    _DATETIME = datetime.datetime
    _DATE = datetime.date

    def __log_response(self, resp, req_num):
        self.logger.debug('Req {}: GET response: {}, content={}'.format(
            req_num, resp.status_code, resp.text))

    def __req_num(self):
        self.request_number += 1
        return self.request_number

    def __assert_type(self, name, value, exp_types):
        value_type = type(value)
        value_type_name = '{}.{}'.format(
            value_type.__module__, value_type.__name__)
        exp_type_names = ['{}.{}'.format(
            t.__module__, t.__name__) for t in exp_types]
        if not any(isinstance(value, t) for t in exp_types):
            if len(exp_types) == 1:
                error_str = "expected type '{}' for {}, got '{}'".format(
                    exp_type_names[0], name, value_type_name)
            else:
                error_str = "expected type in ({}) for {}, got '{}'".format(
                    ', '.join(exp_type_names), name, value_type_name)
            raise ValueError(error_str)

    def __format_datetime(self, var_name, dt):
        '''Formats datetime objects appropriately, depending on whether they are
        naive or timezone-aware'''
        self.__assert_type(var_name, dt, [self._DATETIME])

        tz_offset = dt.strftime('%z')
        tz_offset = tz_offset if tz_offset else '+0000'

        return dt.strftime('%Y-%m-%dT%H:%M:%S') + tz_offset

    def __format_date(self, var_name, dt):
        '''Formats datetime objects appropriately, depending on whether they are
        naive or timezone-aware'''
        self.__assert_type(var_name, dt, [self._DATE, self._DATETIME])

        d = datetime.date(year=dt.year, month=dt.month, day=dt.day)

        return d.isoformat()

    def __datetime_as_millis(self, var_name, dt):
        'Converts datetime objects to compatible millisecond values'
        self.__assert_type(var_name, dt, [self._DATETIME])

        return int(dt.timestamp() * 1000)

    def __get_request(self, path, params):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self.__req_num()
        self.logger.debug('Req {}: GET to {}, params={}'.format(
            req_num, dest, json.dumps(params, indent=4)))

        resp = self.session.get(dest, params=params)
        self.__log_response(resp, req_num)
        tda.debug.register_redactions_from_response(resp)
        return resp

    def __post_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self.__req_num()
        self.logger.debug('Req {}: POST to {}, json={}'.format(
            req_num, dest, json.dumps(data, indent=4)))

        resp = self.session.post(dest, json=data)
        self.__log_response(resp, req_num)
        tda.debug.register_redactions_from_response(resp)
        return resp

    def __put_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self.__req_num()
        self.logger.debug('Req {}: PUT to {}, json={}'.format(
            req_num, dest, json.dumps(data, indent=4)))

        resp = self.session.put(dest, json=data)
        self.__log_response(resp, req_num)
        tda.debug.register_redactions_from_response(resp)
        return resp

    def __patch_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self.__req_num()
        self.logger.debug('Req {}: PATCH to {}, json={}'.format(
            req_num, dest, json.dumps(data, indent=4)))

        resp = self.session.patch(dest, json=data)
        self.__log_response(resp, req_num)
        tda.debug.register_redactions_from_response(resp)
        return resp

    def __delete_request(self, path):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self.__req_num()
        self.logger.debug('Req {}: DELETE to {}'.format(req_num, dest))

        resp = self.session.delete(dest)
        self.__log_response(resp, req_num)
        tda.debug.register_redactions_from_response(resp)
        return resp

    ##########################################################################
    # Orders

    def cancel_order(self, order_id, account_id):
        '''Cancel a specific order for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/delete/
        accounts/%7BaccountId%7D/orders/%7BorderId%7D-0>`__.'''
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__delete_request(path)

    def get_order(self, order_id, account_id):
        '''Get a specific order for a specific account by its order ID.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/get/accounts/
        %7BaccountId%7D/orders/%7BorderId%7D-0>`__.'''
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__get_request(path, {})

    class Order:
        class Status(Enum):
            '''Order statuses passed to :meth:`get_orders_by_path` and
            :meth:`get_orders_by_query`'''
            AWAITING_PARENT_ORDER = 'AWAITING_PARENT_ORDER'
            AWAITING_CONDITION = 'AWAITING_CONDITION'
            AWAITING_MANUAL_REVIEW = 'AWAITING_MANUAL_REVIEW'
            ACCEPTED = 'ACCEPTED'
            AWAITING_UR_OUR = 'AWAITING_UR_OUR'
            PENDING_ACTIVATION = 'PENDING_ACTIVATION'
            QUEUED = 'QUEUED'
            WORKING = 'WORKING'
            REJECTED = 'REJECTED'
            PENDING_CANCEL = 'PENDING_CANCEL'
            CANCELLED = 'CANCELLED'
            PENDING_REPLACE = 'PENDING_REPLACE'
            REPLACED = 'REPLACED'
            FILLED = 'FILLED'
            EXPIRED = 'EXPIRED'

    def __make_order_query(self,
                           *,
                           max_results=None,
                           from_entered_datetime=None,
                           to_entered_datetime=None,
                           status=None,
                           statuses=None):
        status = self.convert_enum(status, self.Order.Status)
        statuses = self.convert_enum_iterable(statuses, self.Order.Status)

        if status is not None and statuses is not None:
            raise ValueError('at most one of status or statuses may be set')

        if from_entered_datetime is None:
            from_entered_datetime = datetime.datetime(
                year=1900, month=1, day=1)
        if to_entered_datetime is None:
            to_entered_datetime = datetime.datetime.utcnow()

        params = {
            'fromEnteredTime': self.__format_datetime(
                'from_entered_datetime', from_entered_datetime),
            'toEnteredTime': self.__format_datetime(
                'to_entered_datetime', to_entered_datetime),
        }

        if max_results:
            params['maxResults'] = max_results

        if status:
            params['status'] = status
        if statuses:
            params['status'] = ','.join(statuses)

        return params

    def get_orders_by_path(self,
                           account_id,
                           *,
                           max_results=None,
                           from_entered_datetime=None,
                           to_entered_datetime=None,
                           status=None,
                           statuses=None):
        '''Orders for a specific account. At most one of ``status`` and
        ``statuses`` may be set. `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/get/accounts/
        %7BaccountId%7D/orders-0>`__.

        :param max_results: The maximum number of orders to retrieve.
        :param from_entered_datetime: Specifies that no orders entered before
                                      this time should be returned. Date must
                                      be within 60 days from today's date.
                                      ``toEnteredTime`` must also be set.
        :param to_entered_datetime: Specifies that no orders entered after this
                                    time should be returned. ``fromEnteredTime``
                                    must also be set.
        :param status: Restrict query to orders with this status. See
                       :class:`Order.Status` for options.
        :param statuses: Restrict query to orders with any of these statuses.
                         See :class:`Order.Status` for options.
        '''
        path = '/v1/accounts/{}/orders'.format(account_id)
        return self.__get_request(path, self.__make_order_query(
            max_results=max_results,
            from_entered_datetime=from_entered_datetime,
            to_entered_datetime=to_entered_datetime,
            status=status,
            statuses=statuses))

    def get_orders_by_query(self,
                            *,
                            max_results=None,
                            from_entered_datetime=None,
                            to_entered_datetime=None,
                            status=None,
                            statuses=None):
        '''Orders for all linked accounts. At most one of ``status`` and
        ``statuses`` may be set.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/get/orders-0>`__.

        :param max_results: The maximum number of orders to retrieve.
        :param from_entered_datetime: Specifies that no orders entered before
                                      this time should be returned. Date must
                                      be within 60 days from today's date.
                                      ``toEnteredTime`` must also be set.
        :param to_entered_datetime: Specifies that no orders entered after this
                                    time should be returned. ``fromEnteredTime``
                                    must also be set.
        :param status: Restrict query to orders with this status. See
                       :class:`Order.Status` for options.
        :param statuses: Restrict query to orders with any of these statuses.
                         See :class:`Order.Status` for options.
        '''
        path = '/v1/orders'
        return self.__get_request(path, self.__make_order_query(
            max_results=max_results,
            from_entered_datetime=from_entered_datetime,
            to_entered_datetime=to_entered_datetime,
            status=status,
            statuses=statuses))

    def place_order(self, account_id, order_spec):
        '''Place an order for a specific account. If order creation was
        successful, the response will contain the ID of the generated order. See
        :meth:`tda.utils.Utils.extract_order_id` for more details.

        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/post/accounts/
        %7BaccountId%7D/orders-0>`__. '''
        path = '/v1/accounts/{}/orders'.format(account_id)
        return self.__post_request(path, order_spec)

    def replace_order(self, account_id, order_id, order_spec):
        '''Replace an existing order for an account. The existing order will be
        replaced by the new order. Once replaced, the old order will be canceled
        and a new order will be created.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/put/accounts/
        %7BaccountId%7D/orders/%7BorderId%7D-0>`__.'''
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__put_request(path, order_spec)

    ##########################################################################
    # Saved Orders

    def create_saved_order(self, account_id, order_spec):
        '''Save an order for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/post/accounts/
        %7BaccountId%7D/savedorders-0>`__.'''
        path = '/v1/accounts/{}/savedorders'.format(account_id)
        return self.__post_request(path, order_spec)

    def delete_saved_order(self, account_id, order_id):
        '''Delete a specific saved order for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/delete/
        accounts/%7BaccountId%7D/savedorders/%7BsavedOrderId%7D-0>`__.'''
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__delete_request(path)

    def get_saved_order(self, account_id, order_id):
        '''Specific saved order by its ID, for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/get/accounts/
        %7BaccountId%7D/savedorders/%7BsavedOrderId%7D-0>`__.'''
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__get_request(path, {})

    def get_saved_orders_by_path(self, account_id):
        '''Saved orders for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/get/accounts/
        %7BaccountId%7D/savedorders-0>`__.'''
        path = '/v1/accounts/{}/savedorders'.format(account_id)
        return self.__get_request(path, {})

    def replace_saved_order(self, account_id, order_id, order_spec):
        '''Replace an existing saved order for an account. The existing saved
        order will be replaced by the new order.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/put/accounts/
        %7BaccountId%7D/savedorders/%7BsavedOrderId%7D-0>`__.'''
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__put_request(path, order_spec)

    ##########################################################################
    # Accounts

    class Account:
        class Fields(Enum):
            '''Account fields passed to :meth:`get_account` and
            :meth:`get_accounts`'''
            POSITIONS = 'positions'
            ORDERS = 'orders'

    def get_account(self, account_id, *, fields=None):
        '''Account balances, positions, and orders for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/get/accounts/
        %7BaccountId%7D-0>`__.

        :param fields: Balances displayed by default, additional fields can be
                       added here by adding values from :class:`Account.Fields`.
        '''
        fields = self.convert_enum_iterable(fields, self.Account.Fields)

        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        path = '/v1/accounts/{}'.format(account_id)
        return self.__get_request(path, params)

    def get_accounts(self, *, fields=None):
        '''Account balances, positions, and orders for all linked accounts.
        `Official documentation
        <https://developer.tdameritrade.com/account-access/apis/get/
        accounts-0>`__.

        :param fields: Balances displayed by default, additional fields can be
                       added here by adding values from :class:`Account.Fields`.
        '''
        fields = self.convert_enum_iterable(fields, self.Account.Fields)

        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        path = '/v1/accounts'
        return self.__get_request(path, params)

    ##########################################################################
    # Instruments

    class Instrument:
        class Projection(Enum):
            '''Search query type for :func:`search_instruments`. See the
            `official documentation
            <https://developer.tdameritrade.com/instruments/apis/get/
            instruments>`__ for details on the semantics of each.'''
            SYMBOL_SEARCH = 'symbol-search'
            SYMBOL_REGEX = 'symbol-regex'
            DESC_SEARCH = 'desc-search'
            DESC_REGEX = 'desc-regex'
            FUNDAMENTAL = 'fundamental'

    def search_instruments(self, symbols, projection):
        '''Search or retrieve instrument data, including fundamental data.
        `Official documentation
        <https://developer.tdameritrade.com/instruments/apis/get/
        instruments>`__.

        :param projection: Query type. See :class:`Instrument.Projection` for
                            options.
        '''
        projection = self.convert_enum(
            projection, self.Instrument.Projection)

        params = {
            'apikey': self.api_key,
            'symbol': ','.join(symbols),
            'projection': projection,
        }

        path = '/v1/instruments'
        return self.__get_request(path, params)

    def get_instrument(self, cusip):
        '''Get an instrument by CUSIP.
        `Official documentation
        <https://developer.tdameritrade.com/instruments/apis/get/instruments/
        %7Bcusip%7D>`__.'''
        if not isinstance(cusip, str):
            raise ValueError('CUSIPs must be passed as strings to preserve ' +
                             'leading zeroes')

        params = {
            'apikey': self.api_key,
        }

        path = '/v1/instruments/{}'.format(cusip)
        return self.__get_request(path, params)

    ##########################################################################
    # Market Hours

    class Markets(Enum):
        '''Values for :func:`get_hours_for_multiple_markets` and
        :func:`get_hours_for_single_market`.'''
        EQUITY = 'EQUITY'
        OPTION = 'OPTION'
        FUTURE = 'FUTURE'
        BOND = 'BOND'
        FOREX = 'FOREX'

    def get_hours_for_multiple_markets(self, markets, date):
        '''Retrieve market hours for specified markets.
        `Official documentation
        <https://developer.tdameritrade.com/market-hours/apis/get/marketdata/
        hours>`__.

        :param markets: Market to return hours for. Iterable of
                        :class:`Markets`.
        :param date: The date for which market hours information is requested.
                     Accepts ``datetime.date`` and ``datetime.datetime``.
        '''
        markets = self.convert_enum_iterable(markets, self.Markets)

        params = {
            'apikey': self.api_key,
            'markets': ','.join(markets),
            'date': self.__format_date('date', date),
        }

        path = '/v1/marketdata/hours'
        return self.__get_request(path, params)

    def get_hours_for_single_market(self, market, date):
        '''Retrieve market hours for specified single market.
        `Official documentation
        <https://developer.tdameritrade.com/market-hours/apis/get/marketdata/
        %7Bmarket%7D/hours>`__.

        :param markets: Market to return hours for. Instance of
                        :class:`Markets`.
        :param date: The date for which market hours information is requested.
                     Accepts ``datetime.date`` and ``datetime.datetime``.
        '''
        market = self.convert_enum(market, self.Markets)

        params = {
            'apikey': self.api_key,
            'date': self.__format_date('date', date),
        }

        path = '/v1/marketdata/{}/hours'.format(market)
        return self.__get_request(path, params)

    ##########################################################################
    # Movers

    class Movers:
        class Direction(Enum):
            '''Values for :func:`get_movers`'''
            UP = 'up'
            DOWN = 'down'

        class Change(Enum):
            '''Values for :func:`get_movers`'''
            VALUE = 'value'
            PERCENT = 'percent'

    def get_movers(self, index, direction, change):
        '''Top 10 (up or down) movers by value or percent for a particular
        market.
        `Official documentation
        <https://developer.tdameritrade.com/movers/apis/get/marketdata/
        %7Bindex%7D/movers>`__.

        :param direction: See :class:`Movers.Direction`
        :param change: See :class:`Movers.Change`
        '''
        direction = self.convert_enum(direction, self.Movers.Direction)
        change = self.convert_enum(change, self.Movers.Change)

        params = {
            'apikey': self.api_key,
            'direction': direction,
            'change': change,
        }

        path = '/v1/marketdata/{}/movers'.format(index)
        return self.__get_request(path, params)

    ##########################################################################
    # Option Chains

    class Options:
        class ContractType(Enum):
            CALL = 'CALL'
            PUT = 'PUT'
            ALL = 'ALL'

        class Strategy(Enum):
            SINGLE = 'SINGLE'
            ANALYTICAL = 'ANALYTICAL'
            COVERED = 'COVERED'
            VERTICAL = 'VERTICAL'
            CALENDAR = 'CALENDAR'
            STRANGLE = 'STRANGLE'
            STRADDLE = 'STRADDLE'
            BUTTERFLY = 'BUTTERFLY'
            CONDOR = 'CONDOR'
            DIAGONAL = 'DIAGONAL'
            COLLAR = 'COLLAR'
            ROLL = 'ROLL'

        class StrikeRange(Enum):
            IN_THE_MONEY = 'ITM'
            NEAR_THE_MONEY = 'NTM'
            OUT_OF_THE_MONEY = 'OTM'
            STRIKES_ABOVE_MARKET = 'SAK'
            STRIKES_BELOW_MARKET = 'SBK'
            STRIKES_NEAR_MARKET = 'SNK'
            ALL = 'ALL'

        class Type(Enum):
            STANDARD = 'S'
            NON_STANDARD = 'NS'
            ALL = 'ALL'

        class ExpirationMonth(Enum):
            JANUARY = 'JAN'
            FEBRUARY = 'FEB'
            MARCH = 'MAR'
            APRIL = 'APR'
            MAY = 'MAY'
            JUN = 'JUN'
            JULY = 'JUL'
            AUGUST = 'AUG'
            SEPTEMBER = 'SEP'
            OCTOBER = 'OCT'
            NOVEMBER = 'NOV'
            DECEMBER = 'DEC'

    def get_option_chain(
            self,
            symbol,
            *,
            contract_type=None,
            strike_count=None,
            include_quotes=None,
            strategy=None,
            interval=None,
            strike=None,
            strike_range=None,
            strike_from_date=None,
            strike_to_date=None,
            volatility=None,
            underlying_price=None,
            interest_rate=None,
            days_to_expiration=None,
            exp_month=None,
            option_type=None):
        '''Get option chain for an optionable Symbol.
        `Official documentation
        <https://developer.tdameritrade.com/option-chains/apis/get/marketdata/
        chains>`__.

        :param contract_type: Type of contracts to return in the chain. See
                              :class:`Options.ContractType` for choices.
        :param strike_count: The number of strikes to return above and below
                             the at-the-money price.
        :param include_quotes: Include quotes for options in the option chain?
        :param strategy: If passed, returns a Strategy Chain. See
                        :class:`Options.Strategy` for choices.
        :param interval: Strike interval for spread strategy chains (see
                         ``strategy`` param).
        :param strike: Return options only at this strike price.
        :param strike_range: Return options for the given range. See
                             :class:`Options.StrikeRange` for choices.
        :param strike_from_date: Only return expirations after this date. For
                                 strategies, expiration refers to the nearest
                                 term expiration in the strategy. Accepts
                                 ``datetime.date`` and ``datetime.datetime``.
        :param strike_to_date: Only return expirations before this date. For
                               strategies, expiration refers to the nearest
                               term expiration in the strategy. Accepts
                               ``datetime.date`` and ``datetime.datetime``.
        :param volatility: Volatility to use in calculations. Applies only to
                           ``ANALYTICAL`` strategy chains.
        :param underlying_price: Underlying price to use in calculations.
                                 Applies only to ``ANALYTICAL`` strategy chains.
        :param interest_rate: Interest rate to use in calculations. Applies only
                              to ``ANALYTICAL`` strategy chains.
        :param days_to_expiration: Days to expiration to use in calculations.
                                   Applies only to ``ANALYTICAL`` strategy
                                   chains
        :param exp_month: Return only options expiring in the specified month. See
                          :class:`Options.ExpirationMonth` for choices.
        :param option_type: Types of options to return. See
                            :class:`Options.Type` for choices.
        '''
        contract_type = self.convert_enum(
            contract_type, self.Options.ContractType)
        strategy = self.convert_enum(strategy, self.Options.Strategy)
        strike_range = self.convert_enum(
            strike_range, self.Options.StrikeRange)
        option_type = self.convert_enum(option_type, self.Options.Type)
        exp_month = self.convert_enum(exp_month, self.Options.ExpirationMonth)

        params = {
            'apikey': self.api_key,
            'symbol': symbol,
        }

        if contract_type is not None:
            params['contractType'] = contract_type
        if strike_count is not None:
            params['strikeCount'] = strike_count
        if include_quotes is not None:
            params['includeQuotes'] = include_quotes
        if strategy is not None:
            params['strategy'] = strategy
        if interval is not None:
            params['interval'] = interval
        if strike is not None:
            params['strike'] = strike
        if strike_range is not None:
            params['range'] = strike_range
        if strike_from_date is not None:
            params['fromDate'] = self.__format_date(
                'strike_from_date', strike_from_date)
        if strike_to_date is not None:
            params['toDate'] = self.__format_date(
                'strike_to_date', strike_to_date)
        if volatility is not None:
            params['volatility'] = volatility
        if underlying_price is not None:
            params['underlyingPrice'] = underlying_price
        if interest_rate is not None:
            params['interestRate'] = interest_rate
        if days_to_expiration is not None:
            params['daysToExpiration'] = days_to_expiration
        if exp_month is not None:
            params['expMonth'] = exp_month
        if option_type is not None:
            params['optionType'] = option_type

        path = '/v1/marketdata/chains'
        return self.__get_request(path, params)

    ##########################################################################
    # Price History

    class PriceHistory:
        class PeriodType(Enum):
            DAY = 'day'
            MONTH = 'month'
            YEAR = 'year'
            YEAR_TO_DATE = 'ytd'

        class Period(Enum):
            # Daily
            ONE_DAY = 1
            TWO_DAYS = 2
            THREE_DAYS = 3
            FOUR_DAYS = 4
            FIVE_DAYS = 5
            TEN_DAYS = 10

            # Monthly
            ONE_MONTH = 1
            TWO_MONTHS = 2
            THREE_MONTHS = 3
            SIX_MONTHS = 6

            # Year
            ONE_YEAR = 1
            TWO_YEARS = 2
            THREE_YEARS = 3
            FIVE_YEARS = 5
            TEN_YEARS = 10
            FIFTEEN_YEARS = 15
            TWENTY_YEARS = 20

            # Year to date
            YEAR_TO_DATE = 1

        class FrequencyType(Enum):
            MINUTE = 'minute'
            DAILY = 'daily'
            WEEKLY = 'weekly'
            MONTHLY = 'monthly'

        class Frequency(Enum):
            # Minute
            EVERY_MINUTE = 1
            EVERY_FIVE_MINUTES = 5
            EVERY_TEN_MINUTES = 10
            EVERY_FIFTEEN_MINUTES = 15
            EVERY_THIRTY_MINUTES = 30

            # Other frequencies
            DAILY = 1
            WEEKLY = 1
            MONTHLY = 1

    def get_price_history(
            self,
            symbol,
            *,
            period_type=None,
            period=None,
            frequency_type=None,
            frequency=None,
            start_datetime=None,
            end_datetime=None,
            need_extended_hours_data=None):
        '''Get price history for a symbol.
        `Official documentation
        <https://developer.tdameritrade.com/price-history/apis/get/marketdata/
        %7Bsymbol%7D/pricehistory>`__.

        :param period_type: The type of period to show.
        :param period: The number of periods to show. Should not be provided if
                       ``start_datetime`` and ``end_datetime``.
        :param frequency_type: The type of frequency with which a new candle
                               is formed.
        :param frequency: The number of the frequencyType to be included in each
                          candle.
        :param start_datetime: End date. Default is previous trading day.
        :param end_datetime: Start date.
        :param need_extended_hours_data: If true, return extended hours data.
                                         Otherwise return regular market hours
                                         only.
        '''
        period_type = self.convert_enum(
            period_type, self.PriceHistory.PeriodType)
        period = self.convert_enum(period, self.PriceHistory.Period)
        frequency_type = self.convert_enum(
            frequency_type, self.PriceHistory.FrequencyType)
        frequency = self.convert_enum(
            frequency, self.PriceHistory.Frequency)

        params = {
            'apikey': self.api_key,
        }

        if period_type is not None:
            params['periodType'] = period_type
        if period is not None:
            params['period'] = period
        if frequency_type is not None:
            params['frequencyType'] = frequency_type
        if frequency is not None:
            params['frequency'] = frequency
        if start_datetime is not None:
            params['startDate'] = self.__datetime_as_millis(
                'start_datetime', start_datetime)
        if end_datetime is not None:
            params['endDate'] = self.__datetime_as_millis(
                'end_datetime', end_datetime)
        if need_extended_hours_data is not None:
            params['needExtendedHoursData'] = need_extended_hours_data

        path = '/v1/marketdata/{}/pricehistory'.format(symbol)
        return self.__get_request(path, params)

    ##########################################################################
    # Quotes

    def get_quote(self, symbol):
        '''
        Get quote for a symbol. Note due to limitations in URL encoding, this
        method is not recommended for instruments with symbols symbols
        containing non-alphanumeric characters, for example as futures like
        ``/ES``. To get quotes for those symbols, use :meth:`Client.get_quotes`.

        `Official documentation
        <https://developer.tdameritrade.com/quotes/apis/get/marketdata/
        %7Bsymbol%7D/quotes>`__.
        '''
        params = {
            'apikey': self.api_key,
        }

        import urllib
        path = '/v1/marketdata/{}/quotes'.format(symbol)
        return self.__get_request(path, params)

    def get_quotes(self, symbols):
        '''Get quote for a symbol. This method supports all symbols, including
        those containing non-alphanumeric characters like ``/ES``.
        `Official documentation
        <https://developer.tdameritrade.com/quotes/apis/get/marketdata/
        quotes>`__.'''
        params = {
            'apikey': self.api_key,
            'symbol': ','.join(symbols)
        }

        path = '/v1/marketdata/quotes'
        return self.__get_request(path, params)

    ##########################################################################
    # Transaction History

    def get_transaction(self, account_id, transaction_id):
        '''Transaction for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/transaction-history/apis/get/
        accounts/%7BaccountId%7D/transactions/%7BtransactionId%7D-0>`__.'''
        params = {
            'apikey': self.api_key,
        }

        path = '/v1/accounts/{}/transactions/{}'.format(
            account_id, transaction_id)
        return self.__get_request(path, params)

    class Transactions:
        class TransactionType(Enum):
            ALL = 'ALL'
            TRADE = 'TRADE'
            BUY_ONLY = 'BUY_ONLY'
            SELL_ONLY = 'SELL_ONLY'
            CASH_IN_OR_CASH_OUT = 'CASH_IN_OR_CASH_OUT'
            CHECKING = 'CHECKING'
            DIVIDEND = 'DIVIDEND'
            INTEREST = 'INTEREST'
            OTHER = 'OTHER'
            ADVISORY_FEES = 'ADVISORY_FEES'

    def get_transactions(
            self,
            account_id,
            *,
            transaction_type=None,
            symbol=None,
            start_date=None,
            end_date=None):
        '''Transaction for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/transaction-history/apis/get/
        accounts/%7BaccountId%7D/transactions-0>`__.

        :param transaction_type: Only transactions with the specified type will
                                  be returned.
        :param symbol: Only transactions with the specified symbol will be
                        returned.
        :param start_date: Only transactions after this date will be returned.
                           Note the maximum date range is one year.
                           Accepts ``datetime.date`` and ``datetime.datetime``.
        :param end_date: Only transactions before this date will be returned
                         Note the maximum date range is one year.
                         Accepts ``datetime.date`` and ``datetime.datetime``.
        '''
        transaction_type = self.convert_enum(
            transaction_type, self.Transactions.TransactionType)

        params = {
            'apikey': self.api_key,
        }

        if transaction_type is not None:
            params['type'] = transaction_type
        if symbol is not None:
            params['symbol'] = symbol
        if start_date is not None:
            params['startDate'] = self.__format_date('start_date', start_date)
        if end_date is not None:
            params['endDate'] = self.__format_date('end_date', end_date)

        path = '/v1/accounts/{}/transactions'.format(account_id)
        return self.__get_request(path, params)

    ##########################################################################
    # User Info and Preferences

    def get_preferences(self, account_id):
        '''Preferences for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/user-principal/apis/get/accounts/
        %7BaccountId%7D/preferences-0>`__.'''
        params = {
            'apikey': self.api_key,
        }

        path = '/v1/accounts/{}/preferences'.format(account_id)
        return self.__get_request(path, params)

    def get_streamer_subscription_keys(self, account_ids):
        '''SubscriptionKey for provided accounts or default accounts.
        `Official documentation
        <https://developer.tdameritrade.com/user-principal/apis/get/
        userprincipals/streamersubscriptionkeys-0>`__.'''
        params = {
            'apikey': self.api_key,
            'accountIds': ','.join(str(i) for i in account_ids)
        }

        path = '/v1/userprincipals/streamersubscriptionkeys'
        return self.__get_request(path, params)

    class UserPrincipals:
        class Fields(Enum):
            STREAMER_SUBSCRIPTION_KEYS = 'streamerSubscriptionKeys'
            STREAMER_CONNECTION_INFO = 'streamerConnectionInfo'
            PREFERENCES = 'preferences'
            SURROGATE_IDS = 'surrogateIds'

    def get_user_principals(self, fields=None):
        '''User Principal details.
        `Official documentation
        <https://developer.tdameritrade.com/user-principal/apis/get/
        userprincipals-0>`__.'''
        fields = self.convert_enum_iterable(
            fields, self.UserPrincipals.Fields)

        params = {
            'apikey': self.api_key,
        }

        if fields is not None:
            params['fields'] = ','.join(fields)

        path = '/v1/userprincipals'
        return self.__get_request(path, params)

    def update_preferences(self, account_id, preferences):
        '''Update preferences for a specific account.

        Please note that the directOptionsRouting and directEquityRouting values
        cannot be modified via this operation.
        `Official documentation
        <https://developer.tdameritrade.com/user-principal/apis/put/accounts/
        %7BaccountId%7D/preferences-0>`__.'''
        path = '/v1/accounts/{}/preferences'.format(account_id)
        return self.__put_request(path, preferences)

    ##########################################################################
    # Watchlist

    def create_watchlist(self, account_id, watchlist_spec):
        ''''Create watchlist for specific account.This method does not verify
        that the symbol or asset type are valid.
        `Official documentation
        <https://developer.tdameritrade.com/watchlist/apis/post/accounts/
        %7BaccountId%7D/watchlists-0>`__.'''
        path = '/v1/accounts/{}/watchlists'.format(account_id)
        return self.__post_request(path, watchlist_spec)

    def delete_watchlist(self, account_id, watchlist_id):
        '''Delete watchlist for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/watchlist/apis/delete/accounts/
        %7BaccountId%7D/watchlists/%7BwatchlistId%7D-0>`__.'''
        path = '/v1/accounts/{}/watchlists/{}'.format(account_id, watchlist_id)
        return self.__delete_request(path)

    def get_watchlist(self, account_id, watchlist_id):
        '''Specific watchlist for a specific account.
        `Official documentation
        <https://developer.tdameritrade.com/watchlist/apis/get/accounts/
        %7BaccountId%7D/watchlists/%7BwatchlistId%7D-0>`__.'''
        path = '/v1/accounts/{}/watchlists/{}'.format(account_id, watchlist_id)
        return self.__get_request(path, params={})

    def get_watchlists_for_multiple_accounts(self):
        '''All watchlists for all of the user\'s linked accounts.
        `Official documentation
        <https://developer.tdameritrade.com/watchlist/apis/get/accounts/
        watchlists-0>`__.'''
        path = '/v1/accounts/watchlists'
        return self.__get_request(path, params={})

    def get_watchlists_for_single_account(self, account_id):
        '''All watchlists of an account.
        `Official documentation
        <https://developer.tdameritrade.com/watchlist/apis/get/accounts/
        %7BaccountId%7D/watchlists-0>`__.'''
        path = '/v1/accounts/{}/watchlists'.format(account_id)
        return self.__get_request(path, params={})

    def replace_watchlist(self, account_id, watchlist_id, watchlist_spec):
        '''Replace watchlist for a specific account. This method does not verify
        that the symbol or asset type are valid.
        `Official documentation
        <https://developer.tdameritrade.com/watchlist/apis/put/accounts/
        %7BaccountId%7D/watchlists/%7BwatchlistId%7D-0>`__.'''
        path = '/v1/accounts/{}/watchlists/{}'.format(account_id, watchlist_id)
        return self.__put_request(path, watchlist_spec)

    def update_watchlist(self, account_id, watchlist_id, watchlist_spec):
        '''Partially update watchlist for a specific account: change watchlist
        name, add to the beginning/end of a watchlist, update or delete items in
        a watchlist. This method does not verify that the symbol or asset type
        are valid.
        `Official documentation
        <https://developer.tdameritrade.com/watchlist/apis/patch/accounts/
        %7BaccountId%7D/watchlists/%7BwatchlistId%7D-0>`__.'''
        path = '/v1/accounts/{}/watchlists/{}'.format(account_id, watchlist_id)
        return self.__patch_request(path, watchlist_spec)
