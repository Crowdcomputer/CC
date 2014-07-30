from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from general import views

urlpatterns = patterns('',
	url(r'^geoloc/updateloc/$', views.UpdateLoc, name='updateloc'),
    url(r'^geoloc/$', views.GeoLoc, name='geoloc'),
    url(r'^geoloc/more$', views.AddGeoLoc, name='addgeoloc'),
    url(r'^create/$', views.CreateUser, name='register'),
    url(r'^profile/$', views.ProfileView, name='profile'),
    url(r'^login/$', views.Login, name='login'),
    url(r'^apilogin/$', views.ApiLogin, name='apilogin'),
    url(r'^logout/$', views.Logout, name='logout'),
    url(r'^thanks/$', TemplateView.as_view(template_name='general/thanks.html'), name='thanks'),
#    url(r'^$',redirect_to, {'url':reverse_lazy('e-list')}),
    url(r'^$', TemplateView.as_view(template_name="general/home.html"), name='home'),
    )
