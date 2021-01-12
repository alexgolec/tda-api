##########################################################################
# Authentication Wrappers

from authlib.integrations.httpx_client import AsyncOAuth2Client, OAuth2Client

import json
import logging
import os
import pickle
import sys
import time

from tda.client import AsyncClient, Client
from tda.debug import register_redactions


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


def __register_token_redactions(token):
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


class RedirectTimeoutError(Exception):
    pass


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

    token = oauth.fetch_token(
        'https://api.tdameritrade.com/v1/oauth2/token',
        authorization_response=current_url,
        access_type='offline',
        client_id=api_key,
        include_client_id=True)

    # Don't emit token details in debug logs
    __register_token_redactions(token)

    # Record the token
    update_token = (
        __update_token(token_path) if token_write_func is None
        else token_write_func)
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
                      auto_refresh_url='https://api.tdameritrade.com/v1/oauth2/token',
                      auto_refresh_kwargs={'client_id': api_key},
                      update_token=update_token))


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

    # Don't emit token details in debug logs
    __register_token_redactions(token)

    # Return a new session configured to refresh credentials
    api_key = __normalize_api_key(api_key)

    session_kwargs = {
        'token': token,
        'token_endpoint': 'https://api.tdameritrade.com/v1/oauth2/token',
    }

    if token_write_func is not None:
        session_kwargs['update_token'] = token_write_func

    if asyncio:
        session_class = AsyncOAuth2Client
        client_class = AsyncClient
    else:
        session_class = OAuth2Client
        client_class = Client

    return client_class(
        api_key,
        session_class(api_key, **session_kwargs))
