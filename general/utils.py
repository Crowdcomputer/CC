# from general.models import TaskInstance, Data
from timeit import itertools
from uuid import uuid4
from django.db import transaction
import logging
from general.models import Data, TaskInstance, ProcessActiviti, UserProfile
import crowdcomputer
from general.mturk import mTurk
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.timezone import is_aware
from django.core.urlresolvers import reverse
from decimal import Decimal
from crowdcomputer import settings
import requests
from requests.auth import HTTPBasicAuth
import json
from general.tasks import triggerReceiver

from lxml import etree


log = logging.getLogger(__name__)

def getResults(task):
    ret = []
    
    
    for instance in task.taskinstance_set.all():
#        if task.humantask.platform=='MT':
#            assignmentId=instance.parameters.get('assignmentId',None)
#            workerId=instance.parameters.get('workerId',None)
#            log.debug("retrive Hit Results for ")
#            mt = mTurk(crowdcomputer.settings.AMZ_PRIVATE, crowdcomputer.settings.AMZ_SECRET)
#            value = mt.getDataFromHit(assignmentId, workerId)
#            instance.output_data.value = value
#            instance.save()
#            ret.append(value)
        if hasattr(instance, 'output_data'):
            if instance.output_data:
                if 'validation' in instance.parameters and instance.parameters['validation']:
                    log.debug("valid")
                    value = instance.output_data.value
                    ret.append(value)
                else:
                    log.debug("data of %s: [%s,%s] is not valid",instance.executor, instance.output_data,instance.parameters)
#            if isinstance(value, list):
#                log.debug('list: %s', value)
#                for v in value:
#                    ret.append(v)
#    #        if not append the element
#            else:
#                log.debug('element [%s}: %s' % (type(value), value))
#                ret.append(value)
    log.debug("results: %s", ret)
    log.debug("merge %s", task.parameters['merge'])
    if task.parameters['merge'] is not None and task.parameters['merge'] == False:
        return mergeData(ret)
    else:
        return ret

'''conversion rates'''
CONVERSION = (('CCM', 1.0), ('USD', 1.16), ('EUR', 0.9), ('COF', 2.0))

def convertReward(from_type, to_type, r_quantity):
    for k, v in CONVERSION:
        if k == from_type: 
            from_value = float(v)
        if k == to_type:
            to_value = float(v)
    if from_value is None or to_value is None:
        return Exception('Reward type does not exists')
    conversion = (float(r_quantity) / from_value) * to_value
    log.debug(conversion)
    return Decimal(str(conversion))
    





#    TODO: write test cases for  functions.

def __combinations(l, n):
    return list(itertools.combinations(l, n))

# first n-m and last m elements are overlapped
def __splitNM(l, n, m):
    ret = []
    ret.append(l[0:n])
    for i in range(n, len(l), n - m):
        left = i - m if i - m > 0 else 0 
        right = i + (n - m) if i + (n - m) < len(l) else len(l)
        ret.append(l[left:right])
    return ret
   
def __splitN(l, n):
    return __splitNM(l, n, 0) 

def splitData(data, operation, n=0, m=0):
    '''
        takes a list and creates list of lists
        combination
        set of N
        set of N and M
    '''
    if operation.lower() == 'combination'.lower():
        return __combinations(data, n)
    elif operation.lower() == 'splitN'.lower():
        return __splitN(data, n)
    elif operation.lower() == 'splitNM'.lower():
        return __splitNM(data, n, m)

def mergeData(data):
    '''
        takes a list (data) of list and returns an array
        t1=[{'id':..,'a1':..},{'id':..,'a1':..},{'id':..,'a1':..}] 
        t2=[{'id':..,'b1':..,'b2':..},{'id':..,'b1':..,'b2':..},{'id':..,'b1':..,'b2':..}]
        res=#[{'id':..,'a1':..},{'id':..,'a1':..},{'id':..,'a1':..},{'id':..,'b1':..,'b2':..},{'id':..,'b1':..,'b2':..},{'id':..,'b1':..,'b2':..}]

    '''
    ret = []
    for d in data:
        value = d
#        if list then concat element
        if isinstance(value, list):
            ret = ret + value
#        if not append the element
        else:
            ret.append(value)      
    return ret 

def __condition(o_value, operator, value):
    if operator == '==':
        return (o_value == value)
    elif operator == '!=':
        return (o_value != value)
    elif operator == '<':
        return (o_value < value)
    elif operator == '>':
        return (o_value > value)
    else: 
        return False

def __satisfy(obj, condition):
    field = str(condition['field'])
    operator = str(condition['operator'])
    value = str(condition['value'])
    if obj:
        log.debug("condition %s %s %s %s" % (obj[field], operator, value, __condition(str(obj[field]), operator, value)))
        if __condition(str(obj[field]), operator, value):
            return obj
        else:
            return None
    return None

def filterData(objects, conditions, condition_operator='and'):
    '''
        takes a list and a condition, return a sublist
        condition is list of dic containing:
        - field
        - operator
        - value
    '''
    listret = []
    for obj in objects:
        obj_t_l = []
        for condition in conditions:
            obj_t = __satisfy(obj, condition)
            if condition_operator == 'and':
                obj = obj_t
            else:
                if obj_t is not None:
                    obj_t_l.append(obj)
        if condition_operator == 'and' and obj:
            listret.append(obj)           
        elif len(obj_t_l) > 0:
            obj = obj_t_l[0]
            listret.append(obj)
    ret = {}
    ret['result'] = listret
    return ret
    

def splitObjects(objects, shared, fields):
    '''
        takes a list of objects and split in two lists.
        shared are the fields shared by both objects
        fields are the fields of the first object.
        remaining fields are for the second object.
    '''
    list1 = []
    list2 = []
    for obj in objects:
        item1 = {}
        item2 = {}
        for key, value in obj.iteritems():
            log.debug('key %s', key)
            if key in shared:
                log.debug('shared')
                item1[key] = value
                item2[key] = value
            elif key in fields:
                log.debug('fields')
                item1[key] = value
            else:
                log.debug('rest')
                item2[key] = value
        list1.append(item1)
        list2.append(item2)
    ret = []
    ret.append(list1)
    ret.append(list2)
    return ret

def joinObjects(objects, field):
    '''
        takes a list of objects and merge them.
        objects are dicts
        if objects have same keys, values are joined into a list.
        [{'id':1,'tag':'ciao1'},
        {'id':2,'tag':['ciao1',ciao3]},
        {'id':1,'smt':'else2'},
        {'id':2,'tag':'ciao2'}] 
        becomes
        [{'id': 1,'smt': 'else2', 'tag': 'ciao1'}, {'id': 2,'tag': ['ciao2', 'ciao1','ciao3']}]
    '''
    res = {}
#    defaultdict(dict)
    for obj in objects:
#        find the index
        idx = obj[field]
#        find the object
        if idx in res:
            t_obj = res[idx]
        else:
            t_obj = {}
            
        for k, v in obj.iteritems():
#            if key is the field don't do anything
            if k != field:
                if k in t_obj:
#                    if it's a list then append it, so we avoid list into lists
                    if isinstance(t_obj[k], list):
                        t_obj[k].append(v)
                    else:
                        t_obj[k] = [v] + t_obj[k]
                else:
                    if isinstance(v, list):
                        t_obj[k] = v
                    else:
                        t_obj[k] = [v]
            else:
                t_obj[k] = v  
#            store in the map
        res[idx] = t_obj
    r = []
#    for all the elements in the list (which are dict)
    for k, v in res.iteritems():
        obj = {}
#        take all the fields of an element
        for k1, v1 in v.iteritems():
            if isinstance(v1, list):
                if len(v1) == 1:
                    obj[k1] = v1[0]
                else:
                    obj[k1] = v1
            else:
                obj[k1] = v1
        r.append(obj)
    return r

    
#    #FIXME: this has to be checked
#    def mergeResults(self,task):
#        instances = task.taskinstance_set.all().exclude(output=None)
#        ret = []
#        for instance in instances:
#            value = instance.output.value
#    #        if list then concat element
#            if isinstance(value, list):
#                log.debug('list: %s', value)
#                for v in value:
#                    ret.append(v)
#    #        if not append the element
#            else:
#                log.debug('element [%s}: %s' % (type(value), value))
#                ret.append(value)
#        return ret
        
   
    # FIXME: this has to be checked
    
#    def joinTasks(self,field, lst):
#        res = defaultdict(dict)
#        for task in lst:
#    #        for instance in task:
#    ##            this works on dictionaries
#    #            objs = 
#            for obj in task:
#    #           searach in the map the object with the same 'field' value
#                idx = obj[field]
#                t_obj = res[idx]
#    #            update it with the object in the list
#                t_obj.update(obj)
#    #            store in the map
#                res[idx] = t_obj
#        r = []
#    #    create a list of values
#        for k, v in res.iteritems():
#            r.append(v)
#        return r
    
    # can be useful. it creates huge amount of data!
   
#    
#    def manageMerging(self,task):
#        dt = None
#        if (task.input_task.count() > 1):
#            log.debug("more than one input")
#        #            if more than one task, create a list of input task merged reults and join them
#            datas = []
#            for input_task in task.input_task.all():
#        #                    input_task is a list
#        #                    merge results give a list with lists inside?
#                datas.append(mergeResults(input_task))
#                log.debug("mergred results %s" % datas)
#            dt = joinTasks(task.input_task_field, datas)
#            log.debug("joined results %s" % datas)
#        else:
#            log.debug("one input")
#    #            take the first
#            dt = (mergeResults(task.input_task.all()[0]))
#        return dt

# end of data


def createInstance(task, data):
    taskinstance = TaskInstance(task=task,
                               status='ST',
                               uuid=uuid4())
    if data:
        taskinstance.input_data = data
    taskinstance.save()
    return taskinstance
    
@transaction.commit_on_success
def startTask(task, data=[]):
    '''
        takes a data list and a task
        create the isntances.
        transactions saves only when all is ok.
    '''
    log.debug("data %s",data)
    data=json.loads(data)
#   for all the objects in the list create a data object
    for i in range(0, task.humantask.number_of_instances):
#        if data has elements
        log.debug("lenght of data is %s",len(data))
        if len(data) > 0:
#            if data is a list of list, then do it
            if isinstance(data[0], list):
                log.debug("data is a list")
                for d in data:
                    dd = Data(value=d)
                    dd.save()
                    log.debug(' %s instance (%s) with data %s ' % (task.title, i, dd.value))
                    createInstance(task, dd)

            else:
                log.debug("data is not a list, it is a %s",type(data))
                dd = Data(value=data)
                dd.save()
                log.debug(' %s instance (%s) with data %s ' % (task.title, i, dd.value))
                createInstance(task, dd)
        else:
            
            log.debug(' %s instance (%s) without data ' % (task.title, i))
            createInstance(task, None)  
    task.status = 'PR'
    task.save()
    log.debug("MT = %s " % task.humantask.platform)
    if (task.humantask.platform == "MT"):
        mturkTask(task)
    return True

def mturkTask(task):
    mt = mTurk(crowdcomputer.settings.AMZ_PRIVATE, crowdcomputer.settings.AMZ_SECRET)
    now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
    log.debug("%s %s" % (is_aware(task.date_deadline), is_aware(now)))
    duration = (task.date_deadline - now)
    log.debug("seconds between date %s " % duration.seconds)
#    reward = convertReward(task.humantask.reward.type, 'USD', task.humantask.reward.quantity)
    reward = task.humantask.reward.quantity
    log.debug("converted reward %s", reward)
    typeId=''
    for instance in task.humantask.taskinstance_set.all():
        url = crowdcomputer.settings.CM_Location + reverse('mt-execute-instance', args=[instance.uuid])
        log.debug(url)
        r = mt.createExternalQuestion("[" + task.owner.username + "] " + task.title, task.description, "CrowdComputer.org", url, duration.seconds, reward)
        pars = {}
        pars['HITId'] = r.HITId
        pars['HITTypeId'] = r.HITTypeId
        log.debug("typeId %s",typeId)
        if typeId=='':
            typeId=r.HITTypeId
        if typeId!=r.HITTypeId:
            typeId=None
        log.debug("typeId %s vs %s",typeId,r.HITTypeId)
        instance.parameters = pars
        instance.save()
    if typeId:
        task.parameters['HITTypeId']=typeId
        task.save()

def forceProcessFinish(process):
    if process.is_finished:
        return
    process.status = 'FN'
    process.save()
    for task in process.task_set.all():
        log.debug("finishing : %s",task.pk)
        forceFinish(task)
    

def forceFinish(task):
    l=[]
    if task.is_finished:
        return
    
    
    for instance in task.taskinstance_set.all():
        if instance.status !='FN':
            instance.status = 'ST'
            instance.save()
            log.debug("finishing instance: %s",instance.pk)
            if instance.validation:
                l.append(instance.validation)
                
    rewardUsers(task)
    if settings.CELERY:
        triggerReceiver.delay(task, getResults(task))
    else:
        triggerReceiver(task,getResults(task))
    task.status = 'FN'
    task.save()
    for i in l:
        forceProcessFinish(i)

    
def stopTask(task):
    task.status = 'ST'
    task.save()
    for instance in task.taskinstance_set.all():
        instance.status = 'ST'
        instance.save()
 

 
   

         

# #FIXME: this has to be rewrite (add data to this function)
# def startTask(task):
#    if task.humantask:
#        if task.humantask.taskinstance_set.count() < task.humantask.number_of_instances:
#            for i in range(task.humantask.number_of_instances):
#                        taskintance = TaskInstance(task=task,
#                                                   status='ST',
#                                                   #input=data,
#                                                   uuid=uuid4())
#                        taskintance.save()   
#        task.status = 'PR'
#        task.save()
#    else:
#    #if task.machinetask:
#        #TODO we need smth here
#        return False
#
# def stop_expired(list_tasks):
#    print 'misc.stop_expired must be implemented'
#    return
# #    for task in list_tasks:
# #        if task.is_expired:
# #            task.finish()
#
#    
#    
# '''
# def startTask(task):
#    log.debug("startTask for %s" % task.title)
# #    this checks if has already instances
#
# #    check if it's a human task then:
#    if task.humantask:
#        if (task.taskinstance_set.count() == 0):
#            dt = []
#    #        if no input, create the instance
#            if task.input_task.count() == 0:
#                log.debug("no input")
#                for i in range(task.instances_required):
#                        taskintance = TaskInstance(task=task,
#                                                   status='ST',
#                                                   uuid=uuid4())
#                        log.debug("instace %s created" % i)
#                        taskintance.save()   
#            else:
# #                merge the results
#                dt = manageMerging(task)
#    #            this can be improved, it does a switch on the splitting method
#    #            if no split do not do anythig
#                if task.split == general.models.NO_SPLIT:
#                    data = Data(value=dt)
#                    data.save()
#                    for i in range(task.instances_required):
#                        log.debug(' %s instance (%s) with data %s ' % (task.title, i, dt))
#                        taskintance = TaskInstance(task=task,
#                                                   status='ST',
#                                                   input=data,
#                                                   uuid=uuid4())
#                        taskintance.save()   
#                else:
#                    splitted = None
#                    if task.split == general.models.COMBINATION:
#                        splitted = combinations(dt, task.split_field_N)
#                    if task.split == general.models.SET_NM:
#                        splitted = splitNM(dt, task.split_field_N, task.split_field_M)
#                    if task.split == general.models.SET_N:
#                        splitted = splitN(dt, task.split_field_N)
#        #            for all the splitted data    
#                    for sd in splitted:
#                        data = Data(value=sd)
#                        data.save()
#            #            for all the required amount of instances
#                        for i in range(task.instances_required):
#                            log.debug(' %s instance (%s) with data %s ' % (task.title, i, sd))
#                            taskintance = TaskInstance(task=task,
#                                                       status='ST',
#                                                       input=data,
#                                                       uuid=uuid4())
#                            taskintance.save()   
#    #        save the task  
#        task.status = 'PR'
#        task.save()
#        log.debug("task [%s] %s status = %s" % (task.pk, task.title, task.status))
# #    it's a machine task
#    else:
#        log.debug("task is machine")
#        dt = manageMerging(task)
#        log.warn("do we need json encoding?")
#        data = {}
#        data['data'] = json.dumps(dt)
#        r = requests.post(task.input_url, data)
#        log.debug("return code %s", r.status_code)
#        log.debug("return data %s", r.text)
#        dataIn = Data(value=dt)
#        dataIn.save()
# #        TODO: fix it here
# #        dataOut= Data(value=r.json)
# #        dataOut.save()
#        taskintance = TaskInstance(task=task,
#                                   status='FN',
#                                   input=dataIn,
# #                                   output=dataOut,
#                                   uuid=uuid4())
#        taskintance.save()
#        task.status = 'FN'
#        task.save()
#        log.debug("trigger task goes here?")
#        triggerTasks(task.process)
# #        send data
# '''
# #FIXME: this has to be checked
# def stopTask(task):
#    task.status = 'ST'
#    task.save()
#    for instance in task.taskinstance_set.all():
#        instance.status = 'ST'
#        instance.save()
#
# #FIXME: this has to be checked
#      
# #Start process, start all tasks withoud input in this proces, start all tasks, which have all input tasks finished 
# def startProcess(process):    
#    process.status = 'PR'
#    process.save()
#    triggerTasks(process)    
#    
# #FIXME: this has to be checked
#
# def stopProcess(process):     
#    process.status = 'ST'
#    process.save()
#    triggerTasks(process)
#
# #FIXME: this has to be checked
#
# #this function basically create the TaskInstance
# def triggerTask(task):
#    startTask(task)
#    stopTask(task)
#
# #FIXME: this has to be rewrite
# def triggerTasks(process):
#    #Take all tasks which are not deleted
#    for task in process.task_set.exclude(status="DL"):
#        #Finish task if it is in process now and (it is expired or has enough instances finished)
#        if (task.is_expired or (task.taskinstance_set.all().count() > 0 and task.instances_given == task.taskinstance_set.all().count())):
#            task.finish()
#            log.debug('Task %s -> %s' % (task.title, task.status))
#        #If process is stopped, we should stop all "inprocess tasks"
#        if process.is_stopped and task.is_inprocess:
#            task.stop()
#            log.debug('Task %s -> %s' % (task.title, task.status))
#
#        # if process is inporcess we should start stopped tasks, which does not have input_task or have all input tasks finished 
#        elif process.is_inprocess:
#            log.debug("Task %s has all the input finished?  %s" % (task.title, (task.input_task.filter(status="FN").count() == task.input_task.count())))
#            if (task.is_stopped and (not (task.input_is_task) or (task.input_task.filter(status="FN").count() == task.input_task.count()))):
#                log.debug('start task')
#                startTask(task)  
#
#        
            
    


#
# def sendEmail(sender, title, html, email):
#    start = int(round(time.time() * 1000))
#    html += "<br/> <a href=\"" + settings.CM_Location + "\">Crowd Computer</a>"
#    #msg = EmailMultiAlternatives(title, html,sender + ' (CrowdComputer)', [], [email])
#    #msg.attach_alternative(html, "text/html")
#    #log.debug("Mail %s" + str(sender))
#    #msg.send()
#
#    msg = EmailMultiAlternatives(
#    subject=title,
#    body=html,
#    from_email=sender, # + ' (CrowdComputer)',
#    to=[email]
#    )
#    msg.attach_alternative(html, "text/html")
#    # Send it:
#    msg.send()
#    log.debug('time = %s', (int(round(time.time() * 1000)) - start))
#    

        

def copyReqParameter(request):
        query_dict = request.GET.copy()
        for k, v in request.GET.iteritems():
            query_dict[k] = v
        return '?%s' % query_dict.urlencode()
    



def receiveTask(name):
    '''receive_skeleton="<receiveTask id=\"{taskname}-receive\" name=\"Receive Task\"></receiveTask>"'''
    attrib = {}
    attrib['id'] = name + '-receive'
    attrib['name'] = 'Receive Task'
    
    obj = etree.Element("receiveTask", attrib=attrib)
    log.debug("receive task " + str(obj))
    return obj

def fixSF(sequence, name, total):
    ''' <sequenceFlow id="flow2" sourceRef="servicetask1" targetRef="endevent1"></sequenceFlow>'''
#   A->B becomes A->C
    log.debug("sequence is : " + sequence.attrib['sourceRef'] + " " + sequence.attrib['targetRef'])
    temp_target = sequence.attrib['targetRef']
    log.debug("temp_target " + temp_target)
    sequence.attrib['targetRef'] = name
    attrib = {}
    attrib['id'] = "flow" + str(total + 10000)
    attrib['sourceRef'] = name
    attrib['targetRef'] = temp_target
    log.debug(temp_target)
#    create C->B
    obj = etree.Element("sequenceFlow", attrib=attrib)
    log.debug("result is " + obj.attrib['sourceRef'] + " " + obj.attrib['targetRef'])
    return obj

def createObject(name, value):
    ret = {}
    ret['name'] = name
    ret['value'] = value
    return ret

def rewardUser(taskinstance):
#    messages.info(request, 'Sorry, we do not support reward (yet)')
    if taskinstance.executor is None:
        return
    pars = taskinstance.parameters
    log.debug("platform %s",taskinstance.task.humantask.platform)
    if taskinstance.task.humantask.platform=="MT":
        log.debug("reward for turk")
        mt = mTurk(crowdcomputer.settings.AMZ_PRIVATE, crowdcomputer.settings.AMZ_SECRET)

        a_id = pars.get('assignmentId',None)
        w_id = pars.get('workerId',None)
        if a_id is None or w_id is None:
            log.debug("a_id is None or w_id is None: %s ",taskinstance.parameters)
        else:   
            log.debug("a_id is %s or w_id is %s ",a_id,w_id)
            mt.approveAssignemnt(a_id, "good job")
            log.debug("approved %s",a_id)
#        log.warn("Turk rewarding is not implemented")
    pars['reward']=True
    log.debug("pars %s",pars)
    taskinstance.save()
    log.warn("Not implemnted method")
    return

    userp, create = UserProfile.objects.get_or_create(user=taskinstance.executor)
    reward = userp.reward_dollars
    #  this is for the bid
    if taskinstance.parameters['reward'] is not None:
        o_reward = taskinstance.task.humantask.reward
    else:
        o_reward = taskinstance.task.humantask.reward
    n_reward = convertReward(o_reward.type, "USD", o_reward.quantity)
    reward = reward + n_reward
#    request.session['reward'] = n_reward
    userp.reward_dollars = reward
    userp.save()
    
def rejectUser(taskinstance):
    if taskinstance.executor is None:
        return
    log.debug("reject user")
    pars =  taskinstance.parameters
#    messages.info(request, 'Sorry, we do not support reward (yet)')
    if taskinstance.task.humantask.platform=="MT":
        mt = mTurk(crowdcomputer.settings.AMZ_PRIVATE, crowdcomputer.settings.AMZ_SECRET)
        a_id =pars.get('assignmentId',None)
        w_id = pars.get('workerId',None)
        if a_id is None or w_id is None:
            log.debug("a_id is None or w_id is None: %s ",taskinstance.parameters)
        else:                
            log.debug("a_id is %s or w_id is %s ",a_id,w_id)
            mt.rejectAssigment(a_id, "good job")
            log.debug("reject %s",a_id)
#        log.warn("Turk rewarding is not implemented")
    taskinstance.save()

    return

def rewardUsers(task):
    log.debug("rewarding for %s",task.pk)
    ht = task.humantask
    reward = ht.reward
    log.debug("reward strategy %s", reward.strategy)
    if (reward.strategy == "ALL"):
        log.debug("all")
        for ti in task.taskinstance_set.all():
            rewardUser(ti)
    elif (reward.strategy == "NONE"):
        log.debug("none")
        for ti in task.taskinstance_set.all():
            rejectUser(ti)
    elif (reward.strategy == "VALID"):
        log.debug("valid")
        for ti in task.taskinstance_set.all():
            if 'validation' in ti.parameters:
                log.debug("validation result %s", ti.parameters['validation'])
                if ti.parameters['validation']:
                    rewardUser(ti)
                else:
                    rejectUser(ti)
            elif ti.executor:
                    ti.parameters['validation']=True
                    rewardUser(ti)
                    ti.save()
    elif (reward.strategy == "BEST"):
        log.debug("best")

        bests = []
        notbests=[]
        best_v = None
        for ti in task.taskinstance_set.all():
            if 'validation' in ti.parameters:
                log.debug("validation result %s", ti.parameters['validation'])
                e=ti.parameters['validation']
                if best_v is None:
                    best_v=e
                    bests.append(e)
                elif e>best_v:
                    notbests+=bests
                    bests=[]
                    bests.append(e)
                    best_v=e
                elif e==best_v:
                    bests.append(e)
                else:
                    notbests.append(e) 
            elif ti.executor:
                    ti.parameters['validation']=True
                    rewardUser(ti)
                    ti.save()
#                if float(ti.parameters['validation'])>=best_v:
#                    best_v=float(ti.parameters['validation'])
#                    if len(bests)>0:
#                        if bests[0]<best_v:
#                            for old_b in bests:
#                                bests.remove(old_b)
#                                notbests.append(old_b)
#                    bests.append(ti)
#                else:
#                    notbests.append(ti)
                
        for b in bests:
            b.parameters['validation_value']=b.parameters['validation']
            b.parameters['validation']=True
            b.save()
            rewardUser(b)
        for nb in notbests:
            nb.parameters['validation_value']=nb.parameters['validation']
            nb.parameters['validation']=False
            nb.save()
            rejectUser(nb)

def startProcess(process,process_id, data):
#    log.debug("starting  %s" % process_id)
#    log.debug("data %s",json.dumps(data))
#    url = settings.ACTIVITI_URL + "/process-instance"
#    response = requests.post(url, data=json.dumps(data), auth=HTTPBasicAuth(settings.ACTIVITI_USERNAME, settings.ACTIVITI_PASSWORD))
#    log.debug(response.text)
#    jsonresp = response.json()
#    processInstanceId = jsonresp.get("id")
#    processDefinition = jsonresp.get("processDefinitionId")
#    process_activiti = ProcessActiviti(process=process, key=process_id, instanceID=processInstanceId, processDefinition=processDefinition)
#    process_activiti.save()
#    log.debug(response.text)
#    return True
    log.debug("starting  %s" % process_id)
    log.debug("data %s",data)
    url = settings.ACTIVITI_URL + "/runtime/process-instances"
    response = requests.post(url, data=json.dumps(data), auth=HTTPBasicAuth(settings.ACTIVITI_USERNAME, settings.ACTIVITI_PASSWORD))
    log.debug(response.text)
    jsonresp = response.json()
    processInstanceId = jsonresp.get("id")
    processDefinition = jsonresp.get("processDefinitionId")
    process_activiti = ProcessActiviti(process=process, key=process_id, instanceID=processInstanceId, processDefinition=processDefinition)
    process_activiti.save()
    log.debug(response.text)
    process.status="PR"
    process.save()
    return True

def checkIfProcessFinished(process):
    if process.status=='FN':
        return True
    else:
        ret=checkIfProcessFinished2(process)
        if ret:
            process.status='FN'
            process.save()
def checkIfProcessFinished2(process):
    vl=[]
    con=True
    for task in process.task_set.all():
        if task.humantask:
            if task.humantask.validation:
                for ti in task.humantask.taskinstance_set.all():
                    if ti.validation:
                        vl.append(ti.validation)
            con=checkIfFinished(task)
            if not con:
                return False
    for v in vl:
        con= checkIfProcessFinished2(v)
        if not con:
            return False
        else:
            v.status='FN'
            v.save()
    return True
                
def checkIfFinished( task  ):
    log.debug("check if finished %s %s",task.title,task.pk )
 

    if task.humantask is None:
        return True
    if task.is_finished:
        return True
    if task.is_expired:
        task.finish()
        if task.taskactiviti is not None:
            log.debug("expired")
#            TODO: call the rewarding 
            rewardUsers(task)
            results = getResults(task)
            if settings.CELERY:
                triggerReceiver.delay(task, results)
            else:
                triggerReceiver(task, results)

            task.status = 'FN'
            task.save()
            return True
    elif 'type' in task.parameters and task.parameters['type'] in ['marketplace', 'newsletter'] :
#        log.info("type %s",task.parameters['type'])
        n = len(task.humantask.taskinstance_set.filter(status="FN"))
        tot = task.humantask.taskinstance_set.count()
#        tot = task.humantask.number_of_instances
#        if tot == 0:
#            means it's newsletter
            
            
        log.debug("is %s = %s"%(n,tot))
        if n == tot:
            if task.taskactiviti is not None:
                log.debug("completed")
                rewardUsers(task)
                #            TODO: call the rewarding 
                results = getResults(task)
#                result = triggerReceiver(task, results)

                if settings.CELERY:
                    triggerReceiver.delay(task, results)
                else:
                    triggerReceiver(task, results)                
                log.debug("completed2")
                task.status = 'FN'
                task.save()
                return True
    return False
    

    
