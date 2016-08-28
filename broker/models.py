from __future__ import unicode_literals

import json, uuid

from django.db import models
from django.core import serializers
from django.contrib.auth.models import User

from users.models import *

class Source(models.Model):
    source = models.CharField(max_length=100)
    source_name = models.CharField(max_length=300)
    
    def __unicode__(self):
        return u'%s' % (self.source)

class DataObject(models.Model):
    id = models.CharField(primary_key=True,max_length=100,db_index=True, editable=False)
    timestamp = models.DateTimeField(db_index=True)
    last_updated = models.DateTimeField(blank=True,null=True)
    
    source = models.ForeignKey(Source)
    
    validated = models.BooleanField(default=False)
    
    user = models.ForeignKey(User,on_delete=models.CASCADE,db_index=True)
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,db_index=True)
    
    class Meta:
        abstract=True
    
    def __unicode__(self):
        return u'%s %s | %s | %s' % (self.user.first_name, self.user.last_name, self.timestamp, self.id)

class Fitness(DataObject):
    activity_category = models.CharField(max_length=100,null=True,blank=True)
    activity_type = models.CharField(max_length=100,null=True,blank=True)
    
    intensity = models.CharField(max_length=100,null=True,blank=True)
    start_time = models.DateTimeField()
    distance = models.DecimalField(max_digits=9,decimal_places=2)
    duration = models.DecimalField(max_digits=12,decimal_places=2)
    calories = models.DecimalField(max_digits=9,decimal_places=2,null=True)

class Routine(DataObject):
    steps = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    distance = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    floors = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    elevation = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    calories = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    water = models.DecimalField(max_digits=9,decimal_places=2,null=True)

class Nutrition(DataObject):
    calories = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    carbohydrates = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    fat = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    fiber = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    protein = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    sodium = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    water = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    meal = models.CharField(max_length=100,blank=True,null=True)

class Sleep(DataObject):
    awake = models.DecimalField(max_digits=12,decimal_places=2,null=True)
    deep = models.DecimalField(max_digits=12,decimal_places=2,null=True)
    light = models.DecimalField(max_digits=12,decimal_places=2,null=True)
    rem = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    times_woken = models.DecimalField(max_digits=9,decimal_places=2,null=True)
    total_sleep = models.DecimalField(max_digits=9,decimal_places=2,null=True)

class Weight(DataObject):
    weight = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    height = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    free_mass = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    fat = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    mass_weight = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    bmi = models.DecimalField(max_digits=5,decimal_places=2,null=True)

class Diabetes(DataObject):
    c_peptide = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    fasting_plasma_glucose_test = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    hba1c = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    insulin = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    oral_glucose_tolerance_test = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    random_plasma_glucose_test = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    relationship_to_meal = models.CharField(max_length=100,null=True,blank=True)
    triglyceride = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    blood_glucose = models.DecimalField(max_digits=8,decimal_places=2,null=True)

class Biometrics(DataObject):
    blood_calcium = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    blood_chromium = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    blood_folic_acid = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    blood_magnesium = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    blood_potassium = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    blood_sodium = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    blood_vitamin_b12 = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    blood_zinc = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    creatine_kinase = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    crp = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    diastolic = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    ferritin = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    hdl = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    hscrp = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    il6 = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    ldl = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    resting_heartrate = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    systolic = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    testosterone= models.DecimalField(max_digits=8,decimal_places=2,null=True)
    total_cholestrol = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    tsh = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    uric_acid = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    vitamin_d = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    white_cell_count = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    spo2 = models.DecimalField(max_digits=8,decimal_places=2,null=True)
    temperature = models.DecimalField(max_digits=8,decimal_places=2,null=True)
