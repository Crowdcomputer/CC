from django.contrib import admin
from models import UserProfile, Language,  Task, TaskInstance, Data, Process,Application,Reward
from general.models import HumanTask, TaskActiviti, ProcessActiviti
#this is for adding the userprofile inthe admin part
admin.site.register(UserProfile)
admin.site.register(Task)
admin.site.register(Language)
admin.site.register(TaskInstance)
admin.site.register(Reward)
admin.site.register(Data)
admin.site.register(Process)
admin.site.register(Application)
admin.site.register(HumanTask)
admin.site.register(ProcessActiviti)
admin.site.register(TaskActiviti)