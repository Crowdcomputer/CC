from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from requester import views

urlpatterns = patterns('',
    url(r'^/$', login_required(TemplateView.as_view(template_name="requester/home.html")), name='r-home'),
    #----------------------------------------------------------------------------------------------------------------------
    url(r'^/process/(?P<process_id>\d+)/task/create/task/$', login_required(views.TaskCreationHub.as_view()), name='r-task-create'),
    url(r'^/process/(?P<process_id>\d+)/task/create/human/$', login_required(views.HumanTaskCreation.as_view()), name='r-task-create-human'),
    url(r'^/process/(?P<process_id>\d+)/task/create/machine/$', login_required(views.MachineTaskCreation.as_view()), name='r-task-create-machine'),
   # url(r'^/process/(?P<process_id>\d+)/task/create/splitdata/$', login_required(views.SplitDataTaskCreation.as_view()), name='r-task-create-splitdata'),
   # url(r'^/process/(?P<process_id>\d+)/task/create/filterdata/$', login_required(views.FilterDataTaskCreation.as_view()), name='r-task-create-filterdata'),
    
    #----------------------------------------------------------------------------------------------------------------------  
    url(r'^/process/(?P<pk>\d+)/update/$', login_required(views.ProcessUpdate.as_view()), name='r-process-update'),
    url(r'^/process/(?P<process_id>\d+)/delete/$', views.ProcessDelete, name='r-process-delete'),
    url(r'^/process/(?P<process_id>\d+)/start/$', views.ProcessStart, name='r-process-start'),
    url(r'^/process/(?P<process_id>\d+)/stop/$', views.ProcessStop, name='r-process-stop'),
    url(r'^/process/create/$', login_required(views.ProcessCreation.as_view()), name='r-process-create'),
    url(r'^/processes/$', login_required(views.ProcessList.as_view()), name='r-process'),
    url(r'^/process/(?P<process_id>\d+)/tasklist/$', login_required(views.TaskList.as_view()), name='r-task-list'),
#    url(r'^/confirmation/$', login_required(views.Confirmation.as_view()), name='r-confirmation'),

#    url(r'^/process/(?P<process_id>\d+)/tasklist/(?P<prev_process_id>\d+)/(?P<prev_task_id>\d+)/$', login_required(views.TaskList.as_view()), name='r-task-list-validation'),

#    url(r'^/task/create/$', views.TaskCreation, name='r-task-create'),
    url(r'^/process/(?P<process_id>\d+)/task/(?P<pk>\d+)/update/$', login_required(views.TaskUpdate.as_view()), name='r-task-update'),
    url(r'^/process/(?P<process_id>\d+)/task/(?P<task_id>\d+)/cvs/$', views.exportcsv, name='r-task-csv'),

    url(r'^/process/(?P<process_id>\d+)/task/(?P<task_id>\d+)/taskinstances/$', login_required(views.TaskInstanceList.as_view()), name='r-taskinstances'),
    url(r'^/process/(?P<process_id>\d+)/task/(?P<task_id>\d+)/delete/$', views.TaskDelete, name='r-task-delete'),
    url(r'^/process/(?P<process_id>\d+)/task/(?P<task_id>\d+)/start/$', views.TaskStartStop, name='r-task-start'),
    url(r'^/process/(?P<process_id>\d+)/task/(?P<task_id>\d+)/stop/$', views.TaskStop, name='r-task-stop'),

    url(r'^/process/upload/$', views.uploadProcess, name='bpmn-upload'),

#    url(r'^/process/(?P<process_id>\d+)/task/(?P<task_id>\d+)/finish/$', views.TaskFinish, name='r-task-finish'),

    )
