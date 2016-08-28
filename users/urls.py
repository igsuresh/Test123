from django.conf.urls import url, include
from django.contrib import admin

from .views import *

urlpatterns = [
    url(r'^profile/update/general', profileUpdateGeneral, name='users-profile-update-general'),
    url(r'^profile/update/password', profileUpdatePassword, name='users-profile-update-password'),
    url(r'^profile/edit', profileEdit, name='users-profile-edit'),
    url(r'^profile/view', profileView, name='users-profile-view'),
    url(r'^profile/view', profileView, name='users-profile'),
    
    url(r'^login/do', actionLogin, name='users-login-action'),
    url(r'^login', signin, name='users-login'),
    url(r'^logout', signout, name='users-logout'),
    
    url(r'^register/do', actionRegister, name='users-register-action'),
    
    url(r'^register', register, name='users-register'),
    
    url(r'^$', signin, name='users-login'),
]