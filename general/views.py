# Create your views here.
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from general.forms import UserForm, LoginForm
from general.models import UserProfile
from rest_framework.authtoken.models import Token
import json
import logging
import urllib2
from crowdcomputer import settings





log = logging.getLogger(__name__)

#profile view.
@login_required
def ProfileView(request):
#for the time being only fb
    l=request.user.social_auth.filter(provider='facebook')
    social_user=request.user.userprofile
    if len(l)>0:
        social_user = l[0]
    return render_to_response('general/profile.html', {'social_user':social_user}, context_instance=RequestContext(request))

@login_required
def Logout(request):
    logout(request)
    return redirect('/')

@login_required
def GeoLoc(request):
    return render_to_response('general/geoloc.html', context_instance=RequestContext(request))

@login_required
#this is a test for finding information from geo loc and retrive the user position.
def AddGeoLoc(request):
#     FIXME: removed
#     user_profile = request.user.userprofile
#     url_s = 'http://ws.geonames.org/extendedFindNearby?lat=%s&lng=%s' % (user_profile.latitude, user_profile.longitude)
#     log.debug(url_s)
#     url = urllib2.urlopen(url_s).read()
#
#     root = objectify.fromstring(url)
#     for geo in root.geoname:
#         log.debug('geoname %s ' % (geo.name))
# #        log.debug(geo.name)
    return redirect(reverse('home'))

#create the json answer when updating via post the location
@login_required
@csrf_protect
def UpdateLoc(request):
    message = {}
    message['status'] = 'ko'
    
    if request.is_ajax():
        if request.method == 'POST':
            message['status'] = 'ok'
#            here the userprofile must be retrived, it's not in the request
            userProfile = UserProfile.objects.get(user=request.user)
            userProfile.latitude = request.POST['latitude']
            userProfile.longitude = request.POST['longitude']
            userProfile.save()
            # Here we can access the POST data
    return HttpResponse(json.dumps(message), content_type="application/json")

def CreateUser(request):
    if request.user.is_authenticated():
        return redirect(reverse_lazy('home'))
    if request.method=='GET':
        form = UserForm()
        return render_to_response('general/creation.html',{'form':form}, context_instance=RequestContext(request))
    if request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            u = User.objects.create(username=username)
            u.first_name=username
            u.set_password(password)
            u.email=email
            u.save()
            up,c=UserProfile.objects.get_or_create(user=u)
            up.save()
            ul=authenticate(username=username, password=password)
            if ul is not None:
                login(request, ul)
            return redirect(reverse_lazy('home'))
        else:
            return render_to_response('general/creation.html',{'form':form}, context_instance=RequestContext(request))

@login_required
def ApiLogin(request):
    token, created = Token.objects.get_or_create(user=request.user)
    f = str(request.GET['from'])
    log.debug("request form value: " + f)
    f+=("?token=%s"%(str(token)))
    return redirect(f)


def Login(request):
    if request.user.is_authenticated():
        return redirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                redirect_to = request.REQUEST.get('next', '')
                login(request, user)
                return HttpResponseRedirect(redirect_to)
            else:
                messages.info(request,'username and password not valid')
                return render_to_response('general/login.html', {'form': form}, context_instance=RequestContext(request))
        else:
            return render_to_response('general/login.html', {'form': form}, context_instance=RequestContext(request))
    else:
        form = LoginForm()
        context = {'form': form}
        return render_to_response('general/login.html', context, context_instance=RequestContext(request))


def errorPage(request,redirect=None, message = None):
    if not redirect:
        redirect=settings.CM_Location
    if message:
        messages.error(request, message)
    return render_to_response('general/error.html', {'redirect':redirect}, context_instance=RequestContext(request))

