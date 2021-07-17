from django.urls import path

from . import views

urlpatterns = [
        path('register', views.register, name='register'),
        path('callback', views.callback, name='callback'),
        path('accounts', views.accounts, name='accounts'),
]
