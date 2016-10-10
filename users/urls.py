from django.conf.urls import url, include
from django.contrib import admin

from .views import *

urlpatterns = [
    
    url(r'^profile/password/change', profilePasswordChange, name='users-profile-password-change'),
    url(r'^profile/password/update', profilePasswordUpdate, name='users-profile-password-update'),
    
    url(r'^profile/general/edit', profileEditGeneral, name='users-profile-general-edit'),
    url(r'^profile/general/update', profileUpdateGeneral, name='users-profile-general-update'),
    
    url(r'^profile', profileEditGeneral, name='users-profile'),
    
    url(r'^login/do', actionLogin, name='users-login-action'),
    url(r'^login', signin, name='users-login'),
    url(r'^logout', signout, name='users-logout'),
    
    url(r'^register/do', actionRegister, name='users-register-action'),
    url(r'^register', register, name='users-register'),
    
    url(r'^$', signin, name='users-login'),
]