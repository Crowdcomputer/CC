'''
Created on Oct 5, 2012

@author: stefanotranquillini
'''
from social_auth.backends.facebook import FacebookBackend
from models import UserProfile, Language
import time
import logging


def get_user_addinfo(backend, details, response, social_user, uid,\
                    user, *args, **kwargs):
    log = logging.getLogger(__name__)
    log.debug('here we are')
    #load profile, defaults when creation empty
    #it returns a touple, profile is the object, created is the boolean if it's created or exists
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        log.debug('created')
    else:
        log.debug('name: %s' %(user.username))
    #if facebook then steal data
    if backend.__class__ == FacebookBackend:  
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        profile.picture = url # depends on where you saved it
        log.debug(profile.picture)
        #get name surname
        first_name = response.get('first_name')
        log.debug(first_name)
        if first_name:
            profile.name=first_name
            log.debug(profile.name)
        surname =response.get('last_name')
        if surname:
            profile.surname=surname
            log.debug(profile.surname)
        birthday =response.get('birthday')
        if birthday:
            date=birthday
            date = date.replace(u'\xa0', '') # removes \xa0 char (&nbsp)
            date = date.encode() # encode to asccii from unicode
            date = time.strptime(date, "%m/%d/%Y") 
            profile.birthday=time.strftime("%Y-%m-%d", date);
            log.debug(profile.birthday)
        email =response.get('email')
        if email:
            profile.email=email
            log.debug(profile.email)
        locale =response.get('locale')
        if locale:
            profile.locale=locale
            log.debug(profile.locale)
        gender =response.get('gender')
        if gender:
            profile.gender=gender
            log.debug(profile.gender)
        #must parse hometown to exrtract the name of the town.
        hometown =response.get('hometown')
        if hometown:
            profile.hometown=hometown.get('name')
            log.debug(profile.hometown)
        languages = response.get('languages')
        log.debug(languages)
        if languages:
            for lang in languages: 
                l, created = Language.objects.get_or_create(fb_id=lang.get('id'), defaults={'fb_id':lang.get('id'),'name':lang.get('name')})
                l.save()
                profile.languages.add(l)
        profile.save()
