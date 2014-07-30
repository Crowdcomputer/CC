'''
Created on Oct 9, 2012

@author: stefanotranquillini
'''
from datetime import datetime, timedelta
from django import template
from django.template.defaultfilters import stringfilter
import logging
register = template.Library()



@stringfilter
@register.filter(name='fromsec')
def secondsConversion(value):
    sec = timedelta(seconds=0)
    d = datetime(1,1,1) + sec
    t_str ="days:%d hours:%d: minutes:%d seconds:%d" % (d.day-1, d.hour, d.minute, d.second)
    return t_str

@stringfilter
@register.filter(name='to_tr_class')
def toTrClass(value):
    switch = {
        'PR': 'warning',
        'ST': 'info',
        'DL': 'error',
        'FN': 'success',
        'VL': 'warning'
    }
    return switch[value]

@stringfilter
@register.filter(name='validation_to_tr_class')
def valToTrClass(value):
    if value:
        return 'success'
    else:
        return 'error'
#    switch = {
#        True: 'success',
#        False: 'error',
#        '': 'action'
#    }
#    return switch[value]

@stringfilter
@register.filter(name='taskData')
def displayTaskData(value,status):
    if (status==''):
        return  str(value.task_set.count())
    return str(value.task_set.filter(status=status).count())

@register.filter(name='percentage')  
def percentage(fraction, population): 
    try:  
        return "%i" % ((float(fraction) / float(population)) * 100)  
    except ValueError:  
        return '' 
    
@register.filter(name='c_percentage')  
def c_percentage(fraction, population): 
    return str(100-int(percentage(fraction, population)))

@register.filter(name='sub')  
def sub(a, b): 
    return a-b

#TODO: extend to all the other types, and create a copy of this, we need it later on.
@register.filter(name='typeOfTask')  
def typeOfTask(obj):
    if obj.humantask is not None:
        if obj.humantask.platform=="MT":
            return "TurkTask"
        else:
            return 'HumanTask'
    elif obj.validationtak is not None:
        return 'ValidationTask'
    else:
        return 'Task'
        
    

@register.filter(name='classname')
def classname(obj):
    classname = obj.__class__.__name__
    return classname