from django.conf import settings as SETTINGS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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
from users.models import *

import csv, datetime, os, requests

@login_required
def profileEditGeneral(request):
    template = 'users/profile-edit.html'
    
    params = {
        'menuHighlight' : "general",
        'profile' : Profile.objects.get(user=request.user),
        'states' : State.objects.all().order_by('name_short')
    }
    
    return render(request,template,params)

@login_required
def profileUpdateGeneral(request):
    template = 'users/profile-edit.html'
    
    if request.method == "POST":
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        dob = datetime.datetime.strptime(request.POST['dob'], "%m/%d/%Y").strftime("%Y-%m-%d")
        
        address1 = request.POST['address1']
        address2 = request.POST['address2']
        city = request.POST['city']
        state = None
        
        if isinstance(request.POST['state'],int) and State.objects.filter(id=request.POST['state']).exists():
            state = State.objects.get(id=request.POST['state'])
        
        zipcode = request.POST['zipcode']
        
        profileComplete = False
        
        if address1 and address2 and city and state and zipcode:
            profileComplete = True
            
        emailSubscription = False
        
        if 'emailSubscription' in request.POST.keys():
            emailSubscription = True
        
        Profile.objects.filter(user=request.user).update(
            profile_complete = profileComplete,
            address1 = address1,
            address2 = address2,
            city = city,
            state=state,
            zipcode = zipcode,
            dob = dob,
            email_subscription = emailSubscription
        )
    
    params = {
        'menuHighlight' : "general",
        'profile' : Profile.objects.get(user=request.user),
        'states' : State.objects.all().order_by('name_short')
    }
    
    return render(request,template,params)

@login_required
def profilePasswordChange(request):
    template = 'users/password-change.html'
    
    params = {
        'menuHighlight' : "password",
    }
    
    return render(request,template,params)

@login_required
def profilePasswordUpdate(request):
    template = 'users/password-change.html'
    
    if request.method == "POST":
        currentPass = request.POST['currentPass']
        newPass = request.POST['newPass']
        confirmPass = request.POST['confirmPass']
        
        if request.user.check_password(currentPass) and (newPass == confirmPass):
            u = User.objects.get(id=request.user.id)
            u.set_password(newPass)
            u.save()
            
            user = authenticate(username=u.email, password=newPass)
            login(request, user)
    
    params = {
        'menuHighlight' : "password",
        'profile' : Profile.objects.get(user=request.user)
    }
    
    return render(request,template,params)

def signin(request):
    template = 'users/login.html'
    
    if ('page_type_action' in request.session.keys()) and not request.session['page_type_action']:
        request.session['error'] = None
    
    request.session['page_type_action'] = False
    
    return render(request,template)

def actionLogin(request):
    page = 'users-login'
    
    request.session['error'] = None
    
    if request.method == "POST":
        status = True
        
        for each in ['email','password']:
            if each not in request.POST.keys():
                status = False
                break
        
        if status:
            email = request.POST['email']
            password = request.POST['password']
            
            user = authenticate(username=email, password=password)
            
            if user is not None and user.is_active:
                login(request, user)
                page = 'portal-dashboard'
            
            else:
                request.session['error'] = "Invalid email and/or password"
        
        else:
            request.session['error'] = "Please complete all required fields"
        
    else:
        request.session['error'] = "Invalid request type"
    
    request.session['page_type_action'] = True
    
    return redirect(page)

def register(request):
    template = 'users/register.html'
    
    if ('page_type_action' in request.session.keys()) and not request.session['page_type_action']:
        request.session['error'] = None
    
    request.session['page_type_action'] = False
    
    return render(request,template)

def actionRegister(request):
    page = 'users-register'
    
    request.session['error'] = None
    
    if request.method == "POST":
        status = True
        
        for each in ['firstName','lastName','gender','dob','email','password','terms']:
            if each not in request.POST.keys():
                status = False
                break
        
        if status:
            firstName = request.POST['firstName']
            lastName = request.POST['lastName']
            gender = request.POST['gender']
            dob = datetime.datetime.strptime(request.POST['dob'], '%m/%d/%Y').date()
            
            email = request.POST['email'].lower()
            password = request.POST['password']
            terms = request.POST['terms']
            
            if not User.objects.filter(email__iexact=email).exists():
                
                # Create the user
                user = User(username=email,email=email,first_name=firstName,last_name=lastName)
                user.set_password(password)
                user.save()
                
                sub = SubscriptionPlan.objects.get(name_short__exact="Basic")
                # Create a user profile
                p = Profile(user=user,subscription=sub,gender=gender,dob=dob)
                
                # Create a Validic POST request for obtaining the user
                url = 'https://api.validic.com/v1/organizations/' + SETTINGS.VALIDIC_ID + '/users.json'
                
                headers = {'Content-Type': 'application/json'}
                
                # Issue validic request
                r = requests.post(
                                    url,
                                    data = json.dumps({
                                            'user' : {'uid' : str(user.id)},
                                            'access_token' : SETTINGS.VALIDIC_KEY
                                        }),
                                    headers=headers
                                )
                
                # Parse Validic's response and update our user profile
                if r.status_code in [200,201,"200","201"]:
                    validicUser = r.json()['user']
                    
                    if validicUser['uid'] in (user.id, str(user.id)):
                        p.validic_id = validicUser['_id']
                        p.validic_access_token = validicUser['access_token']
                        p.save()
                        
                        u = authenticate(username=email, password=password)
                        
                        if u is not None:
                            login(request,u)
                        
                        page = 'users-profile-general-edit'
            
            else:
                request.session['error'] = "Email address already in use"
        
        else:
            request.session['error'] = "Please complete all required fields"
    
    request.session['page_type_action'] = True
    
    return redirect(page)
    
    
@login_required
def signout(request):
    logout(request)
    
    return redirect('users-login')
