from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

@require_http_methods(['GET'])
def index(request):
    return HttpResponse('tda lol')


@require_http_methods(['GET', 'POST'])
def register(request):
    return HttpResponse()


@require_http_methods(['GET'])
def callback(request):
    return HttpResponse('callback')
