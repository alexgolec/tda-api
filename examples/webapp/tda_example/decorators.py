from django.contrib.auth.decorators import user_passes_test

from .models import TDALoginData

def login_and_tda_token_required(func, tda_oauth_url=None):
    def user_has_login_state(user):
        try:
            login_state = user.tdaloginstate
        except TDALoginData.DoesNotExist:
            return False

        return login_state is not None and len(loginstate) > 0

    def f(request):
