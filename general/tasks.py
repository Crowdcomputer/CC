'''
Created on Jun 27, 2013

@author: stefanotranquillini
'''

import logging
import json

from celery import task
from django.core.mail.message import EmailMultiAlternatives
import requests
from requests.auth import HTTPBasicAuth

from crowdcomputer import settings


log = logging.getLogger(__name__)


def createObject(name, value):
    ret = {}
    ret['name'] = name
    ret['value'] = value
    return ret


@task()
def sendEmail(sender, title, html, email):
    html += "<br/> <a href=\"" + settings.CM_Location + "\">Crowd Computer</a>"
    # msg = EmailMultiAlternatives(title, html,sender + ' (CrowdComputer)', [], [email])
    # msg.attach_alternative(html, "text/html")
    log.debug("Mail %s %s %s %s" % (str(sender), title, html, email))
    #msg.send()

    msg = EmailMultiAlternatives(
        subject=title,
        body=html,
        from_email=sender,  # + ' (CrowdComputer)',
        to=[email]
    )
    msg.attach_alternative(html, "text/html")
    # Send it:
    msg.send()


# #FIXME: duplicated method, it's the only way i found.
# def getResults(task):
#    ret=[]
#    for instance in task.taskinstance_set.all():
#        if hasattr(instance, 'output_data'):
#            value = instance.output_data.value
#            if isinstance(value, list):
#                log.debug('list: %s', value)
#                for v in value:
#                    ret.append(v)
#    #        if not append the element
#            else:
#                log.debug('element [%s}: %s' % (type(value), value))
#                ret.append(value)
#    return ret
#
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

#
# @task()
# def triggerPick(task, workerId):
#     #    if task.status=='FN':
#     #        return
#     username = settings.ACTIVITI_USERNAME
#     password = settings.ACTIVITI_PASSWORD
#     #http://localhost:8080/activiti-rest/service/process-instance/149/signal
#     url = settings.ACTIVITI_URL + "/process-instance/" + task.process.processactiviti.instanceID + "/signal"
#     data = {}
#     data['activityId'] = task.taskactiviti.receive + "-receive"
#     name = task.parameters["data_name"]
#     # data[name] = json.dumps(results)
#     dumps = json.dumps(data)
#     log.debug("dumps data %s", dumps)
#     response = requests.post(url, data=dumps, auth=HTTPBasicAuth(username, password))
#     log.debug(response.text)


@task()
def triggerReceiver(task, results):
    #    if task.status=='FN':
    #        return
    task.parameters['result'] = results
    task.save()
    log.info("ok here we go")
    # log.debug("receive  " + task.taskactiviti.receive)
    username = settings.ACTIVITI_USERNAME
    password = settings.ACTIVITI_PASSWORD
    #http://localhost:8080/activiti-rest/service/process-instance/149/signal
    url = settings.ACTIVITI_URL + "/runtime/executions/" + task.process.processactiviti.instanceID
    data = {}
    # data['activityId'] = task.taskactiviti.receive + "-receive"
    data['action'] = 'signal'
    variables = []
    variables.append(createObject(task.parameters["data_name"], results))
    data['variables'] = variables
    dumps = json.dumps(data)
    log.debug("dumps data %s", dumps)
    response = requests.put(url, data=dumps, auth=HTTPBasicAuth(username, password))
    log.debug(response.text)


@task()
# fimd rhe process id
def triggerReceiverInstance(taskinstance):
    #    if task.status=='FN':
    #        return
    username = settings.ACTIVITI_USERNAME
    password = settings.ACTIVITI_PASSWORD
    #http://localhost:8080/activiti-rest/service/process-instance/149/signal
    url = settings.ACTIVITI_URL + "/runtime/executions/" + taskinstance.parameters['process_tactics_id']
    data = {}
    # data['activityId'] = task.parameters['receiver']

    data['action'] = 'signal'
    variables = []
    variables.append(createObject(taskinstance.task.parameters["data_name"], taskinstance.output_data.value))
    variables.append(createObject("taskId", taskinstance.task.id))
    variables.append(createObject("taskInstanceId", taskinstance.id))

    data['variables'] = variables
    dumps = json.dumps(data)
    log.debug("%s %s" % (url, dumps))
    response = requests.put(url, data=dumps, auth=HTTPBasicAuth(username, password))
    log.debug(response.text)


@task()
def signal(id_process, task_id, taskinstance_id):
    '''
    generic signal of procesese
    :param id_process:
    :return:

    '''
    username = settings.ACTIVITI_USERNAME
    password = settings.ACTIVITI_PASSWORD
    url = settings.ACTIVITI_URL + "/runtime/executions/" + str(id_process)

    datapick = {}
    datapick['action'] = 'signal'
    variables = []
    variables.append(createObject("taskId", task_id))
    variables.append(createObject("taskInstanceId", taskinstance_id))

    datapick['variables'] = variables
    dumps = json.dumps(datapick)
    log.debug("signaling %s %s" % (url, dumps));
    response_signal = requests.put(url, data=dumps, auth=HTTPBasicAuth(username, password))
    try:
        resp_j = response_signal.json()
    except:
        return 0
    log.debug("signal response %s", resp_j)
    if "statusCode" in resp_j:
        log.error("error %s", resp_j)
    return 0


# @task()
# def deleteInstance(process):
# #    if task.status=='FN':
# #        return
#     username="kermit"
#     password="kermit"
# #http://localhost:8080/activiti-rest/service/process-instance/149/signal
#     url = settings.ACTIVITI_URL + "/process-instance/runtime/process-instances/"+process.processactiviti.instanceID
#     response = requests.delete(url,auth=HTTPBasicAuth(username, password))
#     log.debug(response.text)

@task()
def queryProcessForPick(task, user, ):
    # FIXME: critical, this takes the first, there's no atomicti.
    username = settings.ACTIVITI_USERNAME
    password = settings.ACTIVITI_PASSWORD
    #http://localhost:8080/activiti-rest/service/process-instance/149/signal
    url = settings.ACTIVITI_URL + "/query/executions"
    data = {}
    log.debug(task.parameters)
    data['processDefinitionId'] = task.parameters['process_instance_id']
    data['activityId'] = task.parameters['receivers'] + "-pick"
    dumps = json.dumps(data)
    log.debug("dumps data %s", dumps)
    response = requests.post(url, data=dumps, auth=HTTPBasicAuth(username, password))
    responsedata = response.json()['data']
    # if two users joins at the same time we are screwed
    if len(responsedata) > 0:
        url = settings.ACTIVITI_URL + "/runtime/executions/" + str(responsedata[0]['id'])

        datapick = {}
        datapick['action'] = 'signal'
        variables = []
        variables.append(createObject("executor_id", user.pk))
        variables.append(createObject("data", "[]"))
        datapick['variables'] = variables
        # variables.append()
        # datapick[] = task.parameters['receivers'] + "-pick"
        dumps = json.dumps(datapick)
        log.debug("signaling %s %s" % (url, datapick));

        response_signal = requests.put(url, data=dumps, auth=HTTPBasicAuth(username, password))
        resp_j = response_signal.json()
        log.debug("signaling  response %s", resp_j)
        if "statusCode" in resp_j:
            # one option is too recall this function.. but there may be aloop problem..
            log.error("error %s", resp_j)
            return False
        return True
    return False



    #   get the first pick task instance and signal it