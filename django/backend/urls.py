"""
Script file: urls.py
Created on: Feb 25, 2021
Last modified on: Mar 28, 2021

Comments:
    Backend URL Configuration
    The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/

Examples:
    [Function views]
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  path('', views.home, name='home')
    [Class-based views]
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    [Including another URLconf]
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import apis.views as main
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required

from apis import auth

urlpatterns = [
    path('', main.index, name='index'),
    path('apis/', include('apis.urls')),
    path('admin/', admin.site.urls),
    path('apis/login', auth.user_login),
    path('apis/logout', auth.user_logout),
    path('apis/regist', auth.user_regist),
    # path('api-auth/', include('rest_framework.urls'))
]


# urlpatterns = [
#     path('', login_required(main.index), name='index'),
#     path('apis/', login_required(include('apis.urls'))),
#     path('admin/', login_required( admin.site.urls)),
#     path('apis/login', auth.user_login),
#     path('apis/logout', auth.user_logout),
#     path('apis/regist', auth.user_regist)
# ]