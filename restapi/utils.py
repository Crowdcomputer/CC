from django.contrib.auth.models import User
from general.tasks import sendEmail
from crowdcomputer import settings
import logging
log = logging.getLogger(__name__)

def getorcreatedUserByEmail(email):
    users = User.objects.all().filter(email=email.strip())
    log.debug("users len %s for email %s"%(len(users),email))
    if len(users)>0:
        user = users[0]
        log.debug("worker is " + user.username)
        return user
    elif len(users)==0:
        user = User(username=email.strip()[:29],email=email.strip())
        user.save()
        log.debug("worker is " + user.username + " " + user.email)
        return user
    else:
        raise "no user"
    
def notifyUser(requester,executor,uuid):
    email_html = "Hi,<br> there is a task waiting for you <a href=\"" + settings.CM_Location + "/exe/execute/instance/" + str(uuid) + "/\">HERE</a><br/>"
    email_title = "[CrowdComputer] There is a task for you"
    log.debug("send email to " + executor.email)
    if settings.CELERY:
        sendEmail.delay(requester.username+"-"+requester.email,email_title,email_html,executor.email)
    else:
        sendEmail(requester.username+"-"+requester.email,email_title,email_html,executor.email)