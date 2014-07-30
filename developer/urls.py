'''
Created on Feb 1, 2013

@author: stefanotranquillini
'''
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from developer import views


urlpatterns = patterns('',
    url(r'^app/create/$', login_required(views.ApplicationCreation.as_view()), name='d-application-create'),
    url(r'^app/$', login_required(views.ApplicationList.as_view()), name='d-application-list'),
    )