from django.conf import settings as SETTINGS
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

import datetime, math

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
#def fitnessView(request):
    template = 'portal/fitness.html'
    
    # DATE RANGE PROCESSING
    
    end = datetime.date.today()
    start = end - timedelta(days=14)
    
    constraints = {'fm' : None,'fd' : None,'fy' : None,'tm' : None,'td' : None,'ty' : None}
    custom = True
    
    for each in constraints.keys():
        if each not in request.GET.keys():
            custom = False
            break
        else:
            constraints[each] = int(request.GET[each])
    
    if custom:
        start = datetime.date(constraints['fy'],constraints['fm'],constraints['fd'])
        end = datetime.date(constraints['ty'],constraints['tm'],constraints['td'])
    
    startTime = datetime.datetime.combine(start,datetime.time())
    endTime = datetime.datetime.combine((end + datetime.timedelta(1)), datetime.time())
    
    # STAT BOX INFO
    
    dailyDistance = Routine.objects.filter(timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('distance'))['distance__sum']
    dailySteps = Routine.objects.filter(timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('steps'))['steps__sum']
    dailyDuration = Fitness.objects.filter(timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('duration'))['duration__sum']
    
    dailyFloors = Routine.objects.filter(timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('floors'))['floors__sum']
    dailyElevation = Routine.objects.filter(timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('elevation'))['elevation__sum']
    
    dailyCalories = Routine.objects.filter(timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('calories'))['calories__sum']
    
    dailyStats = {
                'distance' : int(math.ceil(dailyDistance)) if dailyDistance else 0,
                'distanceMiles' : int(math.ceil(float(dailyDistance)/(1.6 * 1000))) if dailyDistance else 0,
                'steps' : int(math.ceil(dailySteps)) if dailySteps else 0,
                
                'duration' : int(math.ceil(dailyDuration)) if dailyDuration else 0,
                
                'floors' : int(math.ceil(dailyFloors)) if dailyFloors else 0,
                'elevation' : int(math.ceil(dailyElevation)) if dailyElevation else 0,
                
                'calories' : int(math.ceil(dailyCalories)) if dailyCalories else 0
    }
    
    # DISTANCE & ELEVATION
    
    routine = Routine.objects.filter(profile__user=request.user,timestamp__gte=startTime,timestamp__lte=endTime)
    fitness = Fitness.objects.filter(profile__user=request.user,timestamp__gte=startTime,timestamp__lte=endTime)
    
    stepsByApp = {}
    stepsByAppSources = []
    
    distanceByActivity = {}
    activitySources = ['Walking']
    
    elevation = {}
    
    cumActivity = {'duration' : {}, 'calories' : {}}
    activityByIntensity = {'duration' : {}, 'calories' : {}}
    activityByCategory = {'duration' : {}, 'calories' : {}}
    
    for activity in routine:
        # Steps by App
        if activity.source.source_name not in stepsByAppSources:
            stepsByAppSources.append(activity.source.source_name)
        
        if (activity.timestamp.date() not in stepsByApp.keys()) and (activity.steps > 0):
            stepsByApp[activity.timestamp.date()] = {activity.source.source_name : activity.steps}
        
        elif activity.steps > 0:
            if activity.source.source_name in stepsByApp[activity.timestamp.date()].keys():
                stepsByApp[activity.timestamp.date()][activity.source.source_name] += activity.steps
            
            else:
                stepsByApp[activity.timestamp.date()][activity.source.source_name] = activity.steps
        
        # Distance by activity
        
        if (activity.timestamp.date() not in distanceByActivity.keys()) and (activity.distance > 0):
            distanceByActivity[activity.timestamp.date()] = {'Walking' : activity.distance}
        
        elif activity.distance > 0:
            if 'Walking' in distanceByActivity[activity.timestamp.date()].keys():
                distanceByActivity[activity.timestamp.date()]['Walking'] += activity.distance
            else:
                distanceByActivity[activity.timestamp.date()]['Walking'] = activity.distance
        
        # Elevation
        
        if (activity.timestamp.date() not in elevation.keys()) and (activity.elevation > 0):
            elevation[activity.timestamp.date()] = activity.elevation
        
        # Cummulative for walking (calories only; distance unavailable)
        if ('Low' not in activityByIntensity['calories'].keys()) and (activity.calories > 0):
            activityByIntensity['calories']['Low'] = activity.calories
        
        elif activity.calories > 0:
            activityByIntensity['calories']['Low'] += activity.calories
        
        if ('Walking' not in activityByCategory['calories'].keys()) and (activity.calories > 0):
            activityByCategory['calories']['Walking'] = activity.calories
        
        elif activity.calories > 0:
            activityByCategory['calories']['Walking'] += activity.calories
        
        if (activity.timestamp.date() not in cumActivity['calories'].keys()) and (activity.calories > 0):
            cumActivity['calories'][activity.timestamp.date()] = {'Walking' : activity.calories}
        
        elif activity.calories > 0:
            if 'Walking' not in cumActivity['calories'][activity.timestamp.date()].keys():
                cumActivity['calories'][activity.timestamp.date()]['Walking'] = activity.calories
            
            else:
                cumActivity['calories'][activity.timestamp.date()]['Walking'] += activity.calories
    
    # CUMMULATIVE ACTIVITY
    
    for activity in fitness:
        
        # Intensity
        
        if (activity.timestamp.date() not in cumActivity['duration'].keys()) and (activity.duration > 0):
            cumActivity['duration'][activity.timestamp.date()] = {activity.intensity.name : activity.duration}
        
        elif activity.duration > 0:
            if activity.intensity.name not in cumActivity['duration'][activity.timestamp.date()].keys():
                cumActivity['duration'][activity.timestamp.date()][activity.intensity.name] = activity.duration
            
            else:
                cumActivity['duration'][activity.timestamp.date()][activity.intensity.name] += activity.duration
        
        # Calories
        
        if (activity.timestamp.date() not in cumActivity['calories'].keys()) and (activity.calories > 0):
            cumActivity['calories'][activity.timestamp.date()] = {activity.activity_category.name : activity.calories}
        
        elif activity.calories > 0:
            if activity.activity_category.name not in cumActivity['calories'][activity.timestamp.date()].keys():
                cumActivity['calories'][activity.timestamp.date()][activity.activity_category.name] = activity.calories
            
            else:
                cumActivity['calories'][activity.timestamp.date()][activity.activity_category.name] += activity.calories
        
    
    # ACTIVITY BY INTENSITY
    
    for intensity in Intensity.objects.all():
        total = fitness.filter(intensity=intensity).aggregate(Sum('duration'))['duration__sum']
        
        if total:
            if intensity.name not in activityByIntensity['duration'].keys():
                activityByIntensity['duration'][intensity.name] = total
            
            else:
                activityByIntensity['duration'][intensity.name] += total
        
        total = fitness.filter(intensity=intensity).aggregate(Sum('calories'))['calories__sum']
        
        if total:
            if intensity.name not in activityByIntensity['calories'].keys():
                activityByIntensity['calories'][intensity.name] = total
            
            else:
                activityByIntensity['calories'][intensity.name] += total
    
    # ACTIVITY BY CATEGORY
    
    for category in ActivityCategory.objects.all():
        total = fitness.filter(activity_category=category).aggregate(Sum('duration'))['duration__sum']
        
        if total:
            if category.name not in activityByCategory['duration'].keys():
                activityByCategory['duration'][category.name] = total
            
            else:
                activityByCategory['duration'][category.name] += total
        
        total = fitness.filter(activity_category=category).aggregate(Sum('calories'))['calories__sum']
        
        if total:
            if category.name not in activityByCategory['calories'].keys():
                activityByCategory['calories'][category.name] = total
            
            else:
                activityByCategory['calories'][category.name] += total
    
    # REQUIRED VARS & RETURN
    
    profile = Profile.objects.get(user=request.user)
    
    params = {
                'profile' : profile,
                'menuHighlight' : "fitness",
                'deviceConnectionURL' : "https://app.validic.com/%s/%s" % (SETTINGS.VALIDIC_ID,profile.validic_access_token),
                
                'periodStart' : start,
                'periodEnd' : end,
                'dailyStats' : dailyStats,
                
                'stepsByApp' : stepsByApp,
                'stepsByAppSources' : stepsByAppSources,
                
                'distanceByActivity' : distanceByActivity,
                'activitySources' : activitySources,
                'elevation' : elevation,
                
                'activityByIntensity' : activityByIntensity,
                'activityByCategory' : activityByCategory,
                'cumActivity' : cumActivity,
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