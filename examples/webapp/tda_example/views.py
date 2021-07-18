from authlib.integrations.httpx_client import OAuth2Client
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_GET

import tda
import json

from . import secrets
from .models import TDALoginData


def token_oauth_flow(request):
    if not request.user.is_authenticated:
        raise Http404('Login required')

    oauth = OAuth2Client(
            tda.auth.normalize_api_key(secrets.TDA_API_KEY),
            redirect_uri=secrets.TDA_CALLBACK_URL)
    auth_url, state = tda.auth.get_auth_url_and_state(oauth)

    tda_login_data, _ = TDALoginData.objects.get_or_create(user=request.user)
    tda_login_data.oauth_login_state = state
    tda_login_data.save()

    return render(request, 'tda_login.html', {'auth_url': auth_url})


@require_http_methods(['GET'])
def callback(request):
    if not request.user.is_authenticated:
        raise Http404('Login required')

    oauth = OAuth2Client(
            tda.auth.normalize_api_key(secrets.TDA_API_KEY),
            redirect_uri=secrets.TDA_CALLBACK_URL)

    redirected_url = request.build_absolute_uri()
    tda_login_data = request.user.tdalogindata

    state = tda_login_data.oauth_login_state

    client = tda.auth.fetch_token_from_redirect(
            oauth, redirected_url, secrets.TDA_API_KEY,
            tda_login_data.oauth_login_state,
            token_write_func=tda_login_data.token_write_func())

    return HttpResponse('callback')


@require_GET
def accounts(request):
    if not request.user.is_authenticated:
        raise Http404('Login required')

    client = request.user.tdalogindata.get_client()

    accounts = json.dumps(client.get_accounts().json(), indent=4)

    return HttpResponse(accounts)
