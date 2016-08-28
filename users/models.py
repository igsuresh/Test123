from __future__ import unicode_literals

import json, uuid

from django.db import models
from django.core import serializers
from django.contrib.auth.models import User

class State(models.Model):
    name_short = models.CharField(max_length=2)
    name_long = models.CharField(max_length=10)
    
    def __unicode__(self):
        return u'%s' % (self.name_long)

class SubscriptionPlan(models.Model):
    name_short = models.CharField(max_length=10)
    name_long = models.CharField(max_length=200,blank=True,null=True)
    
    def __unicode__(self):
        return u'%s' % (self.name_short)

class Profile(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    
    profile_complete = models.BooleanField(default=False)
    
    address1 = models.CharField(max_length=100,blank=True,null=True)
    address2 = models.CharField(max_length=10,blank=True,null=True)
    city = models.CharField(max_length=100,blank=True,null=True)
    state = models.ForeignKey(State,blank=True,null=True)
    zipcode = models.CharField(max_length=10,blank=True,null=True)
    
    gender = models.CharField(max_length=1,choices=GENDER_CHOICES,default=MALE)
    dob = models.DateField(db_index=True)
    
    validic_id = models.CharField(max_length=200,db_index=True)
    validic_access_token = models.CharField(max_length=200)
    
    email_subscription = models.BooleanField(default=True)
    
    subscription = models.ForeignKey(SubscriptionPlan)
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.user.first_name, self.user.last_name)
        
class Billing(models.Model):
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=10,blank=True,null=True)
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State)
    zipcode = models.CharField(max_length=10)
    
    stripe_id = models.CharField(max_length=200)
    subscription = models.ForeignKey(SubscriptionPlan)
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.user.first_name, self.user.last_name)