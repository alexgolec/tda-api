'''
Token management has become a rather complex affair: many ways of creating one, 
plus legacy vs. new formats, plus refresh token updating, etc. This test suite
exercises the combinatorial explosion of possibilities.
'''

from .utils import no_duplicates
from unittest.mock import patch, MagicMock

import copy
import json
import os
import tda
import tempfile
import unittest


CREATION_TIMESTAMP = 1614258912
MOCK_NOW = CREATION_TIMESTAMP + 60*60*24*91
RECENT_TIMESTAMP = MOCK_NOW - 1

API_KEY = '123456789@AMER.OAUTHAP'
REDIRECT_URL = 'https://redirect.url.com'


class TokenLifecycleTest(unittest.TestCase):

    def asyncio(self):
        return False

    def setUp(self):
        self.maxDiff = None

        self.tmp_dir = tempfile.TemporaryDirectory()
        self.token_path = os.path.join(self.tmp_dir.name, 'token.json')

        self.old_token = {
                'access_token': 'access_token_123',
                'refresh_token': 'refresh_token_123',
                'scope': 'PlaceTrades AccountAccess MoveMoney',
                'expires_in': 1800, 
                'refresh_token_expires_in': 7776000,
                'token_type': 'Bearer',
                'expires_at': CREATION_TIMESTAMP + 1,
        }

        self.updated_token = copy.deepcopy(self.old_token)
        self.updated_token['refresh_token'] = 'refresh_token_123_updated'


    # Token setup methods

    def old_metadata_token(self):
        return {
                'creation_timestamp': CREATION_TIMESTAMP,
                'token': self.old_token,
        }


    def write_legacy_token(self):
        'Token written using the old legacy format, which lacks metadata.'
        with open(self.token_path, 'w') as f:
            json.dump(self.old_token, f)

    def write_old_metadata_token(self):
        'Token created with metadata, but with an old creation timestamp.'
        with open(self.token_path, 'w') as f:
            json.dump(self.old_metadata_token(), f)

    def write_recent_metadata_token(self):
        'Token created with metadata, with a recent creation timestamp.'
        with open(self.token_path, 'w') as f:
            json.dump({
                'creation_timestamp': RECENT_TIMESTAMP,
                'token': self.old_token,
            }, f)

    def write_metadata_token_no_timestamp(self):
        'Token created with metadata, with no creation timestamp.'
        with open(self.token_path, 'w') as f:
            json.dump({
                'creation_timestamp': None,
                'token': self.old_token,
            }, f)


    # On-disk verification methods

    def verify_updated_token(self):
        'Verify that an updated token was written'
        with open(self.token_path, 'r') as f:
            token = json.load(f)
            self.assertEqual(token, {
                'creation_timestamp': MOCK_NOW,
                'token': self.updated_token,
            })

    def verify_not_updated_token(self):
        'Verify that the original token is still in place'
        with open(self.token_path, 'r') as f:
            token = json.load(f)
            self.assertEqual(token, {
                'creation_timestamp': RECENT_TIMESTAMP,
                'token': self.old_token,
            })


    # Client creation methods. Note these rely on mocks being patched in by 
    # calling tests.

    def client_from_token_file(self):
        return tda.auth.client_from_token_file(
                self.token_path, API_KEY, asyncio=self.asyncio())


    def client_from_login_flow(self, mock_OAuth2Client):
        mock_webdriver = MagicMock()
        mock_webdriver.current_url = REDIRECT_URL + '/token_params'

        mock_oauth = MagicMock()
        mock_oauth.create_authorization_url.return_value = (
                'https://redirect-url.com/', None)
        mock_oauth.fetch_token.return_value = self.old_metadata_token()['token']
        mock_OAuth2Client.return_value = mock_oauth

        return tda.auth.client_from_login_flow(
                mock_webdriver, API_KEY, REDIRECT_URL, self.token_path,
                asyncio=self.asyncio())


    def client_from_manual_flow(self, mock_OAuth2Client):
        # Note we don't care about the mock input function because its output is 
        # only passed to fetch_token, and we're not placing any expectations on 
        # that method.
        mock_oauth = MagicMock()
        mock_oauth.create_authorization_url.return_value = (
                'https://redirect-url.com/', None)
        mock_oauth.fetch_token.return_value = self.old_metadata_token()['token']
        mock_OAuth2Client.return_value = mock_oauth

        return tda.auth.client_from_manual_flow(
                API_KEY, REDIRECT_URL, self.token_path, asyncio=self.asyncio())


    # Creation via client_from_token_file

    @no_duplicates
    @patch('tda.auth.OAuth2Client')
    @patch('time.time', MagicMock(return_value=MOCK_NOW))
    def test_client_from_token_file_legacy_token(self, mock_OAuth2Client):
        self.write_legacy_token()
        client = self.client_from_token_file()

        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = self.updated_token
        mock_OAuth2Client.return_value = mock_oauth

        client.ensure_updated_refresh_token()

        self.verify_updated_token()


    @no_duplicates
    @patch('tda.auth.OAuth2Client')
    @patch('time.time', MagicMock(return_value=MOCK_NOW))
    def test_client_from_token_file_old_metadata_token(self, mock_OAuth2Client):
        self.write_old_metadata_token()
        client = self.client_from_token_file()

        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = self.updated_token
        mock_OAuth2Client.return_value = mock_oauth

        client.ensure_updated_refresh_token()

        self.verify_updated_token()


    @no_duplicates
    @patch('tda.auth.OAuth2Client')
    @patch('time.time', MagicMock(return_value=MOCK_NOW))
    def test_client_from_token_file_recent_metadata_token(self, mock_OAuth2Client):
        self.write_recent_metadata_token()
        client = self.client_from_token_file()

        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = self.updated_token
        mock_OAuth2Client.return_value = mock_oauth

        client.ensure_updated_refresh_token()

        self.verify_not_updated_token()

    @no_duplicates
    @patch('tda.auth.OAuth2Client')
    @patch('time.time', MagicMock(return_value=MOCK_NOW))
    def test_client_from_token_file_metadata_token_no_timestamp(
            self, mock_OAuth2Client):
        self.write_metadata_token_no_timestamp()
        client = self.client_from_token_file()

        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = self.updated_token
        mock_OAuth2Client.return_value = mock_oauth

        client.ensure_updated_refresh_token()

        self.verify_updated_token()


    # Creation via client_from_login_flow

    @no_duplicates
    @patch('tda.auth.OAuth2Client')
    @patch('time.time')
    def test_client_from_login_flow_old_token(
            self, mock_time, mock_OAuth2Client):
        self.write_legacy_token()
        mock_time.return_value = CREATION_TIMESTAMP
        client = self.client_from_login_flow(mock_OAuth2Client)

        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = self.updated_token
        mock_OAuth2Client.return_value = mock_oauth

        mock_time.return_value = MOCK_NOW

        client.ensure_updated_refresh_token()

        self.verify_updated_token()


    @no_duplicates
    @patch('tda.auth.OAuth2Client')
    @patch('time.time')
    def test_client_from_login_flow_recent_token(
            self, mock_time, mock_OAuth2Client):
        self.write_legacy_token()
        mock_time.return_value = RECENT_TIMESTAMP
        client = self.client_from_login_flow(mock_OAuth2Client)

        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = self.updated_token
        mock_OAuth2Client.return_value = mock_oauth

        mock_time.return_value = MOCK_NOW

        client.ensure_updated_refresh_token()

        self.verify_not_updated_token()


    # Creation via client_from_manual_flow

    @no_duplicates
    @patch('tda.auth.OAuth2Client')
    @patch('time.time')
    @patch('tda.auth.input', MagicMock())
    def test_client_from_manual_flow_old_token(
            self, mock_time, mock_OAuth2Client):
        self.write_legacy_token()
        mock_time.return_value = CREATION_TIMESTAMP
        client = self.client_from_manual_flow(mock_OAuth2Client)

        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = self.updated_token
        mock_OAuth2Client.return_value = mock_oauth

        mock_time.return_value = MOCK_NOW

        client.ensure_updated_refresh_token()

        self.verify_updated_token()


    @no_duplicates
    @patch('tda.auth.OAuth2Client')
    @patch('time.time')
    @patch('tda.auth.input', MagicMock())
    def test_client_from_manual_flow_recent_token(
            self, mock_time, mock_OAuth2Client):
        self.write_legacy_token()
        mock_time.return_value = RECENT_TIMESTAMP
        client = self.client_from_manual_flow(mock_OAuth2Client)

        mock_oauth = MagicMock()
        mock_oauth.fetch_token.return_value = self.updated_token
        mock_OAuth2Client.return_value = mock_oauth

        mock_time.return_value = MOCK_NOW

        client.ensure_updated_refresh_token()

        self.verify_not_updated_token()


# Same as above, except async
class TokenLifecycleTestAsync(TokenLifecycleTest):
    def asyncio(self):
        return True
