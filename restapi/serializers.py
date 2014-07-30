from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from general.models import Process, Task, TaskInstance, Reward, HumanTask,\
    REWARDS
from decimal import Decimal


#
#class UserSerializer(serializers.ModelSerializer):
#    pk = serializers.Field()
#    groups=serializers.ManySlugRelatedField(read_only=True, slug_field='name')
#    class Meta:
#        model = User
#        fields = ('pk', 'username', 'email','groups')
#
#class GroupSerializer(serializers.HyperlinkedModelSerializer):
#    
#    permissions = serializers.ManySlugRelatedField(
#        slug_field='codename',
#        queryset=Permission.objects.all()
#    )
#
#    class Meta:
#        model = Group
#        fields = ('name')
#
# Serializer of the process. used in ProcessList
class ProcessSerializer(serializers.ModelSerializer):
    pk = serializers.Field()
    owner = serializers.Field(source='owner.username')
    application = serializers.Field(source='application.name')
    
    class Meta:
        model = Process
        
class HumanTaskSerializer(serializers.ModelSerializer):
    pk = serializers.Field()
#    instances = serializers.HyperlinkedIdentityField(view_name='task-instances', format='json')
    reward =  serializers.PrimaryKeyRelatedField()
    validation = serializers.PrimaryKeyRelatedField
    owner = serializers.Field(source='owner.username')
#    reward_type = serializers.ChoiceField(REWARDS)
#    reward_quantity = serializers.DecimalField()
  
    class Meta:
        model = HumanTask    
        read_only_fields = ('uuid', 'process','status')  
       

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
       
#       
#   
## detal of the process. used in ProcessDetail
#class ProcessDetailSerializer(serializers.HyperlinkedModelSerializer):
#    user = serializers.Field(source='user.username')
#    task_list = serializers.HyperlinkedIdentityField(view_name='task-list', format='json')
#
#    class Meta:
#        model = Process
#        fields = ('title', 'description', 'status', 'user', 'task_list',)
#        read_only_fields = ('user',)
#
##  Serializer of Dertail of Instance. used in Task instance detail
#class RewardSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Reward
#       
## Detail of a Task. used in taskdetail and processtaskcreation
#class TaskDetailSerializer(serializers.HyperlinkedModelSerializer):
#    pk = serializers.Field()
#    instances = serializers.HyperlinkedIdentityField(view_name='task-instances', format='json')
#    reward =  serializers.PrimaryKeyRelatedField()
#    
#    class Meta:
#        model = Task
#        read_only_fields = ('uuid', 'process', 'user')
#
##    def validate(self, attrs):
##        return serializers.HyperlinkedModelSerializer.validate(self, attrs)
#    
##TaskDetailSerializer.base_fields['reward'] = RewardSerializer()
#
#
## Serializer of the Task. used in the Process-Task List
#class ProcessTaskSerializer(serializers.HyperlinkedModelSerializer):
#    detail = serializers.HyperlinkedIdentityField(view_name='task-detail', format='json')
#    pk = serializers.Field()
#    class Meta:
#        model = Task
#        fields = ('pk','title', 'description', 'uuid', 'status', 'detail')
#        read_only_fields = ('uuid',)
#        
#        
## Serialzier of TaskInstance used in Task instance list
#class TaskInstanceListSerializer(serializers.ModelSerializer):
#    detail = serializers.HyperlinkedIdentityField(view_name='task-instance-detail', format='json')
#    pk = serializers.Field()
#    user = serializers.PrimaryKeyRelatedField()
#
#    class Meta:
#        model = TaskInstance
#        fields = ('pk', 'uuid', 'detail', 'status','user')
#   
#TaskInstanceListSerializer.base_fields['user'] = UserSerializer()
#
# 
##  Serializer of Dertail of Instance. used in Task instance detail
#class TaskInstanceDetailSerializer(serializers.ModelSerializer):
#    pk = serializers.Field()
#    input = serializers.PrimaryKeyRelatedField(required=False)
#    output = serializers.PrimaryKeyRelatedField(required=False)
#    
#    class Meta:
#        model = TaskInstance
#    


#    class Meta:
#        model = Task
#        fields = ('title', 'description', 'input_url')
