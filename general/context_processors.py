'''
Created on Oct 7, 2012

@author: stefanotranquillini
'''
from models import UserProfile
from crowdcomputer import settings

#this for having userProfile always in the session
#this is called before rendering the template, so forget about the session.
def addProfile(request):
    try:
        userProfile = UserProfile.objects.get(user=request.user)
        return {'user_profile':userProfile}    
    except:
        return {}
    
def addAppName(request):
    try:
        ret = {}
        ret['app_name']=settings.APP_NAME
        ret['short_app_name']=settings.SHORT_APP_NAME
        ret['crowdcomputer_url']=settings.CM_Location
        return ret 
    except:
        return {}

#def addTemplate(request):
#    try:
#        template = UserProfile.objects.get(user=request.user)
#        return {'user_profile':userProfile}    
#    except:
#        return {}
