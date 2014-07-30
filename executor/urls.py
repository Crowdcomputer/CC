from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from executor import views
from executor.views import TaskListExe

urlpatterns = patterns('',
    url(r'^/$',login_required(TemplateView.as_view(template_name="executor/home.html")), name='e-home'),
    url(r'^/list/$',login_required(TaskListExe.as_view()), name='e-list'),
    url(r'^/list/(?P<id>\d+)/$',login_required(TaskListExe.as_view()), name='e-list-owner'),
    url(r'^execute/bid/(?P<uuid>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/$', views.bid, name='bid'),
    url(r'^/execute/instance/(?P<uuid>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/$', views.InstanceExecute, name='e-execute-instance'),
    url(r'^/execute/(?P<uuid>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/$', views.TaskExecute, name='e-execute'),
    url(r'^/taskinstance/(?P<uuid>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/update/$', views.TaskInstanceUpdate, name='e-ti-update'),
    url(r'^/taskinstance/(?P<uuid>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/finish/$', views.TaskInstanceFinish, name='e-ti-finish'),
    url(r'^/turk/execute/instance/(?P<uuid>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/$', views.InstanceExecute, name='mt-execute-instance'),
)
