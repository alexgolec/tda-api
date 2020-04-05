from enum import Enum, unique
from requests_oauthlib import OAuth2Session

import datetime
import pickle
import time


##########################################################################
# Authentication Wrappers


def __token_updater(token_path):
    def update_token(t):
        with open(token_path, 'wb') as f:
            pickle.dump(t, f)
    return update_token


def client_from_token_file(token_path, api_key):
    '''Returns a session from the specified token path. The session will
    perform an auth refresh as needed. It will also update the token on disk
    whenever appropriate.'''

    # Load old token from secrets directory
    with open(token_path, 'rb') as f:
        token = pickle.load(f)

    # Return a new session configured to refresh credentials
    return Client(
        api_key,
        OAuth2Session(api_key, token=token,
                      auto_refresh_url='https://api.tdameritrade.com/v1/oauth2/token',
                      auto_refresh_kwargs={'client_id': api_key},
                      token_updater=__token_updater(token_path)))


def client_from_login_flow(webdriver, api_key, redirect_uri, token_path):
    '''Uses the webdriver to perform an OAuth webapp login flow and creates a
    client for that token. The session will perform an auth refresh as needed.
    It will also update the token on disk where appropriate.'''
    oauth = OAuth2Session(api_key, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(
        'https://auth.tdameritrade.com/auth')

    # Open the login page and wait for the redirect
    webdriver.get(authorization_url)
    callback_url = ''
    while not callback_url.startswith(redirect_uri):
        callback_url = webdriver.current_url
        time.sleep(1)

    token = oauth.fetch_token(
        'https://api.tdameritrade.com/v1/oauth2/token',
        authorization_response=callback_url,
        access_type='offline',
        client_id=api_key,
        include_client_id=True)

    # Record the token
    update_token = __token_updater(token_path)
    update_token(token)

    # Return a new session configured to refresh credentials
    return Client(
        api_key,
        OAuth2Session(api_key, token=token,
                      auto_refresh_url='https://api.tdameritrade.com/v1/oauth2/token',
                      auto_refresh_kwargs={'client_id': api_key},
                      token_updater=update_token))


##########################################################################
# Client

class Client:
    '''A basic, completely unopinionated client. This client provides the most
    direct access to the API possible. All methods return the raw response which
    was returned by the underlying API call, and the user is responsible for
    checking status codes. For methdods which support responses, they can be
    found in the response object's `json()` method.'''

    def __init__(self, api_key, session, *, enforce_enums=True):
        self.api_key = api_key
        self.session = session
        self.enforce_enums = enforce_enums

    def set_enforce_enums(self, enforce_enums):
        self.enforce_enums = enforce_enums

    def __format_datetime(self, dt):
        '''Formats datetime objects appropriately, depending on whether they are
        naive or timezone-aware'''
        tz_offset = dt.strftime('%z')
        tz_offset = tz_offset if tz_offset else '+0000'

        return dt.strftime('%Y-%m-%dT%H:%M:%S') + tz_offset

    def __format_date(self, dt):
        '''Formats datetime objects appropriately, depending on whether they are
        naive or timezone-aware'''
        d = datetime.date(year=dt.year, month=dt.month, day=dt.day)

        return d.isoformat()

    def __datetime_as_millis(self, dt):
        'Converts datetime objects to compatible millisecond values'
        return int(dt.timestamp() * 1000)

    def __get_request(self, path, params):
        dest = 'https://api.tdameritrade.com' + path
        resp = self.session.get(dest, params=params)
        return resp

    def __post_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path
        return self.session.post(dest, json=data)

    def __put_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path
        return self.session.put(dest, json=data)

    def __patch_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path
        return self.session.patch(dest, json=data)

    def __delete_request(self, path):
        dest = 'https://api.tdameritrade.com' + path
        return self.session.delete(dest)

    def __type_error(self, value, required_enum_type):
        raise ValueError(
            ('expected type "{}", got type "{}" (initialize with ' +
             'enforce_enums=True to disable this checking)').format(
                required_enum_type.__name__,
                type(value).__name__))

    def __convert_enum(self, value, required_enum_type):
        if value is None:
            return None

        if isinstance(value, required_enum_type):
            return value.value
        elif self.enforce_enums:
            self.__type_error(value, required_enum_type)
        else:
            return value

    def __convert_enum_iterable(self, iterable, required_enum_type):
        if iterable is None:
            return None

        values = []
        for value in iterable:
            if isinstance(value, required_enum_type):
                values.append(value.value)
            elif self.enforce_enums:
                self.__type_error(value, required_enum_type)
            else:
                values.append(value)
        return values

    ##########################################################################
    # Orders

    def cancel_order(self, order_id, account_id):
        'Cancel a specific order for a specific account.'
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__delete_request(path)

    def get_order(self, order_id, account_id):
        'Get a specific order for a specific account.'
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__get_request(path, {})

    class Order:
        class Status(Enum):
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
        status = self.__convert_enum(status, self.Order.Status)
        statuses = self.__convert_enum_iterable(statuses, self.Order.Status)

        if from_entered_datetime is None:
            from_entered_datetime = datetime.datetime.min
        if to_entered_datetime is None:
            to_entered_datetime = datetime.datetime.utcnow()

        params = {
            'fromEnteredTime': self.__format_datetime(from_entered_datetime),
            'toEnteredTime': self.__format_datetime(to_entered_datetime),
        }

        if max_results:
            params['maxResults'] = max_results

        if status is not None and statuses is not None:
            raise ValueError('at most one of status or statuses may be set')
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
        'Orders for a specific account.'
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
        'Orders for a specific account.'
        path = '/v1/orders'
        return self.__get_request(path, self.__make_order_query(
            max_results=max_results,
            from_entered_datetime=from_entered_datetime,
            to_entered_datetime=to_entered_datetime,
            status=status,
            statuses=statuses))

    def place_order(self, account_id, order_spec):
        'Place an order for a specific account.'
        path = '/v1/accounts/{}/orders'.format(account_id)
        return self.__post_request(path, order_spec)

    def replace_order(self, account_id, order_id, order_spec):
        '''Replace an existing order for an account. The existing order will be
        replaced by the new order. Once replaced, the old order will be canceled
        and a new order will be created.'''
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__put_request(path, order_spec)

    ##########################################################################
    # Saved Orders

    def create_saved_order(self, account_id, order_spec):
        'Save an order for a specific account.'
        path = '/v1/accounts/{}/savedorders'.format(account_id)
        return self.__post_request(path, order_spec)

    def delete_saved_order(self, account_id, order_id):
        'Delete a specific saved order for a specific account.'
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__delete_request(path)

    def get_saved_order(self, account_id, order_id):
        'Specific saved order by its ID, for a specific account.'
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__get_request(path, {})

    def get_saved_orders_by_path(self, account_id):
        'Saved orders for a specific account.'
        path = '/v1/accounts/{}/savedorders'.format(account_id)
        return self.__get_request(path, {})

    def replace_saved_order(self, account_id, order_id, order_spec):
        '''Replace an existing saved order for an account. The existing saved
        order will be replaced by the new order.'''
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__put_request(path, order_spec)

    ##########################################################################
    # Accounts

    class Account:
        class Fields(Enum):
            POSITIONS = 'positions'
            ORDERS = 'orders'

    def get_account(self, account_id, *, fields=None):
        'Account balances, positions, and orders for a specific account.'
        fields = self.__convert_enum_iterable(fields, self.Account.Fields)

        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        path = '/v1/accounts/{}'.format(account_id)
        return self.__get_request(path, params)

    def get_accounts(self, *, fields=None):
        'Account balances, positions, and orders for a specific account.'
        fields = self.__convert_enum_iterable(fields, self.Account.Fields)

        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        path = '/v1/accounts'
        return self.__get_request(path, params)

    ##########################################################################
    # Instruments

    class Instrument:
        class Projection(Enum):
            SYMBOL_SEARCH = 'symbol-search'
            SYMBOL_REGEX = 'symbol-regex'
            DESC_SEARCH = 'desc-search'
            DESC_REGEX = 'desc-regex'
            FUNDAMENTAL = 'fundamental'

    def search_instruments(self, symbol, projection):
        'Search or retrieve instrument data, including fundamental data.'
        projection = self.__convert_enum(projection, self.Instrument.Projection)

        params = {
            'apikey': self.api_key,
            'symbol': symbol,
            'projection': projection,
        }

        path = '/v1/instruments'
        return self.__get_request(path, params)

    def get_instrument(self, cusip):
        'Get an instrument by CUSIP'
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
        EQUITY = 'EQUITY'
        OPTION = 'OPTION'
        FUTURE = 'FUTURE'
        BOND = 'BOND'
        FOREX = 'FOREX'

    def get_hours_for_multiple_markets(self, markets, date):
        'Retrieve market hours for specified markets'
        markets = self.__convert_enum_iterable(markets, self.Markets)

        params = {
            'apikey': self.api_key,
            'markets': ','.join(markets),
            'date': self.__format_datetime(date),
        }
        print(params)

        path = '/v1/marketdata/hours'
        return self.__get_request(path, params)

    def get_hours_for_single_market(self, market, date):
        'Retrieve market hours for specified single market'
        market = self.__convert_enum(market, self.Markets)

        params = {
            'apikey': self.api_key,
            'date': self.__format_datetime(date),
        }
        print(params)

        path = '/v1/marketdata/{}/hours'.format(market)
        return self.__get_request(path, params)

    ##########################################################################
    # Movers

    class Movers:
        class Direction(Enum):
            UP = 'up'
            DOWN = 'down'

        class Change(Enum):
            VALUE = 'value'
            PERCENT = 'percent'

    def get_movers(self, index, direction, change):
        'Search or retrieve instrument data, including fundamental data.'
        direction = self.__convert_enum(direction, self.Movers.Direction)
        change = self.__convert_enum(change, self.Movers.Change)

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
        'Get option chain for an optionable Symbol'
        strategy = self.__convert_enum(strategy, self.Options.Strategy)
        strike_range = self.__convert_enum(
            strike_range, self.Options.StrikeRange)
        option_type = self.__convert_enum(option_type, self.Options.Type)

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
            params['fromDate'] = self.__format_datetime(strike_from_date)
        if strike_to_date is not None:
            params['toDate'] = self.__format_datetime(strike_to_date)
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
            start_date=None,
            end_date=None,
            need_extended_hours_data=None):
        'Get price history for a symbol'
        period_type = self.__convert_enum(
            period_type, self.PriceHistory.PeriodType)
        period = self.__convert_enum(period, self.PriceHistory.Period)
        frequency_type = self.__convert_enum(
            frequency_type, self.PriceHistory.FrequencyType)
        frequency = self.__convert_enum(
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
        if start_date is not None:
            params['startDate'] = self.__datetime_as_millis(start_date)
        if end_date is not None:
            params['endDate'] = self.__datetime_as_millis(end_date)
        if need_extended_hours_data is not None:
            params['needExtendedHoursData'] = need_extended_hours_data

        path = '/v1/marketdata/{}/pricehistory'.format(symbol)
        return self.__get_request(path, params)

    ##########################################################################
    # Quotes

    def get_quote(self, symbol):
        'Get quote for a symbol'
        params = {
            'apikey': self.api_key,
        }

        path = '/v1/marketdata/{}/quotes'.format(symbol)
        return self.__get_request(path, params)

    def get_quotes(self, symbols):
        'Get quote for a symbol'
        params = {
            'apikey': self.api_key,
            'symbol': ','.join(symbols)
        }

        path = '/v1/marketdata/quotes'
        return self.__get_request(path, params)

    ##########################################################################
    # Transaction History

    def get_transaction(self, account_id, transaction_id):
        'Transaction for a specific account.'
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
        'Transaction for a specific account.'
        transaction_type = self.__convert_enum(
            transaction_type, self.Transactions.TransactionType)

        params = {
            'apikey': self.api_key,
        }

        if transaction_type is not None:
            params['type'] = transaction_type
        if symbol is not None:
            params['symbol'] = symbol
        if start_date is not None:
            params['startDate'] = self.__format_date(start_date)
        if end_date is not None:
            params['endDate'] = self.__format_date(end_date)

        path = '/v1/accounts/{}/transactions'.format(account_id)
        return self.__get_request(path, params)

    ##########################################################################
    # User Info and Preferences

    def get_preferences(self, account_id):
        'Preferences for a specific account.'
        params = {
            'apikey': self.api_key,
        }

        path = '/v1/accounts/{}/preferences'.format(account_id)
        return self.__get_request(path, params)

    def get_streamer_subscription_keys(self, account_ids):
        'SubscriptionKey for provided accounts or default accounts.'
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
        'User Principal details.'
        fields = self.__convert_enum_iterable(
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
        cannot be modified via this operation.'''
        path = '/v1/accounts/{}/preferences'.format(account_id)
        return self.__put_request(path, preferences)

    ##########################################################################
    # Watchlist

    def create_watchlist(self, account_id, watchlist_spec):
        ''''Create watchlist for specific account.This method does not verify
        that the symbol or asset type are valid.'''
        path = '/v1/accounts/{}/watchlists'.format(account_id)
        return self.__post_request(path, watchlist_spec)

    def delete_watchlist(self, account_id, watchlist_id):
        'Delete watchlist for a specific account.'
        path = '/v1/accounts/{}/watchlists/{}'.format(account_id, watchlist_id)
        return self.__delete_request(path)

    def get_watchlist(self, account_id, watchlist_id):
        'Specific watchlist for a specific account.'
        path = '/v1/accounts/{}/watchlists/{}'.format(account_id, watchlist_id)
        return self.__get_request(path, params={})

    def get_watchlists_for_multiple_accounts(self):
        'All watchlists for all of the user\'s linked accounts.'
        path = '/v1/accounts/watchlists'
        return self.__get_request(path, params={})

    def get_watchlists_for_single_account(self, account_id):
        'All watchlists of an account.'
        path = '/v1/accounts/{}/watchlists'.format(account_id)
        return self.__get_request(path, params={})

    def replace_watchlist(self, account_id, watchlist_id, watchlist_spec):
        '''Replace watchlist for a specific account. This method does not verify
        that the symbol or asset type are valid. '''
        path = '/v1/accounts/{}/watchlists/{}'.format(account_id, watchlist_id)
        return self.__put_request(path, watchlist_spec)

    def update_watchlist(self, account_id, watchlist_id, watchlist_spec):
        '''Partially update watchlist for a specific account: change watchlist
        name, add to the beginning/end of a watchlist, update or delete items in
        a watchlist. This method does not verify that the symbol or asset type
        are valid.'''
        path = '/v1/accounts/{}/watchlists/{}'.format(account_id, watchlist_id)
        return self.__patch_request(path, watchlist_spec)
