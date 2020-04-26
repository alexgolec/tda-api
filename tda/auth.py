##########################################################################
# Authentication Wrappers

from requests_oauthlib import OAuth2Session

import pickle
import time

from tda.client import Client


def __token_updater(token_path):
    def update_token(t):
        with open(token_path, 'wb') as f:
            pickle.dump(t, f)
    return update_token


def __normalize_api_key(api_key):
    if not api_key.endswith('@AMER.OAUTHAP'):
        api_key = api_key + '@AMER.OAUTHAP'
    return api_key


def client_from_token_file(token_path, api_key):
    '''Returns a session from the specified token path. The session will
    perform an auth refresh as needed. It will also update the token on disk
    whenever appropriate.

    :param token_path: Path to the token. Updated tokens will be written to this
                       path.
    :param api_key: Your TD Ameritrade application's API key, also known as the
                    client ID.
    '''

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


def client_from_login_flow(webdriver, api_key, redirect_url, token_path,
                           redirect_wait_time_seconds=0.1):
    '''Uses the webdriver to perform an OAuth webapp login flow and creates a
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
    :param token_path: Path to which the new token will be written. Updated
                       tokens will be written to this path as well.
    '''
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

    :param api_key: Your TD Ameritrade application's API key, also known as the
                    client ID.
    :param redirect_url: Your TD Ameritrade application's redirect URL. Note
                         this must *exactly* match the value you've entered in
                         your application configuration, otherwise login will
                         fail with a security error.
    :param token_path: Path that new token will be read from and written to.
                       Updated tokens will be written to this path as well.
    :param webdriver_func: Function that returns a webdriver for use in fetching
                           a new token. Will only be called if the token file
                           cannot be found.
    '''
    api_key = __normalize_api_key(api_key)

    try:
        return client_from_token_file(token_path, api_key)
    except FileNotFoundError:
        if webdriver_func is not None:
            with webdriver_func() as driver:
                return client_from_login_flow(
                    driver, api_key, redirect_uri, token_path)
        else:
            raise
