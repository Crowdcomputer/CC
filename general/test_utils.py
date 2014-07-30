from general.models import TaskInstance, Task, Process, Data
from django.utils.datetime_safe import datetime
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import utc

def getUser():
    u, create= User.objects.get_or_create(username='test',email='test@test.com',password='test')
    return u
    
def createProcess(title):
    t,create = Process.objects.get_or_create(title=title,user=getUser())
    return t

def createTasks(title, process):
    date=datetime.now()+timedelta(days=10)
    t,create = Task.objects.get_or_create(title=title,date_deadline=date.replace(tzinfo=utc),user=getUser(),process=process)
    return t

def createTaskInstance(t,data):
    ti = TaskInstance(user=getUser(),)
    ti.task=t
    d=Data(value=data)
    d.save()
    ti.output=d
    ti.save()

def addTaskInstance(task,data):
    ti = task.taskinstance_set.filter(status='ST')[0]
    d=Data(value=data)
    d.save()
    ti.output=d
    ti.status='FN'
    ti.save()
    
        


def lenInsOut(task):
    instances = task.taskinstance_set.all()
    count =0
    for instance in instances:
        value = instance.output.value
        if isinstance(value, list):
            for v in value:
                count+=1
        else:
            count+=1
    return count