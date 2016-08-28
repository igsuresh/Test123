from django.conf.urls import url, include
from django.contrib import admin

from .views import *

urlpatterns = [
    url(r'^dashboard', dashboard, name='portal-dashboard'),
    
    url(r'^fitness/update', fitnessUpdate, name='portal-fitness-update'),
    url(r'^fitness/view', fitnessView, name='portal-fitness-view'),
    url(r'^fitness', fitnessView, name='portal-fitness'),
    
    
    url(r'^nutrition', dashboard, name='portal-nutrition'),
    url(r'^sleep', dashboard, name='portal-sleep'),
    url(r'^biometrics', dashboard, name='portal-biometrics'),
    url(r'^diabetes', dashboard, name='portal-diabetes'),
    
    url(r'^devices', deviceManagement, name='portal-devices'),
    
    url(r'^$', dashboard, name='portal-dashboard'),
]