from django.conf import settings as SETTINGS
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

import datetime

from pheel.utils import *

from broker.models import *
from broker.api import *

from users.models import *

@login_required
def dashboard(request):
    template = 'portal/dashboard.html'
    
    profile = Profile.objects.get(user=request.user)
    
    params = {
                'profile' : profile,
                'menuHighlight' : "dashboard",
                'deviceConnectionURL' : "https://app.validic.com/%s/%s" % (SETTINGS.VALIDIC_ID,profile.validic_access_token)
            }
    
    return cRender(template,params,request)

@login_required
def fitnessView(request):
    template = 'portal/fitness.html'
    
    recordsFitness = Fitness.objects.filter(profile__user=request.user)
    recordsRoutine = Routine.objects.filter(profile__user=request.user)
    
    profile = Profile.objects.get(user=request.user)
    
    params = {
                'recordsFitness' : recordsFitness,
                'recordsRoutine' : recordsRoutine,
                'profile' : profile,
                'menuHighlight' : "fitness",
                'deviceConnectionURL' : "https://app.validic.com/%s/%s" % (SETTINGS.VALIDIC_ID,profile.validic_access_token)
            }
    
    return cRender(template,params,request)

@login_required
def fitnessUpdate(request):
    page = 'portal-fitness-view'
    
    updates = []
    tzOffset = "-04:00"
    
    previousFitness = "2016-01-01T00:00:00" + tzOffset
    previousRoutine = "2016-01-01T00:00:00" + tzOffset
    
    if Fitness.objects.filter(user=request.user).exists():
        previousFitness = Fitness.objects.filter(user=request.user,timestamp__isnull=False).latest('timestamp').timestamp.strftime("%Y-%m-%dT%H:%M:%S") + tzOffset
    
    if Routine.objects.filter(user=request.user).exists():
        previousRoutine = Routine.objects.filter(user=request.user,timestamp__isnull=False).latest('timestamp').timestamp.strftime("%Y-%m-%dT%H:%M:%S") + tzOffset
    
    
    updates.append(oFitness(user=request.user,startDate=previousFitness,endDate=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + tzOffset))
    
    updates.append(oRoutine(user=request.user,startDate=previousRoutine,endDate=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + tzOffset))
    
    for allUpdates in updates:
    
        allUpdates.getData()
    
        allUpdates.store()
    
        while allUpdates.getNext():
            allUpdates.store()
    
    return cRedirect(page,{})

@login_required
def deviceManagement(request):
    profile = Profile.objects.get(user=request.user)
    
    return redirect("https://app.validic.com/%s/%s" % (SETTINGS.VALIDIC_ID,profile.validic_id))