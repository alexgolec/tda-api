from authlib.integrations.httpx_client import OAuth2Client
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_GET

import base64
import json
import tda

from . import secrets
from .models import TDALoginData, TDAOauthState


@require_GET
def token_oauth(request):
    '''
    Initialize the login state and send the user to the TDA login notification 
    page.
    '''

    if not request.user.is_authenticated:
        raise Http404('Login required')

    oauth = OAuth2Client(
            tda.auth.normalize_api_key(secrets.TDA_API_KEY),
            redirect_uri=secrets.TDA_CALLBACK_URL)

    if 'dest' in request.GET:
        state_data = json.dumps({'next_url': request.GET['dest']})
        b64 = base64.urlsafe_b64encode(state_data.encode('utf-8'))
        additional_state = b64.decode('utf-8')
    else:
        additional_state = None

    auth_url, state = tda.auth.get_auth_url_and_state(oauth, additional_state)
    tda_oauth_state, _ = TDAOauthState.objects.get_or_create(user=request.user)
    tda_oauth_state.oauth_secret = state
    tda_oauth_state.save()

    request.session['oauth_state'] = tda_oauth_state.id

    return render(request, 'tda_login.html', {'auth_url': auth_url})


@require_http_methods(['GET'])
def callback(request):
    '''
    Handle the callback by fetching a token and initializing the TDA backend 
    login state.
    '''

    if not request.user.is_authenticated:
        raise Http404('Login required')

    # Fetch a token and register it to the DB.
    oauth = OAuth2Client(
            tda.auth.normalize_api_key(secrets.TDA_API_KEY),
            redirect_uri=secrets.TDA_CALLBACK_URL)

    redirected_url = request.build_absolute_uri()
    oauth_state = TDAOauthState.objects.get(id=request.session['oauth_state'])
    login_data, _ = TDALoginData.objects.get_or_create(user=request.user)

    state = oauth_state.oauth_secret

    client = tda.auth.fetch_token_from_redirect(
            oauth, redirected_url, secrets.TDA_API_KEY,
            state, token_write_func=login_data.token_write_func())

    # Extract the next URL from the state.
    state_split = state.split(':')
    if len(state_split) == 2:
        additional_state = json.loads(base64.urlsafe_b64decode(state_split[1]))
        return redirect(additional_state['next_url'])

    return HttpResponse('callback')
