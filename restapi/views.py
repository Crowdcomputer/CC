from crowdcomputer import settings
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.http.response import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from general.models import Process, Application, Reward, Task, TaskActiviti, \
    TaskInstance
from general.tasks import sendEmail
from general.utils import getResults, startTask, splitData, mergeData, \
    splitObjects, joinObjects, filterData
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from restapi.serializers import ProcessSerializer, HumanTaskSerializer, \
    RewardSerializer
from restapi.utils import getorcreatedUserByEmail, notifyUser
from uuid import uuid4
import json
import logging


# from general.utils import startProcess, sendEmail
log = logging.getLogger(__name__)

@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
#        'users': reverse('user-list', request=request),
#        'groups': reverse('group-list', request=request),
#        'process': reverse('process-list', request=request, format=format)
    })
    
class ProcessCreate(CreateAPIView):  
#    model = Process
    serializer_class = ProcessSerializer
    
    def pre_save(self, obj):
        user = self.request.user
        if settings.DEBUG and user.is_anonymous():
            user = User.objects.get(id=1)
        obj.owner = user
        token = self.request.META.get('HTTP_APP_ID')
        log.debug('token for the app is %s', token)
        if token:
            obj.application = Application.objects.get(token=token)
        else:
            obj.application = Application.objects.get(name='crowdcomputer')

class HumanTaskCreate(CreateAPIView):
    serializer_class = HumanTaskSerializer
    
    def pre_save(self, obj):
        #        rew = Reward(quantity=self.request.DATA['reward_quantity'],type=self.request.DATA['reward_type'])
        #        rew.save()
        #        obj.reward=rew
        obj.owner = self.request.user
        obj.process = get_object_or_404(Process, pk=self.kwargs['pk'])
        obj.uuid = uuid4()




        
# class TurkTaskCreate(CreateAPIView):
#    serializer_class = TurkTaskSerializer
#    
#    def pre_save(self, obj):
#        obj.user=self.request.user
#        obj.process=get_object_or_404(Process,pk=self.kwargs['pk'])
#        obj.uuid = uuid4()
# #        reward has to be made in dollars.

class SplitTask(APIView):
    
    def post(self, request, format=None):
        data = eval(request.DATA.get('data', '[]'))
        operation = request.DATA.get('operation', 'splitN')
        n = eval(request.DATA.get('n', '1'))
        m = eval(request.DATA.get('m', '0'))
#        log.debug("pars: %s %s %s %s" % (n, m, operation, data))
        log.debug("data %s",data)
        log.debug("pars %s %s %s " %(operation,n,m))
        res = splitData(data=data, operation=operation, n=n, m=m)
        log.debug("result %s",res)
        ret = {}
        ret['result'] = res
        return Response(ret, status.HTTP_200_OK)
    
class MergeTask(APIView):
    def post(self, request, format=None):
        data = eval(request.DATA.get('data', '[]'))
        res = mergeData(data=data)
        ret = {'result': res}
        return Response(ret, status.HTTP_200_OK)
    
class SplitObjectTask(APIView):
    
    def post(self, request, format=None):
        data = eval(request.DATA.get('data', '[]'))
        shared = request.DATA.get('shared', '[]')
        fields = request.DATA.get('fields', '[]')
        res = splitObjects(data, shared, fields)
        ret = {'result': res}
        return Response(ret, status.HTTP_200_OK)

class JoinObjectTask(APIView):
    
    def post(self, request, format=None):
        data = eval(request.DATA.get('data', '[]'))
        field = request.DATA.get('field', '')
        res = joinObjects(data, field)
        ret = {}
        ret['result'] = res
        return Response(ret, status.HTTP_200_OK) 
    
class FilterTask(APIView):
    
    def post(self, request, format=None):
        data = eval(request.DATA.get('data', '[]'))
        conditions = request.DATA.get('conditions', '[]')
        condition_operator = request.DATA.get('condition_operator', 'and')
        res = filterData(data,conditions,condition_operator)
        ret = {}
        ret['result'] = res
        return Response(ret, status.HTTP_200_OK)

class RewardCreate(CreateAPIView):
    model = Reward
    serializer_class = RewardSerializer
    
class Validate(APIView):
    def get_object(self, pk,user):
        try:
            t = TaskInstance.objects.get(pk=pk)
            if t.task.owner == user:
                return t 
            else:
                result={}
                result['result']="task is not yours"
                return Response(result, status.HTTP_401_UNAUTHORIZED)
        except Task.DoesNotExist:
            result={}
            result['result']="Task does not exists"
            return Response(result, status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,pk):
        ti = self.get_object(pk,request.user)
        if type(ti) is Response:
            return ti;
        validation = request.DATA.get('validation',"")
        log.debug("validation %s",validation    )
        ti.parameters['validation']=validation
        ti.save()
        result={}
        result['result']='ok'
        ti.finish()
        return Response(result, status.HTTP_200_OK)
 
class StartTask(APIView):
    def get_object(self, pk,user):
        try:
            t = Task.objects.get(pk=pk)
            if t.owner == user:
                return t 
            else:
                raise Http404
        except Task.DoesNotExist:
            log.debug("task does not exists")
            raise Http404
        
#    here we use put beacuse it seems a better design. POST would work as well.
    def put(self, request, pk, format=None):
        """

        :param request:
        :param pk:
        :param format:
        :return: :raise:
        """
        task = self.get_object(pk,request.user)
        data = request.DATA.get('data', None)
        name_receive = request.DATA.get('name', None)
        task_type = task.parameters['type']
        log.debug("type %s" % task_type)
#        for marketplace this is fine
        if task_type.lower() == "marketplace":
            log.debug('marketplace')
            ret = startTask(task, data)
        elif task_type.lower() == "newsletter":
            log.debug('newsletter')
            newsletter = task.parameters['emails']
#            if no data, then we create a instance per user
            if data==None or len(data)==0:
                log.debug("no data")
                task.humantask.number_of_instances=len(newsletter)
                log.debug("number of instances %", task.humantask.number_of_instances)
                ret = startTask(task, data)            
                taskinstances = task.taskinstance_set.all()
                i=0
#                send email to each user
                for email in newsletter:
                    executor = getorcreatedUserByEmail(email)
                    ti = taskinstances[i]
                    ti.executor=executor
                    ti.save()
                    notifyUser(request.user,executor,ti.uuid)
                    i=i+1
#            if there is data, then create the tasks and send each instance to a user
            else:
                log.debug('data are here')
                task.humantask.number_of_instances=1
                ret = startTask(task, data)   
                taskinstances = task.taskinstance_set.all()
                i=0
                for email in newsletter:
                    executor = getorcreatedUserByEmail(email)
#                    if there are less instances then users, then some will not get anything
                    if len(taskinstances)>i:
                        ti = taskinstances[i]
                        ti.executor=executor
                        ti.save()
                        notifyUser(request.user,executor,ti.uuid)
                    i=i+1
            task.save()
        elif task_type.lower() == "contest":
            log.debug("Contest, %s",data)
            task.parameters['data']=data
            log.debug("task parameters %s",task.parameters["data"])
            task.save()
            log.debug('contest')
            ret = startTask(task, data)
        elif task_type.lower() == "bid":
            log.debug('bid')
            ret = startTask(task, data)
        else:
            raise "no type specified"
        activitiTask,created = TaskActiviti.objects.get_or_create(task=task,receive=name_receive)
        result={}
        if ret:
            result['result']='ok'
            return Response(result, status.HTTP_200_OK)
        else:
            result['result']='error'
            return Response(result, status.HTTP_500_INTERNAL_SERVER_ERROR)



        
class TaskStatus(APIView):
    def get_object(self, pk,user):
        try:
            t = Task.objects.get(pk=pk)
            if t.owner == user:
                return t 
            else:
                raise Http404
        except Task.DoesNotExist:
            log.debug("task does not exists")
            raise Http404
        
    def get(self, request, pk, format=None):
        task = self.get_object(pk,request.user)
        result = {}
        result['status']=task.status
        return Response(result, status.HTTP_200_OK)
     
    

    
class TaskResults(APIView):
    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404
        
#    here we use put beacuse it seems a better design. POST would work as well.
    def get(self, request, pk, format=None):
        task = self.get_object(pk)
        result={}
        result['results']=getResults(task)
        return Response(result, status.HTTP_200_OK)
        
    
#    def post(self, request, pk, format=None):
#        pass
# class JSONResponse(HttpResponse):
#    """
#    An HttpResponse that renders it's content into JSON.
#    """
#    def __init__(self, data, **kwargs):
#        content = JSONRenderer().render(data)
#        kwargs['content_type'] = 'application/json'
#        super(JSONResponse, self).__init__(content, **kwargs) 
#   
# @api_view(['POST']) 
# def StartTask(request, id):  
#    
#    return JSONResponse(serializer.data, status=201) 

# class UserList(generics.ListAPIView):
#    """
#    API endpoint that represents a list of users.
#    """
#    model = User
#    serializer_class = UserSerializer
#    
# class UserCreate(generics.CreateAPIView):
#
#    model = User
#    serializer_class = UserSerializer
#    
#    def post_save(self, obj, created=False):
#        log.debug("post save")
#        api_g, creted = Group.objects.get_or_create(name='api')
#        api_g.user_set.add(obj)
#        api_g.save()
# #        obj.save()
#        
# # this check if user exists, if so gives back that user, otherwhise a new one.
# #TODO: allow only the creat
#
# #    def pre_save(self, obj):
# #        log.debug('pre save')
# #        api_g, creted = Group.objects.get_or_create(name='api')
# #        api_g.user_set.add(obj)
# #        api_g.save()
# #        obj.save()
#    
# #        generics.CreateAPIView.pre_save(self, obj)
#        
# #    this is needed for checking the user exists or not.
# #    adding the group is done in a bad way but it's the only method working.
#    def create(self, request, *args, **kwargs):
#        log.debug("create")
#        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
#        try:
#            if 'username' in request.DATA:
#                log.debug("username %s" %request.DATA['username'])
#            if ('email' in request.DATA) and (request.DATA['email']):
# #                retrive users via email. 
#                users = User.objects.all().filter(email=request.DATA['email'])
# #                take the first
#                user=users[0]
# #                in case there are many user with the same email (can it be?)
#                if len(users)>1:
# #                    check if there's one not creted via api, so a user that is registered
#                    users.filter(~Q(groups__name='api'))
# #                    if it exsist then ok. the else case is not needed since user is alredy assigned before.
#                    if len(users)>=1:
#                        user=users[0]    
#            else:
#                user = User.objects.get(username=request.DATA['username'])
#            serializer = UserSerializer(user)
#            headers = self.get_success_headers(serializer.data)
#            in_api = user.groups.filter(name='api').exists()
# #                
# #            for g in user.groups.all():
# #                log.debug("name %s",g.name)
#            log.debug("in api %s ", in_api)
#            return Response(serializer.data, status=status.HTTP_201_CREATED,
#                                headers=headers)
#        except Exception, e:
#            log.debug('exception %s',e)
#            return generics.CreateAPIView.create(self, request, *args, **kwargs)
# #            if serializer.is_valid():
# #                self.pre_save(serializer.object)
# #                self.object = serializer.save()
# #                api_g= Group.objects.get(name='api')
# #                api_g.user_set.add(self.object)
# #                api_g.save()
# #                
# #                headers = self.get_success_headers(serializer.data)
# #                return Response(serializer.data, status=status.HTTP_201_CREATED,
# #                                headers=headers)
# #    
# #            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ##            return generics.CreateAPIView.create(self, request, *args, **kwargs)
# #            self.object.save()
#            
# #            self.object.group=api_g
# #            self.group.save()
# #            return createAPI
#
#
# class MyUserDetail(APIView):
#    def get(self, request, format=None):
#        user = User.objects.get(pk=request.user.pk)
#        serializer = UserSerializer(user)
#        return JSONResponse(serializer.data)
#    
# class SendEmail(APIView):
#    def get_user(self, pk):
#        return get_object_or_404(User,pk=pk)
#         
#    def post(self, request, pk,  format=None):
#        email = self.get_user(pk).email;
#        subject = request.POST['subject']
#        text=request.POST['text']
#        sender=request.POST['sender']
#        app=get_object_or_404(general.models.Application,token=request.META.get('HTTP_APP_ID'))
#        #sender="["+app.name+"] "+sender
#        sendEmail(sender,subject,text,email)
#        return HttpResponse(status=status.HTTP_200_OK)
#        
#    
# class UserDetail(generics.RetrieveAPIView):
#    """
#    API endpoint that represents a single user.
#    """
#    model = User
#    serializer_class = UserSerializer
#    
# #class GroupList(generics.ListCreateAPIView):
# #    """
# #    API endpoint that represents a list of groups.
# #    """
# #    model = Group
# #    serializer_class = GroupSerializer
# #
# class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
#    """
#    API endpoint that represents a single group.
#    """
#    model = Group
#    serializer_class = GroupSerializer
#    
# #    
# # ----------- Other tutorial
# #
# #from django.views.decorators.csrf import csrf_exempt
# #from rest_framework.renderers import JSONRenderer
# #from rest_framework.parsers import JSONParser
# #
# class JSONResponse(HttpResponse):
#    """
#    An HttpResponse that renders it's content into JSON.
#    """
#    def __init__(self, data, **kwargs):
#        content = JSONRenderer().render(data)
#        kwargs['content_type'] = 'application/json'
#        super(JSONResponse, self).__init__(content, **kwargs)
#        
# #@csrf_exempt
# #@api_view(['GET', 'POST'])
# #def process_list(request):
# #    """
# #    List all code snippets, or create a new snippet.
# #    """
# #    if request.method == 'GET':
# #        log.warning("no access control")
# #        processes = Process.objects.all()
# #        serializer = ProcessSerializer(processes)
# #        return JSONResponse(serializer.data)
# #
# #    elif request.method == 'POST':
# #        log.warning("no access control")
# #        data = JSONParser().parse(request)
# #        serializer = ProcessSerializer(data=data)
# #        if serializer.is_valid():
# #            serializer.save()
# #            return JSONResponse(serializer.data, status=201)
# #        else:
# #            return JSONResponse(serializer.errors, status=400)
# #
# #
# #@csrf_exempt
# #@api_view(['GET', 'PUT', 'DELETE'])
# #def process_detail(request, pk):
# #    """
# #    Retrieve, update or delete a code snippet.
# #    """
# #    try:
# #        process = Process.objects.get(pk=pk)
# #    except Process.DoesNotExist:
# #        return HttpResponse(status=404)
# #
# #    if request.method == 'GET':
# #        serializer = ProcessSerializer(process)
# #        return JSONResponse(serializer.data)
# #
# #    elif request.method == 'PUT':
# #        data = JSONParser().parse(request)
# #        serializer = ProcessSerializer(process, data=data)
# #        if serializer.is_valid():
# #            serializer.save()
# #            return JSONResponse(serializer.data)
# #        else:
# #            return JSONResponse(serializer.errors, status=400)
# #
# #    elif request.method == 'DELETE':
# #        process.delete()
# #        return HttpResponse(status=204)
# #--- class based
#    
#    
# #this is to show the token to user
class TokenList(APIView):
    def get(self, request, format=None):
        token, created = Token.objects.get_or_create(user=self.request.user)
        log.debug("token %s %s" %(created,token))
        tt={}
        tt['token']=token.key
        return HttpResponse(json.dumps(tt), mimetype="application/json")  
    
class TestView(APIView):
    def get(self, request, format=None):
        auth = request.META.get('HTTP_Authorization    ')
        app = request.META.get('HTTP_APP_ID')
#        token, created = Token.objects.get_or_create(user=self.request.user)
        log.debug("header %s %s",(auth,app) )
        tt={}
        tt['auth']=auth
        tt['app']=app
        return HttpResponse(json.dumps(tt), mimetype="application/json")  
#
# #class ProcessList(APIView):
# #    
# #    def get(self, request, format=None):
# #        log.warning("no access control")
# #        processes = Process.objects.all()
# #        serializer = ProcessSerializer(processes)
# #        return JSONResponse(serializer.data)
# #
# #    def post(self, request, format=None):
# #        log.warning("no access control")
# #        data = request.DATA
# #        serializer = ProcessSerializer(data=data)
# #        if serializer.is_valid():
# #            serializer.save()
# #            return JSONResponse(serializer.data, status=201)
# #        else:
# #            return JSONResponse(serializer.errors, status=400)
# #
# #
# class ProcessStartStop(APIView):
#
#    def get_object(self, pk,user):
#        try:
#            process = Process.objects.get(pk=pk,user=user)
#            return process
#        except Process.DoesNotExist:
#            return HttpResponse(status=404)
#        
#    def post(self, request, pk, format=None):
#        process = self.get_object(pk,request.user)        
#        startProcess(process)
#        return HttpResponse(status=200)
#
# #    def put(self, request, pk, format=None):
# #        process = self.get_object(pk)  
# #        data = request.DATA
# #        serializer = ProcessSerializer(process, data=data)
# #        if serializer.is_valid():
# #            serializer.save()
# #            return JSONResponse(serializer.data)
# #        else:
# #            return JSONResponse(serializer.errors, status=400)
#        
# #    def delete(self, request, pk, format=None):
# #        process = self.get_object(pk) 
# #        process.delete()
# #        return HttpResponse(status=204)
#
# #-- generics 
#
# class TaskInstancesStatuses(APIView):
#    
#    def get(self, request, pk, format = None):
#        task = get_object_or_404(Task,pk=pk)
#        res ={}
#        res['Total']=task.taskinstance_set.count()
#        for status, description in Task.STATUS_CHOISE:
#            log.debug("status %s, description %s" % (status,description))
#            res[description]=task.taskinstance_set.filter(status=status).count()
#        log.debug("res %s", res)
#        return HttpResponse(json.dumps(res), mimetype="application/json")
#
#        
# #print the list of all the processes of a user. allow only get
# class ProcessList(generics.ListCreateAPIView):
#    model = Process
#    serializer_class = ProcessSerializer
#    
#    def pre_save(self, obj):
#        obj.user = self.request.user
#        token = self.request.META.get('HTTP_APP_ID')
#        log.debug('token for the app is %s',token)
#        if token:
#            obj.application=general.models.Application.objects.get(token=token)
#        
#    def get_queryset(self):
#        qs=generics.ListCreateAPIView.get_queryset(self)
#        user = self.request.user
#        token = self.request.META.get('HTTP_APP_ID')
#        log.debug("token %s" % token)
#        if token is not None:
#            application=general.models.Application.objects.get(token=token)
#            return qs.filter(user=user).filter(application=application)
#        else:
#            return qs.filter(user=user)
#        
#
#
#
# #   print the process detail, so all the parameters. allow all the methods
# class ProcessDetail(generics.RetrieveUpdateDestroyAPIView):
#    model = Process
#    serializer_class = ProcessDetailSerializer
#    
#    def pre_save(self, obj):
#        obj.user = self.request.user
#        
#   
#
# # all the detail of a task, allow all the methods
# class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
#    model = Task
#    serializer_class = TaskDetailSerializer
#    
#    def pre_save(self, obj):
#        obj.user = self.request.user
#
# # all the task of a process. allow only get
# class ProcessTaskList(generics.ListCreateAPIView):
#    model = Task
#    serializer_class = ProcessTaskSerializer
#    
#    def pre_save(self, obj):
#        obj.user = self.request.user
#        
#    def get_queryset(self):
#        pk=self.kwargs['pk']
#        qs = Task.objects.all().filter(process=pk)
#        user = self.request.user
#        return qs.filter(user=user)
#
# class RewardCreate(generics.CreateAPIView):
#    model = Reward
#    serializer_class = RewardSerializer
#    
# class RewardReadUpdate(generics.RetrieveUpdateAPIView):
# #    permission are checked already by the permission class.
#    model = Reward
#    serializer_class = RewardSerializer
#
#
# # all the instances of a task. allow only get
# class TaskInstanceList(generics.ListAPIView):
# #    here control on ownership is tricky. so don't implemented it yet
#    model = TaskInstance
#    serializer_class = TaskInstanceListSerializer
#     
#    def pre_save(self, obj):
#        obj.user = self.request.user
#        
#    def get_queryset(self):
#        qs=generics.ListAPIView.get_queryset(self)
#        qs_filter = qs.filter(task = self.kwargs['pk']).filter(task__user=self.request.user)
#        log.debug("qs_filter len %s",qs_filter.count())
#        return qs_filter
#    
# # show all the detail of an instance. allow all the methods.
# class TaskInstanceDetail(generics.RetrieveUpdateDestroyAPIView):
#    model = TaskInstance
#    serializer_class = TaskInstanceDetailSerializer
#    
# # create Task
# class ProcessTaskCreate(generics.CreateAPIView):
#    model=Task
#    serializer_class = TaskDetailSerializer
#    
# #    
# #    
# #    def initialize_request(self, request, *args, **kargs):
# #        init= generics.CreateAPIView.initialize_request(self, request, *args, **kargs)
# #        init['date_deadline']=lambda: (date.today() + timedelta(days=7))
# #        return init
#
#    def pre_save(self, obj):
#        obj.user=self.request.user
#        obj.process=get_object_or_404(Process,pk=self.kwargs['pk'])
#        obj.uuid = uuid4()

    
    
