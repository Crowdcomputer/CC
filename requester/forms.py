from django import forms
from datetime import date, timedelta
from general.models import Task, Process, Application, HumanTask, \
    Reward, ValidationTask, MachineTask
    # SplitDataTask, FilterDataTask, 
from django.contrib.auth.models import User
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Layout
import general
import logging
from general import utils
from decimal import Decimal
from django.utils.datetime_safe import datetime
from django.forms.forms import Form
from django.forms.fields import FileField

log = logging.getLogger(__name__)

class ProcessForm(ModelForm):
    title = forms.CharField(label=(u'Process name'))
    description = forms.CharField(label=(u'Process description'), widget=forms.Textarea())
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)
    application = forms.ModelChoiceField(queryset=Application.objects.all(), widget=forms.HiddenInput)
    
    class Meta:
        model = Process
        exclude = ('date_created', 'status',)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.form_class = 'form-horizontal'
        super(ProcessForm, self).__init__(*args, **kwargs)




   
# TODO: there should be a smarter way to do this.
class ValidationForm(ModelForm):
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)
    process = forms.ModelChoiceField(queryset=Process.objects.all(), widget=forms.HiddenInput)

    class Meta:
        model = ValidationTask
        exclude = ('to_validate',) + ('parameters', 'status', 'objects', 'date_deadline', 'date_created')

# TODO: there should be a smarter way to do this.  
class HumanTaskForm(ModelForm):
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)
    process = forms.ModelChoiceField(queryset=Process.objects.all(), widget=forms.HiddenInput)
    title = forms.CharField(label=(u'Task name'))
    description = forms.CharField(label=(u'Task description'), widget=forms.Textarea())
    page_url = forms.CharField(label=(u'A url of the task web form'), required=True)
    platfom = forms.ChoiceField(choices=general.models.PLATFORMS, widget=forms.Select(), label=(u'Platform where to deploy'), required=False)
    date_deadline = forms.DateTimeField(label=(u'Deadline (DD/MM/YYYY HH:MM)'), initial=lambda: (datetime.now() + timedelta(days=7)), widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M'), input_formats=('%d/%m/%Y %H:%M',))
    number_of_instances = forms.IntegerField(label=(u'Number of assignments per Task'), required=True, initial=1)
    type = forms.ChoiceField(choices=general.models.REWARDS, widget=forms.Select(), label=(u'Reward Type'), required=True)
    quantity = forms.DecimalField(decimal_places=2, max_digits=8, required=True, initial=Decimal('0.00'))

    class Meta:
        model = HumanTask
        exclude = ('parameters', 'status', 'objects', 'date_deadline', 'date_created') + ('uuid', 'reward')
    
    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        log.debug('%s' % data)
        if data < 0:
            raise forms.ValidationError("C'mon, value must be > 0")
        return data
     
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(Fieldset('Human Task', 'owner', 'process', 'title', 'description', 'platform', 'page_url', 'number_of_instances', 'date_deadline', 'type', 'quantity'))
        super(HumanTaskForm, self).__init__(*args, **kwargs)

class MachineTaskForm(ModelForm):
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)
    process = forms.ModelChoiceField(queryset=Process.objects.all(), widget=forms.HiddenInput)
    title = forms.CharField(label=(u'Task name'))
    description = forms.CharField(label=(u'Task description'), widget=forms.Textarea())
    date_deadline = forms.DateTimeField(label=(u'Deadline (DD/MM/YYYY HH:MM)'), initial=lambda: (datetime.now() + timedelta(days=7)), widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M'), input_formats=('%d/%m/%Y %H:%M',))
    service_url = forms.CharField(label=(u'The url of the service'), required=True)

   
    class Meta:
        model = MachineTask
        exclude = ('parameters', 'status', 'objects', 'date_deadline', 'date_created')
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(Fieldset('Machine Task', 'owner', 'process', 'title', 'description', 'service_url', 'date_deadline'))
        super(MachineTaskForm, self).__init__(*args, **kwargs)
        

class UploadFileForm(Form):
    file  = FileField()
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.form_class = 'form-horizontal'
        super(UploadFileForm, self).__init__(*args, **kwargs)
        
class ValidationForm(Form):
    validation = forms.IntegerField(max_value=100,min_value=0)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.form_class = 'form-horizontal'
        super(ValidationForm, self).__init__(*args, **kwargs)

'''
class SplitDataTaskForm(ModelForm):
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)
    process = forms.ModelChoiceField(queryset=Process.objects.all(), widget=forms.HiddenInput)
    title = forms.CharField(label=(u'Operation name'))
    description = forms.CharField(label=(u'Task description'), initial='task description', widget=forms.HiddenInput)
    date_deadline = forms.DateTimeField(label=(u'Deadline (DD/MM/YYYY HH:MM)'), initial=lambda: (datetime.now() + timedelta(days=7)), widget=forms.HiddenInput) # widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M'), input_formats=('%d/%m/%Y %H:%M',))
    split = forms.ChoiceField(choices=general.models.SPLIT_CHOICE, widget=forms.Select(), label=(u'Split option'), required=False)
    
    class Meta:
        model = SplitDataTask
        exclude = ('parameters', 'status', 'objects')
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(Fieldset('SplitData Operation', 'owner', 'process', 'title', 'split', 'split_field_N', 'split_field_M','date_deadline', 'description'))
        super(SplitDataTaskForm, self).__init__(*args, **kwargs)
class FilterDataTaskForm(ModelForm):
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)
    process = forms.ModelChoiceField(queryset=Process.objects.all(), widget=forms.HiddenInput)
    title = forms.CharField(label=(u'Operation name'))
    description = forms.CharField(label=(u'Task description'), initial='task description', widget=forms.HiddenInput)
    date_deadline = forms.DateTimeField(label=(u'Deadline (DD/MM/YYYY HH:MM)'), initial=lambda: (datetime.now() + timedelta(days=7)), widget=forms.HiddenInput) # widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M'), input_formats=('%d/%m/%Y %H:%M',))
    filter = forms.ChoiceField(choices=general.models.FILTER_CHOICE, widget=forms.Select(), label=(u'Filter option'), required=False)
    class Meta:
        model = FilterDataTask
        exclude = ('parameters', 'status', 'objects')
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(Fieldset('FilterData Operation', 'owner', 'process', 'title', 'filter', 'filter_field', 'filter_value', 'filter_exclude', 'date_deadline', 'description'))
        super(FilterDataTaskForm, self).__init__(*args, **kwargs)

'''
#class HumanTaskForm(TaskForm,ModelForm):
#    owner = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
#    process = forms.ModelChoiceField(queryset=Process.objects.all(),widget=forms.HiddenInput)
#    class Meta:
#        model= HumanTask
#        exclude = ('uuid','reward')
    
#    def __init__(self, *args, **kwargs):
#        super(HumanTaskForm, self).__init__(*args, **kwargs)
#        log.debug(self.fields)
#        validationForm = ValidationForm(prefix="validation")
#        for v in validationForm.fields:
#            log.debug("%s " %(v))
#        self.fields (validationForm.fields)
#        log.debug(self.fields)     
     
#class FullHumanTaskForm(ValidationForm,RewardForm,HumanTaskForm):
##    pass
#    def __init__(self, *args, **kwargs):
##        ModelForm.__init__(self, *args, **kwargs) # Call the constructor of ModelForm
#        RewardForm.__init__(self, *args, **kwargs) # Call the constructor of polo
#        ValidationForm.__init__(self, *args, **kwargs)
#        HumanTaskForm.__init__(self, *args, **kwargs)

#class TaskForm(ModelForm):
#    title = forms.CharField(label=(u'Task name'))
#    description = forms.CharField(label=(u'Task description'), widget=forms.Textarea())
#    input_url = forms.CharField(label=(u'A url of the task web form'), required=True)
#    category = forms.ChoiceField(label=(u'Type of the task:'),help_text = '<strong>Human</strong>: executed by the crowd via webform, <br/><strong>Machine</strong>: calls an external web service.',choices=Task.TASK_TYPE_CHOISE, required=True)
#    input_task = forms.ModelMultipleChoiceField(queryset=Task.objects.none(), required=False, widget=forms.CheckboxSelectMultiple(), label=(u'Take as an input results from:'))
#    input_task_field = forms.CharField(label=(u'Shared field name'),help_text = 'Id of the field used for merging the data of the selected input tasks<hr/>', required=False)
#    split=forms.ChoiceField(choices=Task.SPLIT_CHOICE,widget = forms.Select(),label=(u'Splitting Function'),help_text = 'This function is applied on the input data to create the set of input for each instances',required=False)
#    split_field_N = forms.IntegerField(label=(u'N:'),help_text = 'the number of items in the set',required=False)
#    split_field_M = forms.IntegerField(label=(u'M:'),help_text = 'the number of overlapping items in each set',required=False)
##    redirect = forms.ModelChoiceField(queryset=Task.objects.all(), required=False)
#    reward_type=forms.ChoiceField(choices=general.models.REWARDS,widget = forms.Select(),label=(u'Reward Type'),required=False)
#    reward_quantity = forms.DecimalField(decimal_places=2, max_digits=8,required=False,initial=Decimal('0.00'))
#    instances_required = forms.IntegerField(label=(u'Amount of people<br/> to perform one instance'), required=False)
#    is_unique = forms.BooleanField(widget=forms.Select(choices=((True, 'Yes'), (False, 'No'))),label='Worker must answer only one time?', initial=True, required=False)
#    date_deadline = forms.DateTimeField(label=(u'Deadline (DD/MM/YYYY HH:MM)'),help_text='<hr/><h5 class="muted">Reward</h5>', initial=lambda: (datetime.now() + timedelta(days=7)), widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M'), input_formats=('%d/%m/%Y %H:%M',))
#    process = forms.ModelChoiceField(queryset=Process.objects.all(),widget=forms.HiddenInput)
#    user = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
#    isMturk = forms.BooleanField(widget=forms.Select(choices=((True, 'Yes'), (False, 'No'))),label='Deploy task in Mturk (test)', initial=False, required=False)
#    reward_mturk = forms.DecimalField(label=(u'Reward for AMT, in $'),decimal_places=2, max_digits=8,required=False,initial=Decimal('0.00'))
#    
#    def clean(self):
#        cleaned_data = super(TaskForm, self).clean()
#        tasks = cleaned_data['input_task']
#        d_input = cleaned_data['input_task_field']
#        if len(tasks)>1 and  d_input == '':
#            msg="This field is required"
#            self._errors["input_task_field"] = self.error_class([msg])
#        else:
#            if len(tasks)<=1:
#                cleaned_data['input_task_field']=""
##            raise forms.ValidationError("You have to specify the field")
##        if we have one or more inputs
#        if len(tasks)>0:
#            sp=int(cleaned_data['split'])
#            print ('%s (%s) = %s (%s) -> %s'%(sp,type(sp),general.models.SET_N,type(general.models.SET_N),(sp==general.models.SET_N)))
##            if it is split in N and N is not specified
#            if sp==general.models.SET_N or sp==general.models.COMBINATION:
#                msg="You have to specify the field"
#                n=cleaned_data['split_field_N']
#                log.debug('n %s',n)
#                if n is None:
#                    self._errors["split_field_N"] = self.error_class([msg])
##            if it is N overlapp M and N or/and M are not specified
#            elif sp==general.models.SET_NM:
#                msg="You have to specify the field"
#                n=cleaned_data['split_field_N']
#                m=cleaned_data['split_field_M']
#                log.debug('n %s m %s'%(n,m))
#
#                if n is None:
#                    self._errors["split_field_N"] = self.error_class([msg])
#                if m is None:
#                    self._errors["split_field_M"] = self.error_class([msg])
##        for MT the instances_required is 1
#        log.debug("category %s "%cleaned_data['category'])
#        
##        log.debug("instance_required %s " %cleaned_data['instances_required'])
#        if cleaned_data['category']=='MT':
#            cleaned_data['instances_required']=1
#        else:
#            if cleaned_data['instances_required'] is None:
#                self._errors["instances_required"] = self.error_class([msg])
#                log.debug("AFTER: instance_required %s " %cleaned_data['instances_required'])
#                
#        log.debug(self._errors)
#        return cleaned_data
#
#        
#    class Meta:
#        model = Task
##       taking out category and redirection, for the time being we do not need them 
#        exclude = ('status', 'uuid','type','redirect','reward','parameters')
#
#    def __init__(self, *args, **kwargs):
#        self.helper = FormHelper()
#        self.helper.form_method = 'post'
#        self.helper.add_input(Submit('submit', 'Save'))
#        self.helper.form_class = 'form-horizontal'
#        self.helper.layout=Layout(Fieldset('Task','title','description','category','input_url','input_task','input_task_field','isMturk','reward_mturk','split','split_field_N','split_field_M','instances_required','is_unique','date_deadline','process','user','reward_type','reward_quantity'
#                                ))
#        super(TaskForm, self).__init__(*args, **kwargs)
#        
        
    #def get_user(self):
    #    print self.request.user

    #def __init__(self, user, *args, **kwargs):
    #    self.helper = FormHelper()
    #    self.helper.form_method = 'post'
    #    self.helper.add_input(Submit('submit', 'Submit'))
    #    super(TaskForm, self).__init__(user, *args, **kwargs)
    #def __init__(self,user, *args, **kwargs):
        #self.helper = FormHelper()
        #self.user = user
        #self.helper.form_method = 'post'
        #self.helper.add_input(Submit('submit', 'Save'))
        #user_id = kwargs.pop('user', None)
        #super(TaskForm, self).__init__( *args, **kwargs)
        #self.fields['input_task'].queryset = Task.objects.get(pk=1)
        #self.input_task.queryset = Task.objects.all()
