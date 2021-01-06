from tda import auth
from .utils import no_duplicates
from unittest.mock import patch, ANY, MagicMock
from unittest.mock import ANY as _

import json
import os
import pickle
import tempfile
import unittest


API_KEY = 'APIKEY@AMER.OAUTHAP'


class ClientFromTokenFileTest(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pickle_path = os.path.join(self.tmp_dir.name, 'token.pickle')
        self.json_path = os.path.join(self.tmp_dir.name, 'token.json')
        self.token = {'token': 'yes'}

    def write_token(self):
        with open(self.pickle_path, 'wb') as f:
            pickle.dump(self.token, f)
        with open(self.json_path, 'w') as f:
            json.dump(self.token, f)

    @no_duplicates
    def test_no_such_file(self):
        with self.assertRaises(FileNotFoundError):
            auth.client_from_token_file(self.json_path, API_KEY)

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_pickle_loads(self, session, client):
        self.write_token()

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_token_file(self.pickle_path, API_KEY))
        client.assert_called_once_with(API_KEY, _)
        session.assert_called_once_with(
            API_KEY,
            token=self.token,
            token_endpoint=_,
            update_token=_)

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_json_loads(self, session, client):
        self.write_token()

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_token_file(self.json_path, API_KEY))
        client.assert_called_once_with(API_KEY, _)
        session.assert_called_once_with(
            API_KEY,
            token=self.token,
            token_endpoint=_,
            update_token=_)

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_update_token_updates_token(self, session, client):
        self.write_token()

        auth.client_from_token_file(self.json_path, API_KEY)
        session.assert_called_once()

        session_call = session.mock_calls[0]
        update_token = session_call[2]['update_token']

        updated_token = {'updated': 'token'}
        update_token(updated_token)
        with open(self.json_path, 'r') as f:
            self.assertEqual(json.load(f), updated_token)


    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_api_key_is_normalized(self, session, client):
        self.write_token()

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_token_file(self.json_path, 'API_KEY'))
        client.assert_called_once_with('API_KEY@AMER.OAUTHAP', _)
        session.assert_called_once_with(
            'API_KEY@AMER.OAUTHAP',
            token=self.token,
            token_endpoint=_,
            update_token=_)


class ClientFromAccessFunctionsTest(unittest.TestCase):

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_success_with_write_func(self, session, client):
        token = {'token': 'yes'}

        token_read_func = MagicMock()
        token_read_func.return_value = token

        token_write_func = MagicMock()

        client.return_value = 'returned client'
        self.assertEqual('returned client',
                         auth.client_from_access_functions(
                             'API_KEY@AMER.OAUTHAP',
                             token_read_func,
                             token_write_func))

        session.assert_called_once_with(
            'API_KEY@AMER.OAUTHAP',
            token=token,
            token_endpoint=_,
            update_token=_)
        token_read_func.assert_called_once()

        # Verify that the write function is called when the updater is called
        session_call = session.mock_calls[0]
        update_token = session_call[2]['update_token']
        token_write_func.assert_not_called()
        update_token()
        token_write_func.assert_called_once()


    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_success_no_write_func(self, session, client):
        token = {'token': 'yes'}

        token_read_func = MagicMock()
        token_read_func.return_value = token

        client.return_value = 'returned client'
        self.assertEqual('returned client',
                         auth.client_from_access_functions(
                             'API_KEY@AMER.OAUTHAP',
                             token_read_func))

        session.assert_called_once_with(
            'API_KEY@AMER.OAUTHAP',
            token=token,
            token_endpoint=_)
        token_read_func.assert_called_once()


REDIRECT_URL = 'https://redirect.url.com'


class ClientFromLoginFlow(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.json_path = os.path.join(self.tmp_dir.name, 'token.json')
        self.token = {'token': 'yes'}


    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_no_token_file_https(self, session_constructor, client):
        AUTH_URL = 'https://auth.url.com'

        session = MagicMock()
        session_constructor.return_value = session
        session.create_authorization_url.return_value = AUTH_URL, None
        session.fetch_token.return_value = self.token

        webdriver = MagicMock()
        webdriver.current_url = REDIRECT_URL + '/token_params'

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_login_flow(
                             webdriver, API_KEY, REDIRECT_URL,
                             self.json_path,
                             redirect_wait_time_seconds=0.0))

        with open(self.json_path, 'r') as f:
            self.assertEqual(self.token, json.load(f))

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_no_token_file_http(self, session_constructor, client):
        AUTH_URL = 'https://auth.url.com'

        redirect_url = 'http://redirect.url.com'

        session = MagicMock()
        session_constructor.return_value = session
        session.create_authorization_url.return_value = AUTH_URL, None
        session.fetch_token.return_value = self.token

        webdriver = MagicMock()
        webdriver.current_url = redirect_url + '/token_params'

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_login_flow(
                             webdriver, API_KEY, redirect_url,
                             self.json_path,
                             redirect_wait_time_seconds=0.0))

        with open(self.json_path, 'r') as f:
            self.assertEqual(self.token, json.load(f))

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_no_token_file_http_redirected_to_https(
            self, session_constructor, client):
        AUTH_URL = 'https://auth.url.com'

        redirect_url = 'http://redirect.url.com'
        redirect_url_https = 'https://redirect.url.com'

        session = MagicMock()
        session_constructor.return_value = session
        session.create_authorization_url.return_value = AUTH_URL, None
        session.fetch_token.return_value = self.token

        webdriver = MagicMock()
        webdriver.current_url = redirect_url_https + '/token_params'

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_login_flow(
                             webdriver, API_KEY, redirect_url,
                             self.json_path,
                             redirect_wait_time_seconds=0.0))

        with open(self.json_path, 'r') as f:
            self.assertEqual(self.token, json.load(f))

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_normalize_api_key(self, session_constructor, client):
        AUTH_URL = 'https://auth.url.com'

        session = MagicMock()
        session_constructor.return_value = session
        session.create_authorization_url.return_value = AUTH_URL, None
        session.fetch_token.return_value = self.token

        webdriver = MagicMock()
        webdriver.current_url = REDIRECT_URL + '/token_params'

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_login_flow(
                             webdriver, 'API_KEY', REDIRECT_URL,
                             self.json_path,
                             redirect_wait_time_seconds=0.0))

        self.assertEqual(
                'API_KEY@AMER.OAUTHAP',
                session_constructor.call_args[0][0])


    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_unexpected_redirect_url(self, session_constructor, client):
        AUTH_URL = 'https://auth.url.com'

        redirect_url = 'http://redirect.url.com'

        session = MagicMock()
        session_constructor.return_value = session
        session.create_authorization_url.return_value = AUTH_URL, None
        session.fetch_token.return_value = self.token

        webdriver = MagicMock()
        webdriver.current_url = 'https://bogus.com' + '/token_params'

        with self.assertRaisesRegex(auth.RedirectTimeoutError,
                'timed out waiting for redirect'):
            auth.client_from_login_flow(
                    webdriver, API_KEY, redirect_url,
                    self.json_path,
                    redirect_wait_time_seconds=0.0)


    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Client')
    def test_custom_token_write_func(self, session_constructor, client):
        AUTH_URL = 'https://auth.url.com'

        session = MagicMock()
        session_constructor.return_value = session
        session.create_authorization_url.return_value = AUTH_URL, None
        session.fetch_token.return_value = self.token

        webdriver = MagicMock()
        webdriver.current_url = REDIRECT_URL + '/token_params'

        client.return_value = 'returned client'

        def dummy_token_write_func(*args, **kwargs):
            pass

        self.assertEqual('returned client',
                         auth.client_from_login_flow(
                             webdriver, API_KEY, REDIRECT_URL,
                             self.json_path,
                             redirect_wait_time_seconds=0.0,
                             token_write_func=dummy_token_write_func))

        session_constructor.assert_called_with(
                _, token=_, auto_refresh_url=_, auto_refresh_kwargs=_,
                update_token=dummy_token_write_func)


class EasyClientTest(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.json_path = os.path.join(self.tmp_dir.name, 'token.json')
        self.token = {'token': 'yes'}

    def write_token(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.token, f)

    @no_duplicates
    @patch('tda.auth.client_from_token_file')
    def test_no_token_file_no_wd_func(self, client_from_token_file):
        webdriver_func = MagicMock()
        client_from_token_file.side_effect = FileNotFoundError()

        with self.assertRaises(SystemExit):
            auth.easy_client(API_KEY, REDIRECT_URL, self.json_path)

    @no_duplicates
    @patch('tda.auth.client_from_token_file')
    def test_token_file(self, client_from_token_file):
        self.write_token()

        webdriver_func = MagicMock()
        client_from_token_file.return_value = self.token

        self.assertEquals(self.token,
                          auth.easy_client(API_KEY, REDIRECT_URL, self.json_path))

    @no_duplicates
    @patch('tda.auth.client_from_login_flow')
    @patch('tda.auth.client_from_token_file')
    def test_no_token_file_with_wd_func(
            self,
            client_from_token_file,
            client_from_login_flow):
        webdriver_func = MagicMock()
        client_from_token_file.side_effect = SystemExit()
        client_from_login_flow.return_value = 'returned client'
        webdriver_func = MagicMock()

        self.assertEquals('returned client',
                          auth.easy_client(
                              API_KEY, REDIRECT_URL, self.json_path,
                              webdriver_func=webdriver_func))

        webdriver_func.assert_called_once()
        client_from_login_flow.assert_called_once()
