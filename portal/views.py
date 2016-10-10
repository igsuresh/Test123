from django.conf import settings as SETTINGS
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

import datetime, math

from pheel.utils import *

from broker.models import *
from broker.api import *

from users.models import *

DEVICE_CONNECTION_URL_PREFIX = "https://app.validic.com/%s/%s"

@login_required
def dataUpdate(request, page, constructs):
    updates = []
    tzOffset = "-04:00"
    
    previous = "2016-01-01T00:00:00" + tzOffset
    
    for construct in constructs:
    
        if construct['model'].objects.filter(user=request.user).exists():
            previous = construct['model'].objects.filter(user=request.user,timestamp__isnull=False).latest('timestamp').timestamp.strftime("%Y-%m-%dT%H:%M:%S") + tzOffset
            
        updates.append(construct['obj'](user=request.user,startDate=previous,endDate=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + tzOffset))
    
        for update in updates:
            update.getData()
            
            update.store()
            
            while update.getNext():
                update.store()
    
    return redirect(page)

@login_required
def fitnessView(request):
    template = 'portal/activity/fitness.html'
    
    # DATE RANGE PROCESSING
    
    end = datetime.date.today()
    start = end - timedelta(days=14)
    
    constraints = {'fm' : None,'fd' : None,'fy' : None,'tm' : None,'td' : None,'ty' : None}
    custom = True
    
    for each in constraints.keys():
        if each not in request.GET.keys():
            custom = False
            break
        elif request.GET[each] and request.GET[each].isdigit():
            constraints[each] = int(request.GET[each])
        else:
            custom = False
            break
    
    if custom:
        start = datetime.date(constraints['fy'],constraints['fm'],constraints['fd'])
        end = datetime.date(constraints['ty'],constraints['tm'],constraints['td'])
    
    startTime = datetime.datetime.combine(start,datetime.time())
    endTime = datetime.datetime.combine((end + datetime.timedelta(1)), datetime.time())
    
    # STAT BOX INFO
    
    dailyDistance = Routine.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('distance'))['distance__sum']
    dailySteps = Routine.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('steps'))['steps__sum']
    dailyDuration = Fitness.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('duration'))['duration__sum']
    
    dailyFloors = Routine.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('floors'))['floors__sum']
    dailyElevation = Routine.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('elevation'))['elevation__sum']
    
    dailyCalories = Routine.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('calories'))['calories__sum']
    
    dailyStats = {
                'distance' : int(math.ceil(dailyDistance)) if dailyDistance else 0,
                'distanceMiles' : round(float(dailyDistance)/(1600),2) if dailyDistance else 0,
                'steps' : int(math.ceil(dailySteps)) if dailySteps else 0,
                
                'duration' : round(dailyDuration/3600,2) if dailyDuration else 0,
                
                'floors' : roun(dailyFloors,1) if dailyFloors else 0,
                'elevation' : int(math.ceil(dailyElevation)) if dailyElevation else 0,
                
                'calories' : int(math.ceil(dailyCalories)) if dailyCalories else 0
    }
    
    # DISTANCE & ELEVATION
    
    routine = Routine.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime)
    fitness = Fitness.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime)
    
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
            stepsByApp[activity.timestamp.date()] = {activity.source.source_name : int(math.ceil(activity.steps))}
        
        elif activity.steps > 0:
            if activity.source.source_name in stepsByApp[activity.timestamp.date()].keys():
                stepsByApp[activity.timestamp.date()][activity.source.source_name] += int(math.ceil(activity.steps))
            
            else:
                stepsByApp[activity.timestamp.date()][activity.source.source_name] = int(math.ceil(activity.steps))
        
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
                'deviceConnectionURL' : DEVICE_CONNECTION_URL_PREFIX % (SETTINGS.VALIDIC_ID,profile.validic_access_token),
                
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
    
    return render(request,template,params)

### NUTRITION ###

@login_required
def nutritionView(request):
    template = 'portal/nutrition/nutrition.html'
    
    # DATE RANGE PROCESSING
    
    end = datetime.date.today()
    start = end - timedelta(days=14)
    
    constraints = {'fm' : None,'fd' : None,'fy' : None,'tm' : None,'td' : None,'ty' : None}
    custom = True
    
    for each in constraints.keys():
        if each not in request.GET.keys():
            custom = False
            break
        elif request.GET[each] and request.GET[each].isdigit():
            constraints[each] = int(request.GET[each])
        else:
            custom = False
            break
    
    if custom:
        start = datetime.date(constraints['fy'],constraints['fm'],constraints['fd'])
        end = datetime.date(constraints['ty'],constraints['tm'],constraints['td'])
    
    startTime = datetime.datetime.combine(start,datetime.time())
    endTime = datetime.datetime.combine((end + datetime.timedelta(1)), datetime.time())
    
    # STAT BOX INFO
    
    dailyCalories = Nutrition.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('calories'))['calories__sum']
    dailyCarbs = Nutrition.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('carbohydrates'))['carbohydrates__sum']
    dailyFat = Nutrition.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('fat'))['fat__sum']
    dailyProtein = Nutrition.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('protein'))['protein__sum']
    dailyFiber = Nutrition.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('fiber'))['fiber__sum']
    dailyWater = Nutrition.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime).aggregate(Sum('water'))['water__sum']
    
    dailyStats = {
                'calories' : int(math.ceil(dailyCalories)) if dailyCalories else 0,
                'carbs' : int(math.ceil(dailyCarbs)) if dailyCarbs else 0,
                'fat' : dailyFat if dailyFat else 0,
                'protein' : dailyProtein if dailyProtein else 0,
                'fiber' : dailyFiber if dailyFiber else 0,
                'water' : int(math.ceil(dailyWater)) if dailyWater else 0
    }
    
    # KEY STATS AREA
    
    nutrition = Nutrition.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime)
    
    keyStats = {}
    keyStatsY = ['Carbs', 'Fat', 'Fiber', 'Protein']
    
    lineCharts = {'Calories' : {}, 'Water' : {}, 'Sodium' : {}}
    
    for record in nutrition:
        if (record.timestamp.date() not in keyStats.keys()) and (record.carbohydrates or record.fat or record.fiber or record.protein):
            keyStats[record.timestamp.date()] = {}
        
        if record.carbohydrates and ('Carbs' in keyStats[record.timestamp.date()].keys()):
            keyStats[record.timestamp.date()]['Carbs'] += record.carbohydrates
        
        elif record.carbohydrates:
            keyStats[record.timestamp.date()]['Carbs'] = record.carbohydrates
        
        if record.fat and ('Fat' in keyStats[record.timestamp.date()].keys()):
            keyStats[record.timestamp.date()]['Fat'] += record.fat
        
        elif record.carbohydrates:
            keyStats[record.timestamp.date()]['Fat'] = record.fat
        
        if record.fiber and ('Fiber' in keyStats[record.timestamp.date()].keys()):
            keyStats[record.timestamp.date()]['Fiber'] += record.fiber
        
        elif record.fiber:
            keyStats[record.timestamp.date()]['Fiber'] = record.fiber
        
        if record.protein and ('Protein' in keyStats[record.timestamp.date()].keys()):
            keyStats[record.timestamp.date()]['Protein'] += record.protein
        
        elif record.protein:
            keyStats[record.timestamp.date()]['Protein'] = record.protein
        
        if record.calories and record.timestamp.date() in lineCharts['Calories'].keys():
            lineCharts['Calories'][record.timestamp.date()] += record.calories
        
        elif record.calories:
            lineCharts['Calories'][record.timestamp.date()] = record.calories
        
        if record.water and record.timestamp.date() in lineCharts['Water'].keys():
            lineCharts['Water'][record.timestamp.date()] += record.water
        
        elif record.water:
            lineCharts['Water'][record.timestamp.date()] = record.water
        
        if record.sodium and record.timestamp.date() in lineCharts['Sodium'].keys():
            lineCharts['Sodium'][record.timestamp.date()] += record.sodium
        
        elif record.calories:
            lineCharts['Sodium'][record.timestamp.date()] = record.sodium
    
    # REQUIRED VARS & RETURN
    
    profile = Profile.objects.get(user=request.user)
    
    params = {
        'profile' : profile,
        'menuHighlight' : "nutrition",
        'deviceConnectionURL' : DEVICE_CONNECTION_URL_PREFIX % (SETTINGS.VALIDIC_ID,profile.validic_access_token),
        
        'periodStart' : start,
        'periodEnd' : end,
        'dailyStats' : dailyStats,
        
        'keyStats' : keyStats,
        'keyStatsY' : keyStatsY,
        
        'lineCharts' : lineCharts,
    }
    
    return render(request,template,params)

### SLEEP ###

@login_required
def sleepView(request):
    template = 'portal/sleep/sleep.html'
    
    # DATE RANGE PROCESSING
    
    end = datetime.date.today()
    start = end - timedelta(days=14)
    
    constraints = {'fm' : None,'fd' : None,'fy' : None,'tm' : None,'td' : None,'ty' : None}
    custom = True
    
    for each in constraints.keys():
        if each not in request.GET.keys():
            custom = False
            break
        elif request.GET[each] and request.GET[each].isdigit():
            constraints[each] = int(request.GET[each])
        else:
            custom = False
            break
    
    if custom:
        start = datetime.date(constraints['fy'],constraints['fm'],constraints['fd'])
        end = datetime.date(constraints['ty'],constraints['tm'],constraints['td'])
    
    startTime = datetime.datetime.combine(start,datetime.time())
    endTime = datetime.datetime.combine((end + datetime.timedelta(1)), datetime.time())
    
    sleep = Sleep.objects.filter(user=request.user,timestamp__gte=startTime,timestamp__lte=endTime)
    
    keyStats = {}
    keyStatsY = ['Light', 'Deep', 'Rem']
    
    for record in sleep:
        if (record.timestamp.date() not in keyStats.keys()) and (record.light or record.deep or record.rem):
            keyStats[record.timestamp.date()] = {}
        
        if record.light and ('Light' in keyStats[record.timestamp.date()].keys()):
            keyStats[record.timestamp.date()]['Light'] += record.light
        
        elif record.light:
            keyStats[record.timestamp.date()]['Light'] = record.light
        
        if record.deep and ('Deep' in keyStats[record.timestamp.date()].keys()):
            keyStats[record.timestamp.date()]['Deep'] += record.deep
        
        elif record.deep:
            keyStats[record.timestamp.date()]['Deep'] = record.deep
        
        if record.rem and ('Rem' in keyStats[record.timestamp.date()].keys()):
            keyStats[record.timestamp.date()]['Rem'] += record.rem
        
        elif record.rem:
            keyStats[record.timestamp.date()]['Rem'] = record.rem
    
    # REQUIRED VARS & RETURN
    
    profile = Profile.objects.get(user=request.user)
    
    params = {
        'profile' : profile,
        'menuHighlight' : "sleep",
        'deviceConnectionURL' : DEVICE_CONNECTION_URL_PREFIX % (SETTINGS.VALIDIC_ID,profile.validic_access_token),
        
        'periodStart' : start,
        'periodEnd' : end,
        
        'keyStats' : keyStats,
        'keyStatsY' : keyStatsY,
    }
    
    return render(request,template,params)

@login_required
def deviceManagement(request):
    profile = Profile.objects.get(user=request.user)
    
    return redirect(DEVICE_CONNECTION_URL_PREFIX % (SETTINGS.VALIDIC_ID,profile.validic_id))

