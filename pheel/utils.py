import calendar, json, urllib, csv
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext, Context

from datetime import datetime,timedelta, tzinfo

def cRender(template,params,request=None):
	if request:
		return render(request,template,params)
	
	else:
		return render(template,params)
	
def cRedirect(name,params):
	return redirect(reverse(name,args=params))

def cDaysInYear(year):
	return 366 if calendar.isleap(year) else 365

class FixedOffset(tzinfo):
    """Fixed offset in minutes: `time = utc_time + utc_offset`."""
    def __init__(self, offset):
        self.__offset = timedelta(minutes=offset)
        hours, minutes = divmod(offset, 60)
        #NOTE: the last part is to remind about deprecated POSIX GMT+h timezones
        #  that have the opposite sign in the name;
        #  the corresponding numeric value is not used e.g., no minutes
        self.__name = '<%+03d%02d>%+d' % (hours, minutes, -hours)
    
    def utcoffset(self, dt=None):
        return self.__offset
    
    def tzname(self, dt=None):
        return self.__name
    
    def dst(self, dt=None):
        return timedelta(0)
    
    def __repr__(self):
        return 'FixedOffset(%d)' % (self.utcoffset().total_seconds() / 60)

def fixTime(t,u_str=None):
    
    fixed = t
    
    naive = datetime.strptime(fixed[:-6],"%Y-%m-%dT%H:%M:%S")
    
    offset_str = u_str.replace(":","")
    
    offset = int(offset_str[-4:-2]) * 60 + int(offset_str[-2:])
    
    if offset_str[0] == "-":
        offset = -offset
    
    fixed = naive.replace(tzinfo=FixedOffset(offset))
    
    return fixed
