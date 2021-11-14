import unittest.mock
from unittest.mock import ANY as _

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

import tda_example


AUTH_URL = 'https://www.auth-url.com'


class TokenOAuthTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')


    def login(self):
        self.client.login(username='testuser', password='12345')


    @unittest.mock.patch('tda_example.views.tda.auth.get_auth_url_and_state')
    @unittest.mock.patch('tda_example.views.tda.auth.fetch_token_from_redirect')
    def test_tda_login_success_no_dest(
            self, fetch_token_from_redirect, get_auth_url_and_state):
        self.login()

        # 1. The client places a request to token_oauth

        get_auth_url_and_state.return_value = (AUTH_URL, 'oauth-extra-state')
        r = self.client.get(reverse(tda_example.views.token_oauth))

        self.assertEquals(r.status_code, 200)
        # XXX: In a perfect world we would actually test the parameters passed 
        # to the render method.
        self.assertIn(AUTH_URL, r.content.decode('utf8'))

        self.assertEqual(1, tda_example.models.TDAOauthState.objects.count())
        oauth_state = tda_example.models.TDAOauthState.objects.get(id=1)

        # 2. TDA successfully logs in the client and sends a request to the 
        #    callback URL, passing along the state.

        r = self.client.get(reverse(tda_example.views.callback))
        self.assertRedirects(r, '/')
        fetch_token_from_redirect.assert_called_with(_, _, _, 
                oauth_state.oauth_secret, token_write_func=_)

        # XXX: Asserts that a TDALoginData object was created, but because we're 
        #      using mocks for tda-api, nothing testable has been written to it.
        self.assertEqual(1, tda_example.models.TDALoginData.objects.count())


    @unittest.mock.patch('tda_example.views.tda.auth.get_auth_url_and_state')
    @unittest.mock.patch('tda_example.views.tda.auth.fetch_token_from_redirect')
    def test_tda_login_success_with_dest(
            self, fetch_token_from_redirect, get_auth_url_and_state):
        REDIRECT_URL = 'https://www.after-callback.com'

        self.login()

        # 1. The client places a request to token_oauth

        # tda-api encodes additional state after the OAuth login state, 
        # separated by a colon.
        get_auth_url_and_state.side_effect = (
                lambda oauth, additional_state:
                    (AUTH_URL, 'oauth-login-state:' + additional_state))
        r = self.client.get(
                reverse(tda_example.views.token_oauth), {'dest': REDIRECT_URL})

        self.assertEquals(r.status_code, 200)
        # XXX: In a perfect world we would actually test the parameters passed 
        # to the render method.
        self.assertIn(AUTH_URL, r.content.decode('utf8'))

        self.assertEqual(1, tda_example.models.TDAOauthState.objects.count())
        oauth_state = tda_example.models.TDAOauthState.objects.get(id=1)

        # 2. TDA successfully logs in the client and sends a request to the 
        #    callback URL, passing along the state.

        r = self.client.get(reverse(tda_example.views.callback))
        self.assertRedirects(r, REDIRECT_URL, fetch_redirect_response=False)
        fetch_token_from_redirect.assert_called_with(_, _, _, 
                oauth_state.oauth_secret, token_write_func=_)

        # XXX: Asserts that a TDALoginData object was created, but because we're 
        #      using mocks for tda-api, nothing testable has been written to it.
        self.assertEqual(1, tda_example.models.TDALoginData.objects.count())


    @unittest.mock.patch('tda_example.views.tda.auth.get_auth_url_and_state')
    @unittest.mock.patch('tda_example.views.tda.auth.fetch_token_from_redirect')
    def test_tda_login_logged_out_after_oauth_redirect(
            self, fetch_token_from_redirect, get_auth_url_and_state):
        self.login()

        # 1. The client places a request to token_oauth

        get_auth_url_and_state.return_value = (AUTH_URL, 'oauth-extra-state')
        r = self.client.get(reverse(tda_example.views.token_oauth))

        self.assertEquals(r.status_code, 200)

        # 2. TDA successfully logs in the client and sends a request to the 
        #    callback URL, passing along the state.

        self.client.logout()

        r = self.client.get(reverse(tda_example.views.callback))
        self.assertEquals(r.status_code, 403)


    def test_not_logged_in(self):
        r = self.client.get(reverse('token_oauth'), data={'sure': 'whatever'})
        self.assertEquals(r.status_code, 403)
