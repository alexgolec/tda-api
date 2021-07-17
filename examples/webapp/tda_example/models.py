import base64
import json
import tda

from django.db import models
from django.contrib.auth.models import User

from . import secrets


class TDALoginData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # OAuth login state, used as an XSRF protection during the TDAmeritrade 
    # login process. Note this field presents a race condition: if the user 
    # attempts to log in to TDAmeritrade multiple times, only the most recent 
    # one will be successful as each initiated login attempt overwrites this 
    # field. 
    #
    # Implementing this properly involves creating an instance of this object
    # and tying it back to the user through a session. Given the unlikelihood of 
    # the user attempting to log in multiple times, this is left as an exercise 
    # for the reader.
    oauth_login_state = models.TextField()

    # The actual token, represented as a JSON dump. Users of this framework 
    # should not access this directly, and should instead rely on the helper 
    # methods below.
    token = models.TextField()

    def token_write_func(self):
        '''
        Utility method to create a token writer that saves the token metadata. 
        Suitable for passing in as a ``token_write_func`` to all methods that 
        take one.
        '''
        def update_token(token):
            self.token = json.dumps(token)
            self.save()
        return update_token


    def token_read_func(self):
        '''
        Utility method to create a token reader that loads the token from this 
        object. Suitable for passing in as a ``token_read_func`` to all methods 
        the take one.
        '''
        def read_token():
            return json.loads(self.token)
        return read_token


    def get_client(self, asyncio=False):
        '''
        Returns a client loaded with this user's TDAmeritrade client.
        '''
        return tda.auth.client_from_access_functions(
                secrets.TDA_API_KEY, self.token_read_func(),
                self.token_write_func(), asyncio)
