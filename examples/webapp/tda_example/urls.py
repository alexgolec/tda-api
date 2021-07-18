from django.urls import path

from . import views

urlpatterns = [
        path('token-oauth', views.token_oauth, name='token-oauth'),
        path('callback', views.callback, name='callback'),
        path('accounts', views.accounts, name='accounts'),
]
