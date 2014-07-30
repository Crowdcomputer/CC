    # Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from general.models import Process, Task, Reward, Application, ProcessActiviti
from general.utils import startTask, stopTask, mturkTask, receiveTask, fixSF, \
    createObject, forceFinish, startProcess, checkIfProcessFinished, \
    forceProcessFinish
from general.utils import checkIfFinished
from requester.forms import ProcessForm, HumanTaskForm, MachineTaskForm  # , SplitDataTaskForm,FilterDataTaskForm
from uuid import uuid4
import logging
from general import mturk
from django.contrib import messages
from django.views.generic.base import TemplateView
from general.tasks import deleteInstance
from requester.forms import UploadFileForm
from lxml import etree
from crowdcomputer import settings
import requests
from requests.auth import HTTPBasicAuth
from django.http.response import Http404, HttpResponse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json
import zipfile
from django.db import transaction
from django.core.files.base import ContentFile
import os
from django.core.files.storage import default_storage
import csv







log = logging.getLogger(__name__)


class TaskCreationHub(TemplateView):
    template_name = "requester/task_creation_hub.html"
    
    def get_context_data(self, **kwargs):
        contex_data = TemplateView.get_context_data(self, **kwargs)
        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
        contex_data['process'] = process;
        return contex_data

# @login_required
# def ProcessList(request):
#    process_list = Process.objects.filter(user=request.user).order_by('date_created')
#    return render_to_response('requester/process_list.html', {'process_list':process_list}, context_instance=RequestContext(request))
class ProcessList(ListView):
    template_name = 'requester/process_list.html'
    paginate_by = 10
  
    
    def get_queryset(self, **kwargs):
        process_list = Process.objects.filter(owner=self.request.user).filter(validates=None).order_by('-pk')
#        .order_by('-status')
       # process_list = sorted(process_list, key=lambda a: a.int_status)
        return process_list

class TaskList(ListView):
#    FIXME: do we need to call trigger task function?
#    if so then extend render_to_response and add the function there.
    template_name = 'requester/task_list.html'
    paginate_by = 10
    
    def get_queryset(self):
        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
        task_list = Task.objects.filter(owner=self.request.user, process=process).order_by('date_deadline')
#        FIXME
#        task_list = sorted(task_list, key=lambda a: a.int_status)
#        task_list=process.task_set.all()
        checkIfProcessFinished(process)
        return task_list
    
    def get_context_data(self, **kwargs):
        contex_data = ListView.get_context_data(self, **kwargs)
        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
        contex_data['process'] = process;
        if process.validates:
            contex_data['prev_process_id'] = process.validates.task.process.pk
            contex_data['prev_task_id'] = process.validates.task.pk
#        check if it's bpmn providded and put th epicutre here
        bpmnprocess = process.processactiviti
#        if bpmnprocess is not None:
#            contex_data['picture']='ciao'
        return contex_data

# def TaskList(request, process_id):
#    #retrive list or 404, then short it
#    # cant' use get_list_or_404 because at the first time list is empty!
# #   task_list = get_list_or_404(Task,user=request.user).order_by('date_deadline')
#    process = get_object_or_404(Process, pk=process_id, user=request.user)
#    task_list = Task.objects.filter(user=request.user,process=process).order_by('date_deadline')
#    task_list = sorted(task_list, key=lambda a: a.int_status)
#    
#    #stop_expired(task_list)
#    #we can not just stop tasks, we should check if we should run other tasks, so we use trigger
#    triggerTasks(process)
#    return render_to_response('requester/task_list.html', {'task_list':task_list,'process':process}, context_instance=RequestContext(request))

    # return render_to_response('requester/task_list.html', {'task_list':task_list, 'process_id':process_id}, context_instance=RequestContext(request))



# @login_required
# def ProcessCreation(request):
#    if request.method == 'POST':
#        form = ProcessForm(request.POST, user=request.user)
#        if form.is_valid():
#            #create a task
#            process = Process(user_id=request.user.id,
#                      title=form.cleaned_data['title'],
#                      description=form.cleaned_data['description']
#                    )
#            process.save()
#            return redirect(ProcessList)
#        else:
#            #form error
#            return render_to_response('requester/creation.html', {'form':form}, context_instance=RequestContext(request))   
#    else:
#        #create form
#        form = ProcessForm(None ,user=request.user)
#        return render_to_response('requester/creation.html', {'form':form}, context_instance=RequestContext(request))

class ProcessCreation(CreateView):
    template_name = 'requester/creation.html'
    form_class = ProcessForm
    success_url = reverse_lazy('r-process')
    
    def get_initial(self):
        initial = {}
        initial['owner'] = self.request.user
        app = Application.objects.get(name='crowdcomputer')
        initial['application'] = app
        return initial
    
# DOES NOT WORK
# the urls was wrong, this misses the model, get_queryset
class ProcessUpdate(UpdateView):
    template_name = 'requester/creation.html'
    form_class = ProcessForm
    success_url = reverse_lazy('r-process')
    model = Process
    
    def get_initial(self):
        initial = {}
        initial['user'] = self.request.user
        return initial
    
    def get_queryset(self):
        qs = super(ProcessUpdate, self).get_queryset()
        return qs.filter(user=self.request.user)

@login_required
def ProcessDelete(request, process_id):
    # this actually set the status to delete
#    template = get_object_or_404(Template,pk=template_id,user=request.user)    
#    task=get_object_or_404(Task,pk=task_id, template=template)
#    task.delete()
    process = get_object_or_404(Process, pk=process_id, owner=request.user)
    process.status = "DL"
    process.save()
    if process.processactiviti:
        if settings.CELERY:
            deleteInstance.delay(process)
        else:
            deleteInstance(process)
#    if process.processactiviti:
#        process.processactiviti.deplyment_id
#        repository/deployments/
    # redirect to the view, don't put logic if it's already implemented

    return redirect(reverse('r-process'))



class HumanTaskCreation(CreateView):
    template_name = 'requester/creation.html'
    form_class = HumanTaskForm
    
    
    def get_initial(self):
        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
        initial = {}
        initial['process'] = process
        initial['owner'] = self.request.user
        return initial
    
    def get_success_url(self):
        return reverse('r-task-list', args=(self.kwargs['process_id'],))
   
    def form_invalid(self, form):
        log.debug("form is not valid")
        log.debug(form.errors)
        return CreateView.form_invalid(self, form)
    def form_valid(self, form):
        rew = Reward(type=form['type'].value(), quantity=form['quantity'].value())
        rew.save()
        task = form.save()
        task.reward = rew
        task.uuid = uuid4()
        task.save()
        log.debug("saved")
        return HttpResponseRedirect(self.get_success_url())

class MachineTaskCreation(CreateView):
    template_name = 'requester/creation.html'
    form_class = MachineTaskForm
    
    
    def get_initial(self):
        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
        initial = {}
        initial['process'] = process
        initial['owner'] = self.request.user
        return initial
    
    def get_success_url(self):
        return reverse('r-task-list', args=(self.kwargs['process_id'],))
   
'''class SplitDataTaskCreation(CreateView):
    template_name = 'requester/creation.html'
    form_class = SplitDataTaskForm
    
    
    def get_initial(self):
        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
        initial = {}
        initial['process']=process
        initial['owner']=self.request.user
        return initial
    
    def get_success_url(self):
        return reverse('r-task-list',args=(self.kwargs['process_id'],))

class FilterDataTaskCreation(CreateView):
    template_name = 'requester/creation.html'
    form_class = FilterDataTaskForm
    
    
    def get_initial(self):
        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
        initial = {}
        initial['process']=process
        initial['owner']=self.request.user
        return initial
    
    def get_success_url(self):
        return reverse('r-task-list',args=(self.kwargs['process_id'],))
#    def save(self):
#        reward_form = RewardForm(self.request.POST)
#        htform = HumanTaskForm(self.request.POST)
#        reward = reward_form.save();
#        ht=htform.save(commit=False);
#        ht.reward=reward
#        ht.uuid=uuid4()
#        ht.save()
#        log.debug('saved')
#        return ht
       '''

# class TaskCreation(CreateView):
#    template_name = 'requester/creation.html'
#    form_class = TaskForm
#    
#    
#    def get_initial(self):
#        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
#        initial = {}
#        initial['process']=process
#        initial['owner']=self.request.user
#        return initial
#   
#    def get_success_url(self):
#        return reverse('r-task-list',args=(self.kwargs['process_id'],))
#    
#    def form_valid(self, form):
# #        log.debug("type %s",form['reward_type'].value())
#        rew = Reward(type=form['reward_type'].value(),quantity=form['reward_quantity'].value())
#        rew.save()
#        task = form.save()
#        task.reward=rew
#        task.uuid = uuid4()
# #        crete the reward
#        task.save()
#        log.debug("saved")
# #        check if superuser
#        if task.isMturk:
#            if self.request.user.is_superuser:
#                mturkTask(task,form['reward_mturk'].value())
#            else:
#                messages.warning(self.request, 'You don\'t have grants to create tasks on AMT')
#        return HttpResponseRedirect(self.get_success_url())
# 

# @login_required
# def TaskCreation(request, process_id):
#    process = get_object_or_404(Process, pk=process_id, user=request.user)
#    if request.method == 'POST':
#        form = TaskForm(request.POST, user=request.user)
#        if form.is_valid():
#            #create a task
#            task = Task(user_id=request.user.id,
#                      title=form.cleaned_data['title'],
#                      description=form.cleaned_data['description'],
#                      process=process,
#                      input_url=form.cleaned_data['input_url'],
#                      input_task=form.cleaned_data['input_task'],
#                      redirect=form.cleaned_data['redirect'],
#                      instances_required=form.cleaned_data['instances_required'],
#                      date_deadline=form.cleaned_data['date_deadline'],
#                      uuid=uuid4())
#            task.save()
#            return redirect(TaskList)
#        else:
#            #form error
#            return render_to_response('requester/creation.html', {'form':form}, context_instance=RequestContext(request))   
#    else:
#        #create form
#        form = TaskForm(None ,user=request.user)
#        return render_to_response('requester/creation.html', {'form':form}, context_instance=RequestContext(request))

# @login_required
# def TaskDuplicate(request, task_id):
#    task = get_object_or_404(Task, pk=task_id, user=request.user)
#    task.pk = None
#    task.uuid = uuid4()
#    task.save()
#    task.stop()
#    return redirect(TaskList)


# This class does not work properly (does not save). I did not get how does it work.
# Not sure that it filter by user, because, i tryied to put there anything- the same result
# there's no checking of the fact that processs and tasks should be corrleated. you can put every process id on the top.
# FIXME: implement it, for all the cases code is below.
class TaskUpdate(UpdateView):
    pass
#    template_name = 'requester/creation.html'
#    form_class = TaskForm
#    model = Task
#    
#    def get_form(self, form_class):
#        form = UpdateView.get_form(self, form_class)
#        task=get_object_or_404(Task,process_id__exact=self.kwargs['process_id'],id=self.kwargs['pk'])
#        form.fields['input_task'].queryset=Task.objects.filter(user=self.request.user).filter(process_id__exact=self.kwargs['process_id']).filter(~Q(id=self.kwargs['pk']))
#        if task.reward:
#            form.fields['reward_type'].initial=task.reward.type
#            form.fields['reward_quantity'].initial=task.reward.quantity
#        return form
#    
#    
# #    def form_valid(self, form):
# #        return UpdateView.form_valid(self, form)
#    def form_valid(self, form):
#        task = form.save()
# #        log.debug("reward %s",form['reward'])
#        rew = task.reward
#        rew.type =form['reward_type'].value()
#        rew.quantity=form['reward_quantity'].value()
#        rew.save()
#        return HttpResponseRedirect(self.get_success_url())
#      
#    def get_initial(self):
#        initial = {}
#        initial['user']=self.request.user
#        return initial
#    
#    def get_queryset(self):
#        qs = super(TaskUpdate, self).get_queryset()
#        return qs.filter(user=self.request.user)
#   
#    def get_success_url(self):
#        log.debug("process id %s "%self.kwargs['process_id'])
#        return reverse_lazy('r-task-list',args=(int(self.kwargs['process_id']),))
    
# @login_required
# def TaskUpdate(request, task_id):
#    task = get_object_or_404(Task, pk=task_id, user=request.user)
#    form = TaskForm(request.POST or None, instance=task, user=request.user)
#    if request.method == 'POST':
#        if form.is_valid():
#            form.save()
#            return redirect(TaskList)
#    return render_to_response('requester/task.html', {'form':form}, context_instance=RequestContext(request))


@login_required
def TaskDelete(request, task_id, process_id):
    pass
    # this actually set the status to delete
#    template = get_object_or_404(Template,pk=template_id,user=request.user)    
#    task=get_object_or_404(Task,pk=task_id, template=template)
#    task.delete()
    task = get_object_or_404(Task, pk=task_id, owner=request.user)
    task.delete()
    # redirect to the view, don't put logic if it's already implemented

    return redirect(reverse('r-task-list', kwargs={'process_id': process_id}))


@login_required
def ProcessStart(request, process_id):
    pass

@login_required
def ProcessStop(request, process_id):
    process = get_object_or_404(Process, pk=process_id, owner=request.user)
    if request.method == 'POST':
        # start and stop
        # log.critical('startTask has to be fixed')
        forceProcessFinish(process)
        # redirect to the view, don't put logic if it's already implemented
        return redirect(reverse('r-process'))
    else:
        
        return render_to_response('requester/confirm.html', {'process':process}, context_instance=RequestContext(request))

#    #start and stop
#    process = get_object_or_404(Process, pk=process_id, user=request.user)
#    if process.is_inprocess:
#        stopProcess(process)
#    else:
#        if process.is_stopped:
#            startProcess(process)
# #            startTask(task)
#    #redirect to the view, don't put logic if it's already implemented
#    return redirect(reverse('r-task-list',kwargs={'process_id': process_id}))


@login_required
def TaskStop(request, task_id, process_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        # start and stop
        # log.critical('startTask has to be fixed')
        forceFinish(task)
        # redirect to the view, don't put logic if it's already implemented
        return redirect(reverse('r-task-list', kwargs={'process_id': process_id}))
    else:
        
        return render_to_response('requester/confirm.html', {'task':task}, context_instance=RequestContext(request))
        
@login_required
def TaskStartStop(request, task_id, process_id):

    log.warn("don't use me, i'm here just for testing")
    # start and stop
    task = get_object_or_404(Task, pk=task_id)
    # log.critical('startTask has to be fixed')
    startTask(task)
    # redirect to the view, don't put logic if it's already implemented
    return redirect(reverse('r-task-list', kwargs={'process_id': process_id}))

@login_required
def TaskFinish(request, task_id, process_id):
    
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if task.is_inprocess:
        task.finish()
#        triggerTasks(task.process)
    return redirect(reverse('r-task-list', kwargs={'process_id': process_id}))


class TaskInstanceList(ListView):
    paginate_by = 10
    template_name = 'requester/taskinstance_list.html'
    
    def get_queryset(self):
        task = get_object_or_404(Task, pk=self.kwargs['task_id'], owner=self.request.user)
        tl = task.taskinstance_set.all()
        checkIfProcessFinished(task.process)

        return tl
    
    def get_context_data(self, **kwargs):
        contex_data = ListView.get_context_data(self, **kwargs)
        task = get_object_or_404(Task, pk=self.kwargs['task_id'], owner=self.request.user)
        contex_data['task'] = task
#        if task.process.title.startswith("[V]"):
#            id_process = task.process.title.lstrip("[V] Validation for ")
#            process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
#
#            contex_data['process'] = task
#        else:
        process = get_object_or_404(Process, pk=self.kwargs['process_id'], owner=self.request.user)
        contex_data['process'] = process
        return contex_data
#        task_list = Task.objects.filter(owner=self.request.user,process=process).order_by('date_deadline')
#        FIXME
#        task_list = sorted(task_list, key=lambda a: a.int_status)
#        for task in task_list:
#            checkIfFinished(task)
#        return task_list
# def TaskInstanceList(request, process_id, task_id):
#    #first check if user has the ownership
#    task = get_object_or_404(Task, pk=task_id, owner=request.user)
#    taskinstance_list = task.taskinstance_set.all()
#    process = task.process
#    return render_to_response('requester/taskinstance_list.html', {'process':process, 'taskinstance_list':taskinstance_list}, context_instance=RequestContext(request))
@login_required
def uploadProcess(request):
    ''' deploy the process and starts it '''  
    user = request.user
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            username = settings.ACTIVITI_USERNAME
            password = settings.ACTIVITI_PASSWORD

#            edit the id of the process, so it's almos unique.
#            file_uploaded = request.FILES['file']
            main_file = ""
            obj_uploaded = request.FILES['file']
            
#            data = request.FILES['file'] # or self.files['image'] in your form

            path = default_storage.save(str(uuid4()) + '.zip', ContentFile(obj_uploaded.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            log.debug("file %s", tmp_file)
            if zipfile.is_zipfile(tmp_file):
                zf = zipfile.ZipFile(tmp_file)
                for member in zf.namelist():
                    log.debug("deploying %s", member)
                    bpmn_file = zf.read(member)
                    
                    files = {'file': (member, bpmn_file)}
                    url = settings.ACTIVITI_URL + "/repository/deployments"

                    response = requests.post(url, files=files, auth=HTTPBasicAuth(username, password))
                        
                    log.debug("deploy process response %s", response.status_code)
                    if response.status_code == 500:
                        log.debug("it is a 500")
                        raise Http404
                    log.debug(response.text)
              
#                        User.objects.get(username="crowdcomputer")
#                        log.debug("user %s",cc.username)
                    app = Application.objects.get(name="bpmn")
                    cc = app.user
                    log.debug("app %s %s", app.name, cc)
#                        if c:
#                            app.token = str(uuid4()).replace('-', '')
#                            app.save()
#                        root = etree.fromstring(bpmn_file)
#                        processes = root.findall('{http://www.omg.org/spec/BPMN/20100524/MODEL}process')  
                    if member.startswith("sid-main"):
                        main_file = member[0:member.index('.')]
                        log.debug("Main %s", main_file)
#                        title = processes[0].attrib['name']
                        title = request.FILES['file']
                        log.debug("title");
                        process = Process(title=title, description="process created with bpmn", owner=user, application=app)
                        process.save()
                        log.debug("done")
            log.debug("delete file ")
            default_storage.delete(tmp_file)

            log.debug("something to start -> %s", main_file)
            data = {}
            data['processDefinitionKey'] = str(main_file)
#            data['processId'] = str(process.pk)
#            data['app_token'] = app.token
#            token, created = Token.objects.get_or_create(user=request.user)
#            data['user_token'] = token.key
            variables = []
            variables.append(createObject('processId', str(process.pk)))
            variables.append(createObject('app_token', app.token))
            token, created = Token.objects.get_or_create(user=request.user)
            variables.append(createObject('user_token', token.key))
            data['variables'] = variables
            dumps = json.dumps(data)
            log.debug("dumps data %s", dumps)
    
            startProcess(process, main_file, data)

            return HttpResponseRedirect(reverse_lazy('r-task-list', args=[process.pk]))
    else:
#        check if user exists         
        form = None
        if not user.groups.filter(name='bpmn').exists():
            messages.error(request, "You don't have the rights to use this feature. Please write to stefano@crowdcomputer.org if you need it.")
        else: 
            form = UploadFileForm()
    return render_to_response('requester/creation.html', {'form': form}, context_instance=RequestContext(request))

   
    #            root = etree.fromstring(read_file)
#            processes = root.findall('{http://www.omg.org/spec/BPMN/20100524/MODEL}process')  
# #              change the id to be unique, if we create user then this is not needed.
#            id_process = "sid-" + str(uuid4())
#            log.debug("process id %s", processes[0].attrib['id'])
#            processes[0].attrib['id'] = id_process
#            process_name = processes[0].attrib['id']
# #            process[0].attrib['name'] = id_process
#            log.debug("process id %s", processes[0].attrib['id'])
#            process = processes[0]
#            
# #            add receive tasks to all the processes
#            tasks = root.xpath(".//omg:serviceTask[starts-with(@activiti:extensionId,'org.crowdcomputer.ui.task')]",namespaces={"omg":"http://www.omg.org/spec/BPMN/20100524/MODEL","activiti":"http://activiti.org/bpmn"}) 
# #            sequence_flows_all = root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow')  
# #            random number to not overwrite existing one. hope there are no more than 100000 flows
#            tot = 10000
#            log.debug("tasks %s " % tasks)
#            for task in tasks:
# #        add a receive task for every crowdtask
#                log.debug("task attrib id %s",task.attrib['id'])
#                process.append(receiveTask(task.attrib['id']))
#               
# #            modify the sequence
#                sequence_flow_task = root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow[@sourceRef="' + task.attrib['id'] + '"]')
#                for sequence in sequence_flow_task:
#                    process.append(fixSF(sequence, task.attrib['id'] + "-receive", tot))
#                    tot = tot + 1
#  
#            
#            bpmn_file = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + etree.tostring(root)
#            log.debug("bpmn \n"+bpmn_file+"\n")
#            log.debug("file_upload prima read %s",read_file)
#            files = {'bpmn-file': bpmn_file}
#            log.debug("url to post " + url)
#            fixer_response = requests.post('http://localhost:8080/crocoactivitidiagram/',data=files)
#            log.debug("response " + fixer_response.text)
#            files = {'file': (str(id_process+".bpmn"), fixer_response.text)}
            
            
#            start process

@login_required
def exportcsv(request, process_id, task_id):
    response = HttpResponse(content_type='text/csv')
    task = get_object_or_404(Task, pk=task_id)
    process = get_object_or_404(Process, pk=process_id, owner=request.user)
    response['Content-Disposition'] = 'attachment; filename="' + task.title + '.csv"'

    writer = csv.writer(response)
    allinstances = task.taskinstance_set.all()
    if len(allinstances) > 0:
        firstinstance=None
        i=0
        while (firstinstance is None or firstinstance.executor is None):
            firstinstance = allinstances[i]
            log.debug("%s %s",firstinstance,i)
            i=i+1;
            if i > len(allinstances):
                return response 
        firstrow = ['user']
        if firstinstance.input_data:
            log.debug("fi input %s", firstinstance.input_data.value)
            for obj in firstinstance.input_data.value:
                for key in obj.keys():
                    firstrow.append("input-" + key)
        if firstinstance.output_data:
            log.debug("fi output %s", firstinstance.output_data.value)
            for key in firstinstance.output_data.value.keys():
                firstrow.append("output-" + key)
        if firstinstance.parameters:
            log.debug("fi pars %s", firstinstance.parameters)
            for key in firstinstance.parameters.keys():
                firstrow.append("parameters-" + key)
        writer.writerow(firstrow)
        int
        for instance in allinstances:
            row = []
            if instance.executor:
                if 'validation' in instance.parameters and instance.parameters['validation']:
                    row.append(instance.executor.username)
                    if instance.input_data:
                        for obj in instance.input_data.value:
                            log.debug("all in %s", obj)
                            for value in obj.values():
                                log.debug("input %s", value)
                                row.append("" + str(value))
                    if  instance.output_data:
                        for value in instance.output_data.value.values():
                            log.debug("output %s", value)
                            row.append("" + str(value))
                    if instance.parameters:
                        for value in instance.parameters.values():
                            log.debug("pars %s", value)
                            row.append("" + str(value))
                    writer.writerow(row)
            
    return response
