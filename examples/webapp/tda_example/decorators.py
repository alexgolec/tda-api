from django.contrib.auth.decorators import user_passes_test

from .models import TDALoginData

def require_tda_token(f, *args, **kwargs):
    def user_has_login_state(user):
        try:
            login_state = user.tdaloginstate
        except TDALoginData.DoesNotExist:
            return False

        return login_state is not None and len(loginstate) > 0
