from django.conf.urls import url, include
from django.contrib import admin

from .models import *
from .views import *

urlpatterns = [
    url(r'^dashboard', fitnessView, name='portal-dashboard'),
    
    url(r'^activity/update', dataUpdate, {'page' : 'portal-fitness-view', 'constructs' : [{'model' : Fitness, 'obj' : oFitness}, {'model': Routine, 'obj' : oRoutine}]}, name='portal-fitness-update'),
    url(r'^activity/view/(?P<fm>[0-9]{2})(?P<fd>[0-9]{2})(?P<fy>[0-9]{4})(?P<tm>[0-9]{2})(?P<td>[0-9]{2})(?P<ty>[0-9]{4})', fitnessView, name='portal-fitness-view'),
    url(r'^activity/view', fitnessView, name='portal-fitness-view'),
    url(r'^activity', fitnessView, name='portal-fitness'),
    
    
    url(r'^nutrition/update', dataUpdate, {'page' : 'portal-nutrition-view', 'constructs' : [{'model' : Nutrition, 'obj' : oNutrition}]}, name='portal-nutrition-update'),
    url(r'^nutrition/view/(?P<fm>[0-9]{2})(?P<fd>[0-9]{2})(?P<fy>[0-9]{4})(?P<tm>[0-9]{2})(?P<td>[0-9]{2})(?P<ty>[0-9]{4})', nutritionView, name='portal-nutrition-view'),
    url(r'^nutrition/view', nutritionView, name='portal-nutrition-view'),
    url(r'^nutrition', nutritionView, name='portal-nutrition'),
    
    
    url(r'^sleep/update', dataUpdate, {'page' : 'portal-sleep-view', 'constructs' : [{'model' : Sleep, 'obj' : oSleep}]}, name='portal-sleep-update'),
    url(r'^sleep/view/(?P<fm>[0-9]{2})(?P<fd>[0-9]{2})(?P<fy>[0-9]{4})(?P<tm>[0-9]{2})(?P<td>[0-9]{2})(?P<ty>[0-9]{4})', sleepView, name='portal-sleep-view'),
    url(r'^sleep/view', sleepView, name='portal-sleep-view'),
    url(r'^sleep', sleepView, name='portal-sleep'),
    
    
    url(r'^biometrics', fitnessView, name='portal-biometrics'),
    url(r'^diabetes', fitnessView, name='portal-diabetes'),
    
    url(r'^devices', deviceManagement, name='portal-devices'),
    
    url(r'^$', fitnessView, name='portal-dashboard'),
]