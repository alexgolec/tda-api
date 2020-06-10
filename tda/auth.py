##########################################################################
# Authentication Wrappers

from requests_oauthlib import OAuth2Session

import logging
import pickle
import time

from tda.client import Client
from tda.debug import register_redactions


def get_logger():
    return logging.getLogger(__name__)


def __token_updater(token_path):
    def update_token(t):
        get_logger().info('Updating token to file {}'.format(token_path))

        with open(token_path, 'wb') as f:
            pickle.dump(t, f)
    return update_token


def __normalize_api_key(api_key):
    api_key_suffix = '@AMER.OAUTHAP'

    if not api_key.endswith(api_key_suffix):
        get_logger().info('Appending {} to API key'.format(api_key_suffix))
        api_key = api_key + api_key_suffix
    return api_key


def __register_token_redactions(token):
    register_redactions(token)


def client_from_token_file(token_path, api_key):
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
    # Load old token from secrets directory
    with open(token_path, 'rb') as f:
        token = pickle.load(f)

    # Don't emit token details in debug logs
    __register_token_redactions(token)

    # Return a new session configured to refresh credentials
    return Client(
        api_key,
        OAuth2Session(api_key, token=token,
                      auto_refresh_url='https://api.tdameritrade.com/v1/oauth2/token',
                      auto_refresh_kwargs={'client_id': api_key},
                      token_updater=__token_updater(token_path)))


def client_from_login_flow(webdriver, api_key, redirect_url, token_path,
                           redirect_wait_time_seconds=0.1):
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

    oauth = OAuth2Session(api_key, redirect_uri=redirect_url)
    authorization_url, state = oauth.authorization_url(
        'https://auth.tdameritrade.com/auth')

    # Open the login page and wait for the redirect
    print('Opening the login page in a webdriver. Please use this window to',
          'log in. Successful login will be detected automatically.')
    print('If you encounter any issues, see here for troubleshooting: ' +
          'https://tda-api.readthedocs.io/en/latest/auth.html' +
          '#troubleshooting')

    webdriver.get(authorization_url)
    callback_url = ''
    while not callback_url.startswith(redirect_url):
        callback_url = webdriver.current_url
        time.sleep(redirect_wait_time_seconds)

    token = oauth.fetch_token(
        'https://api.tdameritrade.com/v1/oauth2/token',
        authorization_response=callback_url,
        access_type='offline',
        client_id=api_key,
        include_client_id=True)

    # Don't emit token details in debug logs
    __register_token_redactions(token)

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


def easy_client(api_key, redirect_uri, token_path, webdriver_func=None):
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
    api_key = __normalize_api_key(api_key)
    logger = get_logger()

    try:
        c = client_from_token_file(token_path, api_key)
        logger.info('Returning client loaded from token file \'{}\''.format(
            token_path))
        return c
    except FileNotFoundError:
        logger.info('Failed to find token file \'{}\''.format(token_path))

        if webdriver_func is not None:
            with webdriver_func() as driver:
                c = client_from_login_flow(
                    driver, api_key, redirect_uri, token_path)
                logger.info(
                    'Returning client fetched using webdriver, writing' +
                    'token to \'{}\''.format(token_path))
                return c
        else:
            logger.info('No webdriver_func set, returning')
            raise
