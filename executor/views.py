# Create your views here.
from django.core.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.generic.list import ListView
from executor.forms import BidForm
from general.models import Task, TaskInstance, Data, UserProfile, HumanTask, \
    Process
from general.utils import createInstance, copyReqParameter, createObject, \
    startProcess, checkIfProcessFinished
import json
import logging
from uuid import uuid4
from general.views import errorPage
from general import utils
from django.http.response import Http404
from general.utils import checkIfFinished
from django.utils.timezone import now
from django.contrib.auth.models import User
import urllib
import crowdcomputer
from rest_framework.authtoken.models import Token
from general.mturk import mTurk
from crowdcomputer import settings


# TODO: comment and check.
# i don't understand much of the code, it was too long time ago (plus i didn't write it) and there's no comments explaining what the code does.

log = logging.getLogger(__name__)

class TaskListExe(ListView):
    object_list = 'task_list'
    template_name = 'executor/task_list.html'

    def get_queryset(self):
#        only humantasks
        queryset = Task.objects.select_subclasses("humantask").filter(status='PR').filter(humantask__platform="CC")
        if 'id' in self.kwargs:
            log.debug("looking for %s",self.kwargs['id'])
            try:
                owner = User.objects.get(pk=self.kwargs['id'])
                queryset.filter(owner=owner)
            except:
                log.debug("there's no user")
        return queryset

def baseChecking(request, task):
    if task.is_deleted:
        messages.warning(request, 'Well, The task is deleted and will never be active again')
        return redirect(reverse('e-home'))
    if task.is_stopped:
        messages.warning(request, 'Well, The task is currently not active')
        return redirect(reverse('e-home'))
    if task.is_expired:
        task.finish()
        messages.warning(request, 'Well, The task is expired, unfortunately you can not perform it')
        return redirect(reverse('e-home'))
    if task.is_finished:
        task.finish()
        messages.warning(request, 'Well, The task is finished')
        return redirect(reverse('e-home'))

    return None



@login_required
def bid(request, uuid):
    """

    :param request:
    :param uuid:
    :return:
    """
    form = BidForm()
    task = get_object_or_404(HumanTask, uuid=uuid)
    basecheck = baseChecking(request, task)
    if  basecheck is not None:
        return basecheck
    if request.POST:
        form = BidForm(request.POST)
        if form.is_valid():
            # get the task
            #TODO: it's not working
            amount = form.cleaned_data['amount']
            if (amount<=task.reward.quantity):
            #         here create a task instance with this amount and assign to the user.
                data = '{}'
                if "data" in  task.parameters:
                    data = task.parameters['data']
                log.debug("Data %s", data)
                d = Data(value=data)
                d.save()
                # get the first instance
                qs = task.taskinstance_set.filter(status='ST')
                if qs.count() > 0:
                    taskinstance = qs[0]
                    taskinstance.parameters['reward']=amount
                    taskinstance.status='PR'
                    taskinstance.executor=request.user
                    taskinstance.save()
                    task.status='PR'
                    task.save()
                    return render_to_response('executor/task_execute.html', {'task':task, 'taskinstance': taskinstance.id}, context_instance=RequestContext(request))
                else:
                    messages.warning(request, 'This task is completed')
                    return redirect(reverse('home'))
            else:
                messages.warning(request, 'Your bid was rejected')
    return render_to_response('executor/bid.html', {'task':task,'form':form}, context_instance=RequestContext(request))
        #ask for bid

@login_required
def TaskExecute(request, uuid):
    ''' When user opens up the page for executing a task, no instance assigned '''
    log.debug("execute")
    # here we need some logic though
    task = get_object_or_404(HumanTask, uuid=uuid)
    basecheck = baseChecking(request, task)
    if  basecheck is not None:
        return basecheck
# If task there are no any not assigned tasks and no tasks assigned to this user
    if (task.taskinstance_set.filter(status='ST').count() == 0 and len(task.taskinstance_set.filter(executor=request.user, status='PR')) == 0):
        log.debug("there is NOT")
        if task.parameters["type"] != "contest":
            messages.warning(request, 'Well, There are no any available instances in this task')
            return redirect(reverse('e-home'))



#    else:
#        # if there is an instance assigned to this user - we return it
#        log.debug("there is")
#        if len(task.taskinstance_set.filter(executor=request.user).filter(status='PR')) > 0:
#            taskinstance = task.taskinstance_set.filter(status='PR', executor=request.user)[0]
#        # if there is no instances assigned to this user - we return the first instance which is free and not assignet to anybody
#        else:
#            taskinstance = task.taskinstance_set.filter(status='ST')[0]
# #            taskinstance.executor=request.user
#        if (taskinstance.executor):
#            log.debug("executor %s ",taskinstance.executor.username)
#        else:
#            log.debug("no exec")
    # data=''
    else:
        if len(task.taskinstance_set.filter(executor=request.user, status='PR')) == 0 and task.parameters["type"] == "bid":
            return redirect(reverse('bid', kwargs={'uuid':uuid}))
        else:
            return render_to_response('executor/task_execute.html', {'task':task, 'taskinstance': 0}, context_instance=RequestContext(request))

@login_required
def InstanceExecute(request, uuid):

    ''' When user opens up the page for executing a instance assigned to him'''
    # here we need some logic though
    taskinstance = get_object_or_404(TaskInstance, uuid=uuid)
    ht = taskinstance.task.humantask
    turk = False
    if taskinstance.task.humantask.platform == "MT":
        turk = True
        log.debug('turk')
    else:
        if taskinstance.executor != request.user:
            raise Http404

    if ht is None:
        return redirect(Http404)
    basecheck = baseChecking(request, taskinstance.task)
    if  basecheck is not None:
        return basecheck
    if taskinstance.is_finished:
        messages.warning(request, 'Well, This task instance is already finished')
    elif taskinstance.is_validation:
        messages.warning(request, 'Well, This task instance is already finished')
    elif turk:
#            if mturk rediret to the correct page.
        log.debug("turk")
        pars = "?uuid=%s" % taskinstance.uuid + "&ccl=" + urllib.quote_plus(crowdcomputer.settings.CM_Location)
        pars = pars + "&" + copyReqParameter(request)
        return render_to_response('executor/turk_task_execute.html', {'task':taskinstance.task, 'taskinstance':taskinstance, 'pars':pars}, context_instance=RequestContext(request))
    elif not taskinstance.executor:
        messages.warning(request, 'Strange, but the task instance is not assigned to anybody, it is not allowed to perform it.')
    else:
        return render_to_response('executor/task_execute.html', {'task':ht, 'taskinstance':taskinstance}, context_instance=RequestContext(request))
    url = taskinstance.task.process.application.url
    log.debug(url)
    return errorPage(request, url)



# AJAX creation of response. It should return the id of response or error

@login_required
@csrf_protect
def TaskInstanceUpdate(request, uuid):
    ''' assign instance to user '''
    log.debug("task instance update")
    if request.is_ajax():
        log.debug("task instance update")
        message = {}
        task = HumanTask.objects.get(uuid=uuid)
        qs = task.taskinstance_set.filter(status='PR').filter(executor=request.user)
#        check if user has an instance?

        if (qs.count() > 0):
            taskinstance = qs[0]
            log.debug("there is an already assigned instance")
        else:
            if task.parameters["type"] == 'contest':
                log.debug("contest")
#                FIXME: always with none
                data = '{}'
                if "data" in  task.parameters:
                    data = task.parameters['data']
                log.debug("Data %s", data)
                d = Data(value=data)
                d.save()
                createInstance(task, d)
                taskinstance = task.taskinstance_set.filter(status='ST')[0]
            else:
#            search for the first not completed instance
                qs = task.taskinstance_set.filter(status='ST')
                if qs.count() > 0:
                    taskinstance = qs[0]
                else:

    #                if none, then reject the user
                    message['success'] = False
                    message['detail'] = 'Somebody performed all the instances of this task, so try another task.'
                    return HttpResponse(json.dumps(message), content_type="application/json")
#        if no instance then error


        if (taskinstance is None):

        # If the amount of instances is fixed - we show error
                message['success'] = False
                message['detail'] = 'Error'
                return HttpResponse(json.dumps(message), content_type="application/json")

#        else
        elif (taskinstance.status == 'ST' or taskinstance.status == 'PR') and taskinstance.task.is_inprocess:
#            it means that may be there are no any stopped instances - but there is an instance which is in process and assigned to you - then you will be given it to work on
            log.debug("here we are ")
            taskinstance.executor = request.user
            log.debug("executor = %s", taskinstance.executor)
            # taskinstance.date_started=datetime.now()
            # I don't remember wether I should save it or not
            taskinstance.save()
            taskinstance.start()
            data={}
            if taskinstance.input_data:
                data = json.dumps(taskinstance.input_data.value)
                log.debug("input data" + data)
            message['success'] = True
            message['input_data'] = data
            message['taskinstance'] = taskinstance.uuid
#            if taskinstance.executor:
#            assigned at the top, not needed here anymore
            message['taskinstance_user'] = taskinstance.executor.username
            message['taskinstance_id'] = taskinstance.id
            # message['detail'] = taskinstance.id
            return HttpResponse(json.dumps(message), content_type="application/json")
        else:
            message['success'] = False
            message['detail'] = 'The task is not active'
            return HttpResponse(json.dumps(message), content_type="application/json")




# @login_required
@csrf_protect
def TaskInstanceFinish(request, uuid):
    ''' Finishes the instance '''
    message = {}

#        retrive the instance
    taskinstance = TaskInstance.objects.get(uuid=uuid)
    if (taskinstance is None):
#            if instance does not exists: Error
        message['success'] = False
        message['detail'] = 'Error response, id %s user %s' % (uuid)
        return HttpResponse(json.dumps(message), content_type="application/json")
    else:
#            it's there
        message['success'] = True
        message['redirect'] = taskinstance.task.process.application.url
        if taskinstance.is_finished:
#                user is completing an ended instance
            message['success'] = False
            message['detail'] = 'Your response is already finished'
            return HttpResponse(json.dumps(message), content_type="application/json")

        else:
#                get user output
            turk = False
            if taskinstance.task.humantask.platform == 'MT':
                turk = True
                log.debug('Turk')
            values = {}
            p = taskinstance.parameters
            if turk:
                for k, v in request.REQUEST.iteritems():
                    log.debug("iteritems %s %s", k, v)
                    if k not in ["callback", "jsonp", "_", "assignmentId", "hitId"]:
                        values[k] = v
#                        update paarmeters. hitId already there.
                    if k in ["assignmentId", "workerId"]:
                        p[k] = v
#                        just to be sure that we store the data
                taskinstance.save()
            else:
                values = request.REQUEST['output']
            log.debug("the user sent: %s",values)
            data = Data(value=values)
            data.save()

            user = request.user
#           check if turk

            if turk:
                username = values['workerId']
                log.debug("username mturk %s", username)
                password = User.objects.make_random_password()
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.email = username + "@mturk.com"
                    user.password = password
                    user.save()
                taskinstance.executor = user
                taskinstance.save()
            else:
                taskinstance.executor = request.user
                taskinstance.save()
            log.debug("executor is : %s", taskinstance.executor.username)
            taskinstance.output_data = data

            message['success'] = True
            message['redirect'] = taskinstance.task.process.application.url

#            check if task has validation.
            validation = taskinstance.task.humantask.validation
            if validation is not None:
                if validation != "VALID":
                    taskinstance.validation_status()
                    owner = taskinstance.task.owner
                    app = taskinstance.task.process.application
                    process = Process(title="Validation for " + str(taskinstance.task.title), description="Validation process for task " + str(taskinstance.pk), owner=owner, application=app)
                    process.save()
                    taskinstance.validation = process
                    process.validates = taskinstance
                    taskinstance.save()

                    data = {}
                    data['processDefinitionKey'] = validation

                    variables = []
                    variables.append(createObject('processId', process.pk))
                    variables.append(createObject('app_token', app.token))
                    token, created = Token.objects.get_or_create(user=owner)
                    variables.append(createObject('user_token', token.key))

                    variables.append(createObject('data', [json.dumps(taskinstance.output_data.value)]))
                    variables.append(createObject('task_instance', taskinstance.pk))
                    data['variables'] = variables
#                    data['processId']=process.pk
#                    data['app_token']=app.token
#                    data.update(variables)
#                    data['user_token']=token.key
#                    data['data']=json.dumps([taskinstance.output_data.value])
#                    data['task_instance']=taskinstance.pk
                    dumps = json.dumps(data)
                    log.debug("dumps data %s", dumps)
                    startProcess(process, validation, data)
#                    retrive main process and check if it's finished

#                    checkIfProcessFinished(taskinstance.task.process)
                else:
                    pars = taskinstance.parameters
                    if pars is None:
                        pars = {}
                    pars['validation'] = True
#                    taskinstance.save()
                    taskinstance.finish()

                    checkIfProcessFinished(taskinstance.task.process)
#                startProcess(taskinstance.task.validation,taskinstance.pk)
            else:
#                check if task is finished
                taskinstance.finish()
#                this evaluates just the validation process, not the main.
                p_pars = taskinstance.task.process.parameters
                if 'validation_process' in p_pars:
                    t_process = Process.objects.get(id=p_pars['validation_process'])
                    checkIfProcessFinished(t_process)
                else:
                    checkIfProcessFinished(taskinstance.task.process)

#            ToDO:
#            Check if task is validation, in case update the task instance it refers to.
#            reward validators
#            else
#            TODO: call the validation process.



#                this check if task is over.and in case triggers the next step in the BPMN

            if turk:
                callback = request.REQUEST.get('jsonp', '')
                resp = json.dumps(message)
                response = callback + '(' + resp + ');'
                log.debug(response)
                response = HttpResponse(response, content_type="application/json")
                return response

        return HttpResponse(json.dumps(message), content_type="application/json")



