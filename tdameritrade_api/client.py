from private import api_wrapper


def __token_updater(token_path):
    import pickle
    def update_token(t):
        with open(token_path, 'wb') as f:
            pickle.dump(t, f)
    return update_token


def client_from_token_file(token_path, api_key):
    '''Returns a session from the specified token path. The session will 
    perform an auth refresh as needed. It will also update the token on disk 
    whenever appropriate.'''
    import pickle
    from requests_oauthlib import OAuth2Session

    # Load old token from secrets directory
    with open(token_path, 'rb') as f:
        token = pickle.load(f)

    # Return a new session configured to refresh credentials
    return api_wrapper.BaseClient(
            api_key,
            OAuth2Session(api_key, token=token,
                auto_refresh_url='https://api.tdameritrade.com/v1/oauth2/token',
                auto_refresh_kwargs={'client_id': api_key},
                token_updater=__token_updater(token_path)))


def client_from_login_flow(webdriver, api_key, redirect_uri, token_path):
    '''Uses the webdriver to perform an OAuth webapp login flow and creates a 
    client for that token. The session will perform an auth refresh as needed. 
    It will also update the token on disk where appropriate.'''
    import pickle
    from requests_oauthlib import OAuth2Session

    oauth = OAuth2Session(api_key, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(
            'https://auth.tdameritrade.com/auth')

    # Open the login page and wait for the redirect
    webdriver.get(authorization_url)
    callback_url = ''
    while not callback_url.startswith(redirect_uri):
        import time
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
    return api_wrapper.BaseClient(
            api_key,
            OAuth2Session(api_key, token=token,
                auto_refresh_url='https://api.tdameritrade.com/v1/oauth2/token',
                auto_refresh_kwargs={'client_id': api_key},
                token_updater=update_token))

