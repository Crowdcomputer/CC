from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from restapi import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = patterns('restapi.views',
        url(r'^$', 'api_root', name='api-root'),
        url(r'^process/create/$', views.ProcessCreate.as_view(), name='process-create'),
        url(r'^process/(?P<pk>[0-9]+)/task/human/create/$', views.HumanTaskCreate.as_view(), name='human-task-create'),
        url(r'^task/data/split/$', views.SplitTask.as_view(), name='split-task'),
        url(r'^task/data/merge/$', views.MergeTask.as_view(), name='merge-task'),
        url(r'^task/data/filter/$', views.FilterTask.as_view(), name='filter-task'),
        url(r'^task/object/merge/$', views.JoinObjectTask.as_view(), name='join-object-task'),
        url(r'^task/object/split/$', views.SplitObjectTask.as_view(), name='split-object-task'),
#        url(r'^task/turk/create/$', views.TurkTaskCreate.as_view(), name='turk-task-create'),
        url(r'^task/(?P<pk>[0-9]+)/start/$', views.StartTask.as_view(), name='task-start'),
        url(r'^task/(?P<pk>[0-9]+)/status/$', views.TaskStatus.as_view(), name='task-status'),
        url(r'^task/(?P<pk>[0-9]+)/results/$', views.TaskResults.as_view(), name='task-result'),
        url(r'^taskinstance/(?P<pk>[0-9]+)/validate/$', views.Validate.as_view(), name='taskinstance-validate'),
        url(r'^reward/create/$', views.RewardCreate.as_view(), name='reward-create'),
        url(r'^token/', views.TokenList.as_view(), name='api-token'),
        url(r'^test/', views.TestView.as_view(), name='test'),
#        url(r'^process/(?P<pk>[0-9]+)/task/$', views.ProcessTaskCreate.as_view(), name='task-create'),
#        url(r'^process/(?P<pk>[0-9]+)/task/start/$', views.ProcessTaskCreate.as_view(), name='task-start'),
#        url(r'^task/(?P<pk>[0-9]+)/taskinstances/$', views.TaskInstanceList.as_view(), name='task-instances'),
#        url(r'^taskinstance/(?P<pk>[0-9]+)/$', views.TaskInstanceDetail.as_view(), name='task-instance-detail'),
#        url(r'^token/', views.TokenList.as_view()),
#        url(r'^api-token-auth/', obtain_auth_token),
#        url(r'^users/$', views.UserList.as_view(), name='user-list'),
#        url(r'^user/create/$', views.UserCreate.as_view(), name='user-create'),
#        url(r'^users/(?P<pk>\d+)/$', views.UserDetail.as_view(), name='user-detail'),
#        url(r'^users/(?P<pk>\d+)/sendemail/$', views.SendEmail.as_view(), name='user-send-email'),
#        url(r'^users/me/$', views.MyUserDetail.as_view(), name='my-detail'),
# #        url(r'^groups/$', views.GroupList.as_view(), name='group-list'),
#        url(r'^groups/(?P<pk>\d+)/$', views.GroupDetail.as_view(), name='group-detail'),
#        url(r'^processes/$', views.ProcessList.as_view(), name='process-list'),
#        url(r'^processes/(?P<pk>[0-9]+)/tasklist/$', views.ProcessTaskList.as_view(), name='task-list'),
#        url(r'^processes/(?P<pk>[0-9]+)/startstop/$', views.ProcessStartStop.as_view(), name='process-start-stop'),
#        url(r'^processes/(?P<pk>[0-9]+)/task/$', views.ProcessTaskCreate.as_view(), name='task-create'),
#        url(r'^processes/(?P<pk>[0-9]+)/$', views.ProcessDetail.as_view(), name='process-detail'),
#        url(r'^task/(?P<pk>[0-9]+)/$', views.TaskDetail.as_view(), name='task-detail'),
#        url(r'^task/(?P<pk>[0-9]+)/taskinstances/$', views.TaskInstanceList.as_view(), name='task-instances'),
#        url(r'^task/(?P<pk>[0-9]+)/taskinstances/status/$', views.TaskInstancesStatuses.as_view(), name='task-instnace-statuses'),
#        url(r'^taskinstance/(?P<pk>[0-9]+)/$', views.TaskInstanceDetail.as_view(), name='task-instance-detail'),
#        url(r'^task/(?P<pk>[0-9]+)/instances/status$', views.TaskDetail.as_view(), name='task-detail'),
#        url(r'^reward/create/', views.RewardCreate.as_view(), name = 'reward-create'),
#        url(r'^reward/(?P<pk>[0-9]+)/', views.RewardReadUpdate.as_view(), name = 'reward'),
#        url(r'^reward/(?P<pk>[0-9]+)/update/', views.RewardReadUpdate.as_view(), name = 'reward-update'),

       url(r'^token/', views.TokenList.as_view()),
#        url(r'^api-token-auth/', obtain_auth_token),
    )
    
    # Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])


    # Default login/logout views
    
# urlpatterns += patterns('',
#        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# )
#    
