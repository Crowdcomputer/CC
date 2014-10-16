'''
Created on May 22, 2013

@author: stefanotranquillini
'''
from datetime import datetime
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import jsonfield
from django.contrib.auth.models import User
from django.utils.timezone import utc
from model_utils.managers import InheritanceManager
# from MySQLdb.constants.FIELD_TYPE import NULL
from rest_framework.authtoken.models import Token


class Language(models.Model):
    name = models.CharField(max_length=100, default='')
    fb_id = models.CharField(max_length=100, default='0')

    def __unicode__(self):
        return str(self.fb_id)


# if we don't switch to 1.5 this is fine
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    # do we need login data?
    # login = models.ForeignKey(Login)
    name = models.CharField(max_length=100, default='')
    surname = models.CharField(max_length=100, default='')
    birthday = models.DateField(default=datetime.now, blank=True)
    email = models.CharField(max_length=100, default='')
    locale = models.CharField(max_length=100, default='')
    picture = models.CharField(max_length=255, default='')
    gender = models.CharField(max_length=100, default='')
    hometown = models.CharField(max_length=255, default='')
    # languages goes as 1-M relation,
    languages = models.ManyToManyField(Language, blank=True, null=True)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    reward_dollars = models.DecimalField(decimal_places=2, max_digits=8, default=Decimal('0.0'))
    reward_time = models.IntegerField(default=0)
    # checkins = models.TextField()

    def __unicode__(self):
        return self.name + ' ' + self.surname

    @property
    def count_tasks(self):
        return len(self.user.task_set.all())

    @property
    def count_responses(self):
        return len(self.user.response_set.all())


class Application(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200, default='', unique=True)
    token = models.CharField(max_length=200, default='')
    url = models.URLField(max_length=400, default='', null=True, blank=True)

    def __unicode__(self):
        return self.name


STATUS_CHOISE_PROCESS = (('PR', 'In process'), ('ST', 'Stopped'), ('FN', 'Finished'), ('DL', 'Deleted'),)


class Process(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=1000, default='')
    date_created = models.DateTimeField(auto_now_add=True, auto_now=False)
    parameters = jsonfield.JSONField()
    application = models.ForeignKey(Application)
    status = models.CharField(max_length=2, choices=STATUS_CHOISE_PROCESS, default='ST', blank=True)
    validates = models.OneToOneField('TaskInstance', blank=True, null=True)

    def __unicode__(self):
        return '[' + str(self.id) + '] ' + str(self.title)

    @property
    def is_inprocess(self):
        return self.status == 'PR'

    @property
    def is_stopped(self):
        return self.status == 'ST'

    @property
    def is_finished(self):
        return self.status == 'FN'

    @property
    def is_deleted(self):
        return self.status == 'DL'

    def start(self):
        self.status = 'PR'
        self.save()

    def stop(self):
        self.status = 'ST'
        self.save()


REWARDS = (('CCM', 'CrowdComputer'), ('USD', 'Dollars'), ('EUR', 'Euro'), ('COF', 'Coffies'),)
STRATEGIES = (('ALL', 'Pay all'), ('NONE', 'Pay None'), ('VALID', 'Pay Valid'), ('BEST', 'Pay Best'))


class Reward(models.Model):
    # description = models.CharField(max_length=100, default='')
    quantity = models.DecimalField(decimal_places=2, max_digits=8, default=Decimal('0.0'), blank=True, null=True)
    type = models.CharField(max_length=3, choices=REWARDS, default='CCM')
    strategy = models.CharField(max_length=10, choices=STRATEGIES, default='ALL')


class Data(models.Model):
    value = jsonfield.JSONField()

    def __unicode__(self):
        return str(self.id)


STATUS_CHOISE = (('PR', 'In process'), ('ST', 'Stopped'), ('FN', 'Finished'), ('DL', 'Deleted'),)


class Task(models.Model):
    owner = models.ForeignKey(User)
    process = models.ForeignKey(Process)
    title = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=1000, default='')
    date_created = models.TimeField(auto_now_add=True, auto_now=False)
    date_deadline = models.DateTimeField(default=lambda: (datetime.now() + timedelta(days=7)), auto_now_add=False)
    parameters = jsonfield.JSONField(blank=True)
    objects = InheritanceManager()
    status = models.CharField(max_length=2, choices=STATUS_CHOISE, default='ST', blank=True)

    def __unicode__(self):
        return '[' + str(self.id) + '] ' + str(self.title)

    @property
    def is_inprocess(self):
        return self.status == 'PR'

    @property
    def is_stopped(self):
        return self.status == 'ST'

    @property
    def is_finished(self):
        return self.status == 'FN'

    @property
    def is_deleted(self):
        return self.status == 'DL'

    @property
    def is_expired(self):
        return (self.date_deadline < datetime.utcnow().replace(tzinfo=utc))


    @property
    def instances_given(self):
        return self.taskinstance_set.filter(status='FN').count()

    @property
    def instances_available(self):
        return self.taskinstance_set.filter(status='ST').count()

    @property
    def instances_running(self):
        valid = self.taskinstance_set.filter(status='VL').count()
        progress = self.taskinstance_set.filter(status='PR').count()
        return valid + progress

    @property
    def instances_amount(self):
        return self.taskinstance_set.all().count()

    def finish(self):
        self.status = 'FN'
        self.save()


    def delete(self):
        self.status = 'DL'
        self.save()

    def start(self):
        self.status = 'PR'
        self.process.start()
        self.save()

    def stop(self):
        self.status = 'ST'
        self.save()


# this does not work , if it's human where's uuid?
# TACTICS = ((1, 'Task'), ('MT', 'Amazon Mechancial Turk'))
class ValidationTask(Task):
    # value is inside taskinstance.data.value
    #    strategy / tactic
    quality_threshold = models.IntegerField()
# reward = models.OneToOneField(Reward, null=True, blank=True)
#    uuid = models.CharField(max_length=36, default='')
#  number_of_instances = models.IntegerField(default=1)


# page_url = models.URLField(max_length=400, default='', null=True, blank=True)

# nothing to add, maybe remove something from general Task
class MachineTask(Task):
    service_url = models.URLField(max_length=400, default='', null=True, blank=True)


PLATFORMS = (('CC', 'CrowdComputer'), ('MT', 'Amazon Mechancial Turk'),)


class HumanTask(Task):
    # is_unique = models.BooleanField(default=True)
    number_of_instances = models.IntegerField(default=1)
    uuid = models.CharField(max_length=36, default='')
    page_url = models.URLField(max_length=400, default='', null=True, blank=True)
    platform = models.CharField(max_length=2, choices=PLATFORMS, default='CC')
    validation = models.CharField(max_length=400, default=None, null=True, blank=True)
    reward = models.OneToOneField(Reward, null=True, blank=True)


#
# #I think that we don't need 'no split in thi class'
# SPLIT_CHOICE = ((1, 'No split'), (2, 'Set of N'), (3, 'Set of N with M overlapp'), (4, 'Combinations'),)    
# class SplitDataTask(Task):
#    split = models.IntegerField(choices=SPLIT_CHOICE, default=1)
#    split_field_N = models.PositiveSmallIntegerField(default=1, blank=True, null=True)
#    split_field_M = models.PositiveSmallIntegerField(default=1, blank=True, null=True)
#   
# #    we probably need this beacuse of the input_url
#    def save(self, force_insert=False, force_update=False, using=None):
#        self.title = 'Split'
#        self.description = 'Split the data'
#        #self.input_url='http://' #- i think that we don't need this part as we don't have it anymore in the task model
#        Task.save(self, force_insert=force_insert, force_update=force_update, using=using)

# #  we have to decide what to put here
# FILTER_CHOICE = ((1, 'Has a substring'), (2, 'More than treshold'), (3, 'Equal to'),)    
# class FilterDataTask(Task): 
#    filter = models.IntegerField(choices=FILTER_CHOICE, default=1)
#    filter_field = models.CharField(max_length=1024, default='')
#    filter_value = models.CharField(max_length=1024, default='')
#    filter_exclude = models.BooleanField(default=False) # if true - than "does not have", "less then", "not equal to"
#    def save(self, force_insert=False, force_update=False, using=None):
#        self.title = 'Filter'
#        self.description = 'Filter the data'
#        #self.input_url='http://' #- i think that we don't need this part as we don't have it anymore in the task model
#        Task.save(self, force_insert=force_insert, force_update=force_update, using=using)     
#
# #  we have to decide what to put here
# class MergeDataTask(Task): 
#    # If we simply merge data with equal structure- i think that we can have it blank (no additional fields)
#    def save(self, force_insert=False, force_update=False, using=None):
#        self.title = 'Merge'
#        self.description = 'Merge the data'
#        self.input_url = 'http://'
#        Task.save(self, force_insert=force_insert, force_update=force_update, using=using)   
#
# #  we have to decide what to put here
# class JoinObjectTask(Task): 
#    join_common_field = models.CharField(max_length=1024, default='') #here we might add functionality that if you need several common fields - then comma separated.
#    def save(self, force_insert=False, force_update=False, using=None):
#        self.title = 'Join Object'
#        self.description = 'Join Object the data'
#        self.input_url = 'http://'
#        Task.save(self, force_insert=force_insert, force_update=force_update, using=using)       
#
# #  we have to decide what to put here (not sure how to do this)
# class SplitObjectTask(Task): 
#    def save(self, force_insert=False, force_update=False, using=None):
#        self.title = 'Split Object'
#        self.description = 'Split Object the data'
#        self.input_url = 'http://'
#        Task.save(self, force_insert=force_insert, force_update=force_update, using=using)    

class TaskInstance(models.Model):
    # executor
    executor = models.ForeignKey(User, null=True, blank=True)
    # mto1: many Responses generated for one task
    task = models.ForeignKey(Task)
    STATUS_CHOISE = (('ST', 'Stopped'), ('PR', 'Process'), ('FN', 'Finished'), ('VL', 'Validation'))
    status = models.CharField(max_length=2, choices=STATUS_CHOISE, default='ST')
    date_created = models.DateTimeField(auto_now_add=True, auto_now=False)
    date_started = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    date_finished = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    input_data = models.ForeignKey(Data, null=True, blank=True, related_name="input_data")
    output_data = models.ForeignKey(Data, null=True, blank=True, related_name="output_data")
    uuid = models.CharField(max_length=36, default='')
    parameters = jsonfield.JSONField()
    quality = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0)

    validation = models.OneToOneField(Process, null=True, blank=True)

    def __unicode__(self):
        return str(self.id)

    @property
    def is_inprocess(self):
        return self.status == 'PR'

    @property
    def is_stopped(self):
        return self.status == 'ST'

    @property
    def is_finished(self):
        return self.status == 'FN'

    @property
    def is_deleted(self):
        return self.status == 'DL'

    @property
    def is_validation(self):
        return self.status == 'VL'

    def start(self):
        self.status = 'PR'
        self.date_started = datetime.now()
        self.task.start()
        self.save()


    def finish(self):
        self.status = 'FN'
        self.date_finished = datetime.now()
        self.save()

    def validation_status(self):
        self.status = 'VL'
        self.save()


class ValidationTaskInstance(TaskInstance):
    to_validate = models.ForeignKey(TaskInstance, related_name='validate_by')


class UserBPMN(models.Model):
    user = models.OneToOneField(User)
    password_activiti = models.CharField(max_length=200)


class ProcessActiviti(models.Model):
    process = models.OneToOneField(Process)
    key = models.CharField(max_length=200)
    instanceID = models.CharField(max_length=200)
    processDefinition = models.CharField(max_length=200)


#    why not the picture?

class TaskActiviti(models.Model):
    task = models.OneToOneField(Task)
    receive = models.CharField(max_length=200)


# #this is used to create the flow, 
# #only for hte UI engine
# class TaskProcess(models.Model):
#    task = models.ForeignKey(Task)
#    input_tasks = models.ManyToManyField("self")
#    output_tasks = models.ManyToManyField("self")
#
# #    this is the table where we store process execution information for the "process" engine of UI part.
# # BPMN part does not uses this
# class ProcessInstance(models.Model):
#    process = models.ForeignKey(Process)
#    STATUS_CHOISE = (('PR', 'In process'), ('ST', 'Stopped'), ('FN', 'Finished'), ('DL', 'Deleted'),)
#    status = models.CharField(max_length=2, choices=STATUS_CHOISE, default='ST')
#    startTask = models.ForeignKey(TaskProcess)
#    
#    

@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
