from django.conf.urls import patterns, include, url
from django.contrib import admin
from api.views import router, task_router


admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^api2/', include(router.urls)),
                       url(r'^api2/', include(task_router.urls)),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^exe', include('executor.urls')),
                       # url(r'^mt', include('mturk.urls')),
                       url(r'^req', include('requester.urls')),
                       url(r'^api/', include('restapi.urls')),
                       url(r'^dev/', include('developer.urls')),
                       #    url(r'^bpmn/', include('bpmn.urls')),
                       url(r'^', include('general.urls')),
                       url(r'', include('social_auth.urls')),

)
urlpatterns += patterns('django.contrib.flatpages.views',
                        (r'^(?P<url>.*)$', 'flatpage'),
)