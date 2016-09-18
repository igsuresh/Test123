from django.conf import settings as SETTINGS
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import RequestContext

from decimal import Decimal
from datetime import datetime

from pheel.utils import *
from broker.models import *
from users.models import *

import datetime, json, requests

class oDataObject():
    access_token = SETTINGS.VALIDIC_KEY
    organization_id = SETTINGS.VALIDIC_ID
    urlRoot = "https://api.validic.com/v1/organizations"
    latest = False
    model = None
    dataType = ""
    
    def __init__(self,user=None,latest=False,startDate=None,endDate=None,expanded=False,source=None,limit=None):
        self.user_id = None
        
        if user:
            self.user_id = Profile.objects.get(user=user).validic_id
        
        self.latest = latest
        self.start_date = startDate
        self.end_date = endDate
        self.expanded = 1 if expanded else 0
        self.source = None
        self.limit = None
        self.response = None
    
    def getData(self):
        url = '/'.join([self.urlRoot,self.organization_id,"%s.json"]) % self.dataType
        
        if self.user_id and self.latest:
            url = '/'.join([self.urlRoot,organization_id,"users",self.user_id,dataType,"latest.json"])
        
        elif self.user_id and not self.latest:
            url = '/'.join([self.urlRoot,self.organization_id,"users",self.user_id,"%s.json"]) % self.dataType
        
        elif self.latest and not self.user_id:
            url = '/'.join([self.urlRoot,self.organization_id,self.dataType,"latest.json"])
        
        headers = {'Content-Type': 'application/json'}
        
        payload = {'access_token' : self.access_token}
        
        for k,v in {
                        'start_date' : self.start_date,
                        'end_date' : self.end_date,
                        'expanded' : self.expanded,
                        'source' : self.source,
                        'limit' : self.limit
                    }.items():
            
            if v:
                payload[k] = v
        
        self.response = requests.get(url, params=payload,headers=headers)
    
    def getPrevious(self):
        r = None
        
        if self.response and ('status' in self.response.json()['summary'].keys()) and (self.response.json()['summary']['previous']):
            
            if (int(self.response.json()['summary']['status']) == 200) and self.response.json()['summary']['previous'].startswith("https//.api.validic.com/"):
                r = requests.get(self.response.json()['summary']['previous'])
        
        self.response = r
        
    def getNext(self):
        r = None
        
        if self.response and ('status' in self.response.json()['summary'].keys()) and (self.response.json()['summary']['next']):
            
            if (int(self.response.json()['summary']['status']) == 200) and self.response.json()['summary']['next'].startswith("https//.api.validic.com/"):
                r = requests.get(self.response.json()['summary']['next'])
                
                if r['summary']['page'] == 1:
                    r = None
        
        self.response = r
    
    def returnStatus(self):
        status = None
        
        if self.response and ('status' in self.response.json()['summary'].keys()):
            status = self.response.json()['summary']['status']
        
        return status
    
    def returnCount(self):
        count = 0
        
        if self.response and ('results' in self.response.json()['summary'].keys()):
            count = self.response.json()['summary']['results']
        
        return count
    
    def returnOffset(self):
        offset = 0
        
        if self.response and ('offset' in self.response.json()['summary'].keys()):
            status = self.response.json()['summary']['offset']
        
        return status
    
    def check(self):
        return self.returnStatus() and (self.returnCount() > 0)
    
    def storeUpdate(self,record,last_updated,source):
        pass
    
    def storeCreateInst(self,record,id,last_updated,source,profile):
        pass
    
    def store(self):
        if self.check():
            create = []
            
            for record in self.response.json()[self.dataType]:
                id = record["_id"]
                last_updated = fixTime(record["last_updated"],record['utc_offset'])
                source, sourceCreated = Source.objects.get_or_create(source=record['source'],source_name=record['source_name'])
                profile = Profile.objects.get(validic_id=record['user_id'])
                
                # First check if the record exists, and if it only needs updates
                if self.model.objects.filter(pk=id,last_updated__lt=last_updated).exists():
                    self.storeUpdate(record,last_updated,source)
                
                # Else create if doesn't exist at all
                elif not self.model.objects.filter(pk=id).exists():
                    create.append(self.storeCreateInst(record,id,last_updated,source,profile))
            
            if len(create) > 0:
                self.model.objects.bulk_create(create)

class oFitness(oDataObject):
    model = Fitness
    dataType = "fitness"
    
    def storeUpdate(self,record,last_updated,source):
        activityCategory = ActivityCategory.objects.get_or_create(name="Other")
        activityType = ActivityType.objects.get_or_create(name="Other")
        intensity = Intensity.objects.get_or_create(name="Other")
        
        if 'activity_category' in record.keys() and record['activity_category']:
            activityCategory, status = ActivityCategory.objects.get_or_create(name=record['activity_category'])
        
        if 'activity_type' in record.keys() and record['activiy_type']:
            activityType, status = ActivityType.objects.get_or_create(name=record['activity_type'])
        
        if 'intensity' in record.keys() and record['intensity']:
            intensity, status = Intensity.objects.get_or_create(name=record['intensity'])
        
        self.model.objects.filter(pk=id).update(
                                                timestamp = fixTime(record['timestamp'],record['utc_offset']),
                                                last_updated = last_updated,
                                                source = source,
                                                validated = record['validated'],
                                                activity_category = activityCategory,
                                                activity_type = activityType,
                                                intensity = intensity,
                                                start_time = fixTime(record['start_time'],record['utc_offset']),
                                                distance = record['distance'],
                                                duration = record['duration'],
                                                calories = record['calories']
                                            )
    
    def storeCreateInst(self,record,id,last_updated,source,profile):
        activityCategory = ActivityCategory.objects.get_or_create(name="Other")
        activityType = ActivityType.objects.get_or_create(name="Other")
        intensity = Intensity.objects.get_or_create(name="Other")
        
        if 'activity_category' in record.keys() and record['activity_category']:
            activityCategory, status = ActivityCategory.objects.get_or_create(name=record['activity_category'])
        
        if 'activity_type' in record.keys() and record['activiy_type']:
            activityType, status = ActivityType.objects.get_or_create(name=record['activity_type'])
        
        if 'intensity' in record.keys() and record['intensity']:
            intensity, status = Intensity.objects.get_or_create(name=record['intensity'])
        
        return self.model(
                                id = id,
                                timestamp = fixTime(record['timestamp'],record['utc_offset']),
                                last_updated = last_updated,
                                source = source,
                                user = profile.user,
                                profile = profile,
                                validated = record['validated'],
                                activity_category = activityCategory,
                                activity_type = activityType,
                                intensity = intensity,
                                start_time = fixTime(record['start_time'],record['utc_offset']),
                                distance = record['distance'],
                                duration = record['duration'],
                                calories = record['calories']
                            )

class oRoutine(oDataObject):
    model = Routine
    dataType = "routine"
    
    def storeUpdate(self,record,last_updated,source):
        self.model.objects.filter(pk=id).update(
                                                timestamp = fixTime(record['timestamp'],record['utc_offset']),
                                                last_updated = last_updated,
                                                source = source,
                                                validated = record['validated'],
                                                steps = record['steps'],
                                                distance = record['distance'],
                                                floors = record['floors'],
                                                elevation = record['elevation'],
                                                calories = record['calories_burned'],
                                                water = record['water']
                                            )
    
    def storeCreateInst(self,record,id,last_updated,source,profile):
        return self.model(
                        id = id,
                        timestamp = fixTime(record['timestamp'],record['utc_offset']),
                        last_updated = last_updated,
                        source = source,
                        user = profile.user,
                        profile = profile,
                        validated = record['validated'],
                        steps = record['steps'],
                        distance = record['distance'],
                        floors = record['floors'],
                        elevation = record['elevation'],
                        calories = record['calories_burned'],
                        water = record['water']
                    )

class oNutrition(oDataObject):
    model = Nutrition
    dataType = "nutrition"
    
    def storeUpdate(record,last_updated,source):
        model.objects.filter(pk=id).update(
                                                timestamp = fixTime(record['timestamp'],record['utc_offset']),
                                                last_updated = last_updated,
                                                source = source,
                                                validated = record['validated'],
                                                calories = record['calories'],
                                                carbohydrates = record['carbohydrates'],
                                                fat = record['fat'],
                                                fiber = record['fiber'],
                                                protein = record['protein'],
                                                sodium = record['sodium'],
                                                water = record['water'],
                                                meal = record['meal']
                                            )
    
    def storeCreateInst(record,id,last_updated,source,profile):
        return model(
                        id = id,
                        timestamp = fixTime(record['timestamp'],record['utc_offset']),
                        last_updated = last_updated,
                        source = source,
                        user = profile.user,
                        profile = profile,
                        validated = record['validated'],
                        calories = record['calories'],
                        carbohydrates = record['carbohydrates'],
                        fat = record['fat'],
                        fiber = record['fiber'],
                        protein = record['protein'],
                        sodium = record['sodium'],
                        water = record['water'],
                        meal = record['meal']
                    )
    

class oSleep(oDataObject):
    model = Sleep
    dataType = "sleep"
    
    def storeUpdate(record,last_updated,source):
        model.objects.filter(pk=id).update(
                                                timestamp = fixTime(record['timestamp'],record['utc_offset']),
                                                last_updated = last_updated,
                                                source = source,
                                                validated = record['validated'],
                                                awake = record['awake'],
                                                deep = record['deep'],
                                                light = record['light'],
                                                rem = record['rem'],
                                                times_woken = record['times_woken'],
                                                total_sleep = record['total_sleep']
                                            )
    
    def storeCreateInst(record,id,last_updated,source,profile):
        return model(
                        id = id,
                        timestamp = fixTime(record['timestamp'],record['utc_offset']),
                        last_updated = last_updated,
                        source = source,
                        user = profile.user,
                        profile = profile,
                        validated = record['validated'],
                        awake = record['awake'],
                        deep = record['deep'],
                        light = record['light'],
                        rem = record['rem'],
                        times_woken = record['times_woken'],
                        total_sleep = record['total_sleep']
                    )

class oWeight(oDataObject):
    model = Weight
    dataType = "weight"
    
    def storeUpdate(record,last_updated,source):
        model.objects.filter(pk=id).update(
                                                timestamp = fixTime(record['timestamp'],record['utc_offset']),
                                                last_updated = last_updated,
                                                source = source,
                                                validated = record['validated'],
                                                weight = record['weight'],
                                                height = record['height'],
                                                free_mass = record['free_mass'],
                                                fat = record['fat_percent'],
                                                mass_weight = record['mass_weight'],
                                                bmi = record['bmi']
                                            )
    
    def storeCreateInst(record,id,last_updated,source,profile):
        return model(
                        id = id,
                        timestamp = fixTime(record['timestamp'],record['utc_offset']),
                        last_updated = last_updated,
                        source = source,
                        user = profile.user,
                        profile = profile,
                        validated = record['validated'],
                        weight = record['weight'],
                        height = record['height'],
                        free_mass = record['free_mass'],
                        fat = record['fat_percent'],
                        mass_weight = record['mass_weight'],
                        bmi = record['bmi']
                    )
                    

class oDiabetes(oDataObject):
    model = Diabetes
    dataType = "diabetes"
    
    def storeUpdate(record,last_updated,source):
        model.objects.filter(pk=id).update(
                                                timestamp = fixTime(record['timestamp'],record['utc_offset']),
                                                last_updated = last_updated,
                                                source = source,
                                                validated = record['validated'],
                                                c_peptide = record['c_peptide'],
                                                fasting_plasma_glucose_test = record['fasting_plasma_glucose_test'],
                                                hba1c = record['hba1c'],
                                                insulin = record['insulin'],
                                                oral_glucose_tolerance_test = record['oral_glucose_tolerance_test'],
                                                random_plasma_glucose_test = record['random_plasma_glucose_test'],
                                                relationship_to_meal = record['relationship_to_meal'],
                                                triglyceride = record['triglyceride'],
                                                blood_glucose = record['bloody_glucose']
                                            )
    
    def storeCreateInst(record,id,last_updated,source,profile):
        return model(
                        id = id,
                        timestamp = fixTime(record['timestamp'],record['utc_offset']),
                        last_updated = last_updated,
                        source = source,
                        user = profile.user,
                        profile = profile,
                        validated = record['validated'],
                        c_peptide = record['c_peptide'],
                        fasting_plasma_glucose_test = record['fasting_plasma_glucose_test'],
                        hba1c = record['hba1c'],
                        insulin = record['insulin'],
                        oral_glucose_tolerance_test = record['oral_glucose_tolerance_test'],
                        random_plasma_glucose_test = record['random_plasma_glucose_test'],
                        relationship_to_meal = record['relationship_to_meal'],
                        triglyceride = record['triglyceride'],
                        blood_glucose = record['bloody_glucose']
                    )
    
class Biometrics(oDataObject):
    model = Biometrics
    dataType = "biometrics"
    
    def storeUpdate(record,last_updated,source):
        model.objects.filter(pk=id).update(
                                                timestamp = fixTime(record['timestamp'],record['utc_offset']),
                                                last_updated = last_updated,
                                                source = source,
                                                validated = record['validated'],
                                                blood_calcium = record['blood_calcium'],
                                                blood_chromium = record['blood_chromium'],
                                                blood_folic_acid = record['blood_folic_acid'],
                                                blood_magnesium = record['blood_magnesium'],
                                                blood_potassium = record['blood_potassium'],
                                                blood_sodium = record['blood_sodium'],
                                                blood_vitamin_b12 = record['blood_vitamin_b12'],
                                                blood_zinc = record['blood_zinc'],
                                                creatine_kinase = record['creatine_kinase'],
                                                crp = record['crp'],
                                                diastolic = record['diastolic'],
                                                ferritin = record['ferritin'],
                                                hdl = record['hdl'],
                                                hscrp = record['hscrp'],
                                                il6 = record['il6'],
                                                ldl = record['ldl'],
                                                resting_heartrate = record['resting_heartrate'],
                                                systolic = record['systolic'],
                                                testosterone = record['testosterone'],
                                                total_cholestrol = record['total_cholestrol'],
                                                tsh = record['tsh'],
                                                uric_acid = record['uric_acid'],
                                                vitamin_d = record['vitamin_d'],
                                                white_cell_count = record['white_cell_count'],
                                                spo2 = record['spo2'],
                                                temperature = record['temperature']
                                            )
    
    
    def storeCreateInst(record,id,last_updated,source,profile):
        return model(
                        id = id,
                        timestamp = fixTime(record['timestamp'],record['utc_offset']),
                        last_updated = last_updated,
                        source = source,
                        user = profile.user,
                        profile = profile,
                        validated = record['validated'],
                        blood_calcium = record['blood_calcium'],
                        blood_chromium = record['blood_chromium'],
                        blood_folic_acid = record['blood_folic_acid'],
                        blood_magnesium = record['blood_magnesium'],
                        blood_potassium = record['blood_potassium'],
                        blood_sodium = record['blood_sodium'],
                        blood_vitamin_b12 = record['blood_vitamin_b12'],
                        blood_zinc = record['blood_zinc'],
                        creatine_kinase = record['creatine_kinase'],
                        crp = record['crp'],
                        diastolic = record['diastolic'],
                        ferritin = record['ferritin'],
                        hdl = record['hdl'],
                        hscrp = record['hscrp'],
                        il6 = record['il6'],
                        ldl = record['ldl'],
                        resting_heartrate = record['resting_heartrate'],
                        systolic = record['systolic'],
                        testosterone = record['testosterone'],
                        total_cholestrol = record['total_cholestrol'],
                        tsh = record['tsh'],
                        uric_acid = record['uric_acid'],
                        vitamin_d = record['vitamin_d'],
                        white_cell_count = record['white_cell_count'],
                        spo2 = record['spo2'],
                        temperature = record['temperature']
                    )
    