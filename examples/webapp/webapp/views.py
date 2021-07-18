from django.views.decorators.http import require_http_methods, require_GET
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render

import tda_example.views as tda_views


@require_GET
def index(request):
    return HttpResponse('tda lol')


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(tda_views.token_oauth_flow)
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})
