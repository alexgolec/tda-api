##########################################################################
# Authentication Wrappers

from authlib.integrations.httpx_client import AsyncOAuth2Client, OAuth2Client

import json
import logging
import os
import pickle
import sys
import time
import warnings

from tda.client import AsyncClient, Client
from tda.debug import register_redactions


TOKEN_ENDPOINT = 'https://api.tdameritrade.com/v1/oauth2/token'


def get_logger():
    return logging.getLogger(__name__)


def __update_token(token_path):
    def update_token(t, *args, **kwargs):
        get_logger().info('Updating token to file {}'.format(token_path))

        with open(token_path, 'w') as f:
            json.dump(t, f)
    return update_token


def __token_loader(token_path):
    def load_token():
        get_logger().info('Loading token from file {}'.format(token_path))

        with open(token_path, 'rb') as f:
            token_data = f.read()
            try:
                return json.loads(token_data.decode())
            except ValueError:
                get_logger().warning(
                    "Unable to load JSON token from file {}, falling back to pickle"
                    .format(token_path)
                )
                return pickle.loads(token_data)
    return load_token


def __normalize_api_key(api_key):
    api_key_suffix = '@AMER.OAUTHAP'

    if not api_key.endswith(api_key_suffix):
        get_logger().info('Appending {} to API key'.format(api_key_suffix))
        api_key = api_key + api_key_suffix
    return api_key


def _register_token_redactions(token):
    register_redactions(token)


def client_from_token_file(token_path, api_key, asyncio=False):
    '''
    Returns a session from an existing token file. The session will perform
    an auth refresh as needed. It will also update the token on disk whenever
    appropriate.

    :param token_path: Path to an existing token. Updated tokens will be written
                       to this path. If you do not yet have a token, use
                       :func:`~tda.auth.client_from_login_flow` or
                       :func:`~tda.auth.easy_client` to create one.
    :param api_key: Your TD Ameritrade application's API key, also known as the
                    client ID.
    '''

    load = __token_loader(token_path)

    return client_from_access_functions(
        api_key, load, __update_token(token_path), asyncio=asyncio)


def __fetch_and_register_token_from_redirect(
        oauth, redirected_url, api_key, token_path, token_write_func, asyncio):
    token = oauth.fetch_token(
        TOKEN_ENDPOINT,
        authorization_response=redirected_url,
        access_type='offline',
        client_id=api_key,
        include_client_id=True)

    # Don't emit token details in debug logs
    _register_token_redactions(token)

    # Set up token writing and perform the initial token write
    update_token = (
        __update_token(token_path) if token_write_func is None
        else token_write_func)
    metadata_manager = TokenMetadata(int(time.time()), update_token)
    update_token = metadata_manager.wrapped_token_write_func()
    update_token(token)

    if asyncio:
        session_class = AsyncOAuth2Client
        client_class = AsyncClient
    else:
        session_class = OAuth2Client
        client_class = Client

    # Return a new session configured to refresh credentials
    return client_class(
        api_key,
        session_class(api_key, token=token,
                      auto_refresh_url=TOKEN_ENDPOINT,
                      auto_refresh_kwargs={'client_id': api_key},
                      update_token=update_token),
        token_metadata=metadata_manager)


class RedirectTimeoutError(Exception):
    pass


class TokenMetadata:
    '''
    Provides the functionality required to maintain and update our view of the
    token's metadata.
    '''
    # XXX: Token metadata is currently not considered sensitive enough to wrap
    #      register for redactions. If we add anything sensitive to the token
    #      metadata, we'll need to update the redaction registration logic.

    def __init__(self, creation_timestamp, unwrapped_token_write_func=None):
        self.creation_timestamp = creation_timestamp

        # The token write function is ultimately stored in the session. When we
        # get a new token we immediately wrap it in a new sesssion. We hold on
        # to the unwrapped token writer function to allow us to inject the
        # appropriate write function.
        self.unwrapped_token_write_func = unwrapped_token_write_func

    @classmethod
    def from_loaded_token(cls, token, unwrapped_token_write_func=None):
        '''
        Returns a new ``TokenMetadata`` object extracted from the metadata of
        the loaded token object. If the token has a legacy format which contains
        no metadata, assign default values.
        '''
        if cls.is_metadata_aware_token(token):
            return TokenMetadata(
                token['creation_timestamp'], unwrapped_token_write_func)
        elif cls.is_legacy_token(token):
            return TokenMetadata(None, unwrapped_token_write_func)
        else:
            get_logger().warn('Unrecognized token format')
            return TokenMetadata(None, unwrapped_token_write_func)

    @classmethod
    def is_legacy_token(cls, token):
        return 'creation_timestamp' not in token

    @classmethod
    def is_metadata_aware_token(cls, token):
        return 'creation_timestamp' in token and 'token' in token

    def wrapped_token_write_func(self):
        '''
        Hook the call to the token write function so that the write function is
        passed the metadata-aware version of the token.
        '''
        def wrapped_token_write_func(token, *args, **kwargs):
            return self.unwrapped_token_write_func(
                self.wrap_token_in_metadata(token), *args, **kwargs)
        return wrapped_token_write_func

    def wrap_token_in_metadata(self, token):
        return {
            'creation_timestamp': self.creation_timestamp,
            'token': token,
        }

    def ensure_refresh_token_update(
            self, api_key, session, update_interval_seconds=None):
        '''
        If the refresh token is older than update_interval_seconds, update it by
        issuing a call to the token refresh endpoint and return a new session
        wrapped around the resulting token. Returns None if the refresh token
        was not updated.
        '''
        if update_interval_seconds is None:
            # 85 days is less than the documented 90 day expiration window of
            # the token, but hopefully long enough to not trigger TDA's
            # thresholds for excessive refresh token updates.
            update_interval_seconds = 60 * 60 * 24 * 85

        if not (self.creation_timestamp is None
                or time.time() - self.creation_timestamp >
                update_interval_seconds):
            return None

        old_token = session.token
        oauth = OAuth2Client(api_key)

        new_token = oauth.fetch_token(
            TOKEN_ENDPOINT,
            grant_type='refresh_token',
            refresh_token=old_token['refresh_token'],
            access_type='offline')

        self.creation_timestamp = int(time.time())

        # Don't emit token details in debug logs
        _register_token_redactions(new_token)

        token_write_func = self.wrapped_token_write_func()
        token_write_func(new_token)

        session_class = session.__class__
        return session_class(
            api_key,
            token=new_token,
            token_endpoint=TOKEN_ENDPOINT,
            update_token=token_write_func)


# TODO: Raise an exception when passing both token_path and token_write_func
def client_from_login_flow(webdriver, api_key, redirect_url, token_path,
                           redirect_wait_time_seconds=0.1, max_waits=3000,
                           asyncio=False, token_write_func=None):
    '''
    Uses the webdriver to perform an OAuth webapp login flow and creates a
    client wrapped around the resulting token. The client will be configured to
    refresh the token as necessary, writing each updated version to
    ``token_path``.

    :param webdriver: `selenium <https://selenium-python.readthedocs.io>`__
                      webdriver which will be used to perform the login flow.
    :param api_key: Your TD Ameritrade application's API key, also known as the
                    client ID.
    :param redirect_url: Your TD Ameritrade application's redirect URL. Note
                         this must *exactly* match the value you've entered in
                         your application configuration, otherwise login will
                         fail with a security error.
    :param token_path: Path to which the new token will be written. If the token
                       file already exists, it will be overwritten with a new
                       one. Updated tokens will be written to this path as well.
    '''
    get_logger().info(('Creating new token with redirect URL \'{}\' ' +
                       'and token path \'{}\'').format(redirect_url, token_path))

    api_key = __normalize_api_key(api_key)

    oauth = OAuth2Client(api_key, redirect_uri=redirect_url)
    authorization_url, state = oauth.create_authorization_url(
        'https://auth.tdameritrade.com/auth')

    # Open the login page and wait for the redirect
    print('\n**************************************************************\n')
    print('Opening the login page in a webdriver. Please use this window to',
          'log in. Successful login will be detected automatically.')
    print()
    print('If you encounter any issues, see here for troubleshooting: ' +
          'https://tda-api.readthedocs.io/en/stable/auth.html' +
          '#troubleshooting')
    print('\n**************************************************************\n')

    webdriver.get(authorization_url)

    # Tolerate redirects to HTTPS on the callback URL
    if redirect_url.startswith('http://'):
        print(('WARNING: Your redirect URL ({}) will transmit data over HTTP, ' +
               'which is a potentially severe security vulnerability. ' +
               'Please go to your app\'s configuration with TDAmeritrade ' +
               'and update your redirect URL to begin with \'https\' ' +
               'to stop seeing this message.').format(redirect_url))

        redirect_urls = (redirect_url, 'https' + redirect_url[4:])
    else:
        redirect_urls = (redirect_url,)

    # Wait until the current URL starts with the callback URL
    current_url = ''
    num_waits = 0
    while not any(current_url.startswith(r_url) for r_url in redirect_urls):
        current_url = webdriver.current_url

        if num_waits > max_waits:
            raise RedirectTimeoutError('timed out waiting for redirect')
        time.sleep(redirect_wait_time_seconds)
        num_waits += 1

    return __fetch_and_register_token_from_redirect(
        oauth, current_url, api_key, token_path, token_write_func,
        asyncio)


def client_from_manual_flow(api_key, redirect_url, token_path,
                            asyncio=False, token_write_func=None):
    '''
    Walks the user through performing an OAuth login flow by manually
    copy-pasting URLs, and returns a client wrapped around the resulting token.
    The client will be configured to refresh the token as necessary, writing
    each updated version to ``token_path``.

    Note this method is more complicated and error prone, and should be avoided
    in favor of :func:`client_from_login_flow` wherever possible.

    :param api_key: Your TD Ameritrade application's API key, also known as the
                    client ID.
    :param redirect_url: Your TD Ameritrade application's redirect URL. Note
                         this must *exactly* match the value you've entered in
                         your application configuration, otherwise login will
                         fail with a security error.
    :param token_path: Path to which the new token will be written. If the token
                       file already exists, it will be overwritten with a new
                       one. Updated tokens will be written to this path as well.
    '''
    get_logger().info(('Creating new token with redirect URL \'{}\' ' +
                       'and token path \'{}\'').format(redirect_url, token_path))

    api_key = __normalize_api_key(api_key)

    oauth = OAuth2Client(api_key, redirect_uri=redirect_url)
    authorization_url, state = oauth.create_authorization_url(
        'https://auth.tdameritrade.com/auth')

    print('\n**************************************************************\n')
    print('This is the manual login and token creation flow for tda-api.')
    print('Please follow these instructions exactly:')
    print()
    print(' 1. Open the following link by copy-pasting it into the browser')
    print('    of your choice:')
    print()
    print('        ' + authorization_url)
    print()
    print(' 2. Log in with your account credentials. You may be asked to')
    print('    perform two-factor authentication using text messaging or')
    print('    another method, as well as whether to trust the browser.')
    print()
    print(' 3. When asked whether to allow your app access to your account,')
    print('    select "Allow".')
    print()
    print(' 4. Your browser should be redirected to your redirect URI. Copy')
    print('    the ENTIRE address, paste it into the following prompt, and press')
    print('    Enter/Return.')
    print()
    print('If you encounter any issues, see here for troubleshooting:')
    print('https://tda-api.readthedocs.io/en/stable/auth.html')
    print('#troubleshooting')
    print('\n**************************************************************\n')

    if redirect_url.startswith('http://'):
        print(('WARNING: Your redirect URL ({}) will transmit data over HTTP, ' +
               'which is a potentially severe security vulnerability. ' +
               'Please go to your app\'s configuration with TDAmeritrade ' +
               'and update your redirect URL to begin with \'https\' ' +
               'to stop seeing this message.').format(redirect_url))

    # Workaround for Mac OS freezing on reading nput
    import platform
    if platform.system() == 'Darwin':  # pragma: no cover
        import readline

    redirected_url = input('Redirect URL> ').strip()

    return __fetch_and_register_token_from_redirect(
        oauth, redirected_url, api_key, token_path, token_write_func,
        asyncio)


def easy_client(api_key, redirect_uri, token_path, webdriver_func=None,
                asyncio=False):
    '''Convenient wrapper around :func:`client_from_login_flow` and
    :func:`client_from_token_file`. If ``token_path`` exists, loads the token
    from it. Otherwise open a login flow to fetch a new token. Returns a client
    configured to refresh the token to ``token_path``.

    *Reminder:* You should never create the token file yourself or modify it in
    any way. If ``token_path`` refers to an existing file, this method will
    assume that file is valid token and will attempt to parse it.

    :param api_key: Your TD Ameritrade application's API key, also known as the
                    client ID.
    :param redirect_url: Your TD Ameritrade application's redirect URL. Note
                         this must *exactly* match the value you've entered in
                         your application configuration, otherwise login will
                         fail with a security error.
    :param token_path: Path that new token will be read from and written to. If
                       If this file exists, this method will assume it's valid
                       and will attempt to parse it as a token. If it does not,
                       this method will create a new one using
                       :func:`~tda.auth.client_from_login_flow`. Updated tokens
                       will be written to this path as well.
    :param webdriver_func: Function that returns a webdriver for use in fetching
                           a new token. Will only be called if the token file
                           cannot be found.
    '''
    logger = get_logger()

    if os.path.isfile(token_path):
        c = client_from_token_file(token_path, api_key, asyncio=asyncio)
        logger.info('Returning client loaded from token file \'{}\''.format(
            token_path))
        return c
    else:
        logger.warning('Failed to find token file \'{}\''.format(token_path))

        if webdriver_func is not None:
            with webdriver_func() as driver:
                c = client_from_login_flow(
                    driver, api_key, redirect_uri, token_path, asyncio=asyncio)
                logger.info(
                    'Returning client fetched using webdriver, writing' +
                    'token to \'{}\''.format(token_path))
                return c
        else:
            logger.error('No webdriver_func set, cannot fetch token')
            sys.exit(1)


def client_from_access_functions(api_key, token_read_func,
                                 token_write_func=None, asyncio=False):
    '''
    Returns a session from an existing token file, using the accessor methods to
    read and write the token. This is an advanced method for users who do not
    have access to a standard writable filesystem, such as users of AWS Lambda
    and other serverless products who must persist token updates on
    non-filesystem places, such as S3. 99.9% of users should not use this
    function.

    Users are free to customize how they represent the token file. In theory,
    since they have direct access to the token, they can get creative about how
    they store it and fetch it. In practice, it is *highly* recommended to
    simply accept the token object and use ``pickle`` to serialize and
    deserialize it, without inspecting it in any way.

    :param api_key: Your TD Ameritrade application's API key, also known as the
                    client ID.
    :param token_read_func: Function that takes no arguments and returns a token
                            object.
    :param token_write_func: Function that a token object and writes it. Will be
                             called whenever the token is updated, such as when
                             it is refreshed. Optional, but *highly*
                             recommended. Note old tokens become unusable on
                             refresh, so not setting this parameter risks
                             permanently losing refreshed tokens.
    '''
    token = token_read_func()

    # Extract metadata and unpack the token, if necessary
    metadata = TokenMetadata.from_loaded_token(token, token_write_func)
    if TokenMetadata.is_metadata_aware_token(token):
        token = token['token']

    # Don't emit token details in debug logs
    _register_token_redactions(token)

    # Return a new session configured to refresh credentials
    api_key = __normalize_api_key(api_key)

    session_kwargs = {
        'token': token,
        'token_endpoint': TOKEN_ENDPOINT,
    }

    if token_write_func is not None:
        wrapped_token_write_func = metadata.wrapped_token_write_func()
        session_kwargs['update_token'] = wrapped_token_write_func

    if asyncio:
        session_class = AsyncOAuth2Client
        client_class = AsyncClient
    else:
        session_class = OAuth2Client
        client_class = Client

    return client_class(
        api_key,
        session_class(api_key, **session_kwargs),
        token_metadata=metadata)
