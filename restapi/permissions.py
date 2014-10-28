'''
Created on Jan 23, 2013

@author: stefanotranquillini
'''

from rest_framework import permissions
import logging
from rest_framework.permissions import SAFE_METHODS
from django.contrib.auth.models import User
from general.models import Application

log = logging.getLogger(__name__)


#check if user is owner of the item
class IsOwnerOrGoOut(permissions.BasePermission):

    def has_permission(self, request, view, obj=None):
#        log.debug("IsOwnerOrGoOut")
        # Skip the check unless this is an object-level test
        if obj is None:
            log.debug("obj is none")
            return True
        #if it's the instance        
        if isinstance(obj, User):
#            log.debug("obj is user")
            return True
        if hasattr(obj, 'task'):  
            log.debug("task %s",obj.task.owner == request.user)
            return obj.task.owner == request.user
#        this goes after since even the instance has a user but it's not the one we have to check
        elif hasattr(obj, 'owner'):
            log.debug("owner %s",obj.owner == request.user)
            return obj.owner == request.user
#        todo not sure this is fine for instnaces.
        elif hasattr(obj, 'executor'):  
             log.debug("executor %s",obj.executor == request.user )
             return obj.executor == request.user
        else:
            log.debug("none of above")
            return False

#check if belongs to the app
class IsFromApp(permissions.BasePermission):

    def has_permission(self, request, view, obj=None):
#        log.debug("IsFromApp")
        # Skip the check unless this is an object-level test
        #log.debug('is from app')
        if request.method in SAFE_METHODS:
            
#            log.debug('safe method')
            return True
        #FIXME remove app
        apptoken = Application.objects.get(name="bpmn")
        log.debug("apptoken " + apptoken)
        if apptoken is None:
            log.debug('apptoken is none')
            return False
        
        if obj is None:
            log.debug('obj none')
            return True
        #if it's the instance        
        # Write permissions are only allowed to the owner of the snippet
     
        #log.debug('apptoken %s',apptoken)
#       check if user has user 
#    this is a process
        token = None
        if hasattr(obj, 'application'):
            token = obj.application.token
#            log.debug('process')
#        this is a task
        elif hasattr(obj, 'process'):
            token = obj.processs.application.token
#            log.debug('task')
#        this is an instance
        elif hasattr(obj, 'task'):
            token = obj.task.process.application.token
#            log.debug('instance')
        else:
#            log.debug("none of above")
            return False
#        log.debug("token %s, apptoken %s",(token,apptoken))
        ret = (token == apptoken)
        log.debug('auth res %s %s vs %s'% (ret,token,apptoken))
        return ret
