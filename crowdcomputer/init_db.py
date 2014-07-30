'''
Created on Nov 26, 2012

@author: stefanotranquillini
'''

from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from general.models import Application
from uuid import uuid4

def init():
    initAppsAndCC()

def initAppsAndCC():
    try:
        user, c = User.objects.get_or_create(username='crowdcomputer',email="crowdcomputer@gmail.com",password="this.is.spam")
        user.save()
        print "%s %s"%(user.username,c)
        app, c = Application.objects.get_or_create(name="crowdcomputer",url="http://www.crowdcomputer.org",user=user)
        if c:
            app.token=str(uuid4()).replace('-','')
        app.save()
        print "%s %s" %(app.name, app.token)

        app, c = Application.objects.get_or_create(name="bpmn",url="http://www.crowdcomputer.org",user=user)
       
        if c:
            app.token=str(uuid4()).replace('-','')
        print "%s %s" %(app.name, app.token)
        app.save()
        bpmn, c = Group.objects.get_or_create(name='bpmn')
        bpmn.save()
    except Exception, e:
        print e
        print 'exception'  

def createAdmin(username,password,email):
    try:
        admin, c = User.objects.get_or_create(email=email)
        if c:
            admin.set_password(password)
            admin.username=username
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            print 'creato'
        else:
            admin.set_password(password)
            admin.save()
            print 'aggiornato'
    except Exception:
        print 'exception'

        