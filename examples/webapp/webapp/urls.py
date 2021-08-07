"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

import tda_example.views
import webapp.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('td-example/', include('tda_example.urls')),
    path('accounts', webapp.views.accounts, name='accounts'),
    path('register', webapp.views.register, name='register'),
    path('', webapp.views.index, name='index'),
]