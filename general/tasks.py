'''
Created on Jun 27, 2013

@author: stefanotranquillini
'''

from celery import task
from crowdcomputer import settings
from django.core.mail.message import EmailMultiAlternatives
import logging
import json
import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__name__)


@task()
def sendEmail(sender, title, html, email):
    html += "<br/> <a href=\"" + settings.CM_Location + "\">Crowd Computer</a>"
    #msg = EmailMultiAlternatives(title, html,sender + ' (CrowdComputer)', [], [email])
    #msg.attach_alternative(html, "text/html")
    log.debug("Mail %s %s %s %s" % (str(sender),title,html,email))
    #msg.send()

    msg = EmailMultiAlternatives(
    subject=title,
    body=html,
    from_email=sender, # + ' (CrowdComputer)',
    to=[email]
    )
    msg.attach_alternative(html, "text/html")
    # Send it:
    msg.send()

##FIXME: duplicated method, it's the only way i found.
#def getResults(task):
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

@task()
def triggerReceiver(task, results):
#    if task.status=='FN':
#        return
    log.info("ok here we go")
    log.debug("receive  " + task.taskactiviti.receive)
    username=settings.ACTIVITI_USERNAME
    password=settings.ACTIVITI_PASSWORD
#http://localhost:8080/activiti-rest/service/process-instance/149/signal
    url = settings.ACTIVITI_URL + "/process-instance/"+task.process.processactiviti.instanceID+"/signal"
    data = {}
    data['activityId'] = task.taskactiviti.receive+"-receive"
    name = task.parameters["data_name"]
    # data[name] = json.dumps(results)
    dumps = json.dumps(data)
    log.debug("dumps data %s", dumps)
    response = requests.post(url, data=dumps, auth=HTTPBasicAuth(username, password))
    log.debug(response.text)

@task()
# fimd rhe process id
def triggerReceiverInstance(taskinstance):
#    if task.status=='FN':
#        return
    username=settings.ACTIVITI_USERNAME
    password=settings.ACTIVITI_PASSWORD
#http://localhost:8080/activiti-rest/service/process-instance/149/signal
    url = settings.ACTIVITI_URL + "/process-instance/"+taskinstance.parameters['process_tactics_id']+"/signal"
    data = {}
    data['activityId'] = taskinstance.parameters['receiver']
    name = taskinstance.task.parameters["data_name"]
    data[name] = taskinstance.output_data.value
    dumps = json.dumps(data)
    log.debug("dumps data %s", dumps)
    response = requests.post(url, data=dumps, auth=HTTPBasicAuth(username, password))
    log.debug(response.text)
    
@task()
def deleteInstance(process):
#    if task.status=='FN':
#        return
    username="kermit"
    password="kermit"
#http://localhost:8080/activiti-rest/service/process-instance/149/signal
    url = settings.ACTIVITI_URL + "/process-instance/runtime/process-instances/"+process.processactiviti.instanceID
    response = requests.delete(url,auth=HTTPBasicAuth(username, password))
    log.debug(response.text)
    

