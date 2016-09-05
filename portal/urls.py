from django.conf.urls import url, include
from django.contrib import admin

from .views import *

urlpatterns = [
    url(r'^dashboard', fitnessView, name='portal-dashboard'),
    
    url(r'^fitness/update', fitnessUpdate, name='portal-fitness-update'),
    
    #url(r'^fitness/view/from/([0-9]{2})/([0-9]{2})/([0-9]{4})/to/([0-9]{2})/([0-9]{2})/([0-9]{4})', fitnessView, name='portal-fitness-view'),
    
    #url(r'^fitness/view/(?P<from>[0-9]{2}-[0-9]{2}-[0-9]{4})/(?P<to>[0-9]{2}-[0-9]{2}-[0-9]{4})', fitnessView, name='portal-fitness-view'),
    
    url(r'^fitness/view/(?P<fm>[0-9]{2})(?P<fd>[0-9]{2})(?P<fy>[0-9]{4})(?P<tm>[0-9]{2})(?P<td>[0-9]{2})(?P<ty>[0-9]{4})', fitnessView, name='portal-fitness-view'),
    
    #url(r'^fitness/view/([0-9]{2}-[0-9]{2}-[0-9]{4})/([0-9]{2}-[0-9]{2}-[0-9]{4})', fitnessView, name='portal-fitness-view'),
    
    #url(r'^fitness/view/([0-9]{2})/([0-9]{2})/([0-9]{4})/([0-9]{2})/([0-9]{2})/([0-9]{4})', fitnessView, name='portal-fitness-view'),
    
    url(r'^activity/view', fitnessView, name='portal-fitness-view'),
    
    url(r'^activity', fitnessView, name='portal-fitness'),
    
    url(r'^nutrition', fitnessView, name='portal-nutrition'),
    url(r'^sleep', fitnessView, name='portal-sleep'),
    url(r'^biometrics', fitnessView, name='portal-biometrics'),
    url(r'^diabetes', fitnessView, name='portal-diabetes'),
    
    url(r'^devices', deviceManagement, name='portal-devices'),
    
    url(r'^$', fitnessView, name='portal-dashboard'),
]