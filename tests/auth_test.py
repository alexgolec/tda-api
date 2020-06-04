from tda import auth
from tests.test_utils import no_duplicates
from unittest.mock import patch, ANY, MagicMock
from unittest.mock import ANY as _

import os
import pickle
import tempfile
import unittest


API_KEY = 'APIKEY'


class ClientFromTokenFileTest(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pickle_path = os.path.join(self.tmp_dir.name, 'token.pickle')
        self.token = {'token': 'yes'}

    def write_token(self):
        with open(self.pickle_path, 'wb') as f:
            pickle.dump(self.token, f)

    @no_duplicates
    def test_no_such_file(self):
        with self.assertRaises(FileNotFoundError):
            auth.client_from_token_file(self.pickle_path, API_KEY)

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Session')
    def test_file_exists(self, session, client):
        self.write_token()

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_token_file(self.pickle_path, API_KEY))
        client.assert_called_once_with(API_KEY, _)
        session.assert_called_once_with(
            API_KEY,
            token=self.token,
            auto_refresh_url=_,
            auto_refresh_kwargs=_,
            token_updater=_)


REDIRECT_URL = 'https://redirect.url.com'


class ClientFromLoginFlow(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pickle_path = os.path.join(self.tmp_dir.name, 'token.pickle')
        self.token = {'token': 'yes'}

    @no_duplicates
    @patch('tda.auth.Client')
    @patch('tda.auth.OAuth2Session')
    def test_no_token_file(self, session_constructor, client):
        AUTH_URL = 'https://auth.url.com'

        session = MagicMock()
        session_constructor.return_value = session
        session.authorization_url.return_value = AUTH_URL, None
        session.fetch_token.return_value = self.token

        webdriver = MagicMock()
        webdriver.get.return_value = REDIRECT_URL + '/token_params'

        client.return_value = 'returned client'

        self.assertEqual('returned client',
                         auth.client_from_login_flow(
                             webdriver, API_KEY, REDIRECT_URL,
                             self.pickle_path,
                             redirect_wait_time_seconds=0.0))

        with open(self.pickle_path, 'rb') as f:
            self.assertEqual(self.token, pickle.load(f))


class EasyClientTest(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pickle_path = os.path.join(self.tmp_dir.name, 'token.pickle')
        self.token = {'token': 'yes'}

    def write_token(self):
        with open(self.pickle_path, 'wb') as f:
            pickle.dump(self.token, f)

    @no_duplicates
    @patch('tda.auth.client_from_token_file')
    def test_no_token_file_no_wd_func(self, client_from_token_file):
        webdriver_func = MagicMock()
        client_from_token_file.side_effect = FileNotFoundError()

        with self.assertRaises(FileNotFoundError):
            auth.easy_client(API_KEY, REDIRECT_URL, self.pickle_path)

    @no_duplicates
    @patch('tda.auth.client_from_token_file')
    def test_token_file(self, client_from_token_file):
        webdriver_func = MagicMock()
        client_from_token_file.return_value = self.token

        self.assertEquals(self.token,
                          auth.easy_client(API_KEY, REDIRECT_URL, self.pickle_path))

    @no_duplicates
    @patch('tda.auth.client_from_login_flow')
    @patch('tda.auth.client_from_token_file')
    def test_no_token_file_with_wd_func(
            self,
            client_from_token_file,
            client_from_login_flow):
        webdriver_func = MagicMock()
        client_from_token_file.side_effect = FileNotFoundError()
        client_from_login_flow.return_value = 'returned client'
        webdriver_func = MagicMock()

        self.assertEquals('returned client',
                          auth.easy_client(
                              API_KEY, REDIRECT_URL, self.pickle_path,
                              webdriver_func=webdriver_func))

        webdriver_func.assert_called_once()
        client_from_login_flow.assert_called_once()
