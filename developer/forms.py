'''
Created on Feb 1, 2013

@author: stefanotranquillini
'''
from django.forms.models import ModelForm
from general.models import Application
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.models import User
        

class AppForm(ModelForm):
    name = forms.CharField(label=(u'App Title'))
    url = forms.URLField(label=(u'URL of your application'))

    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput)

    class Meta:
        model = Application
        exclude = ('token')

    def clean_name(self):
        name = str(self.cleaned_data['name'])
    
       #exists = Application.objects.filter(name=name).exists()
       #instead of that in the models we have Application name unique=True
       # if name.lower()=='crowdcomputer':
       #     self._errors["name"]=self.error_class(["Crowdcomputer is reserved"])
        return name
        
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.form_class = 'form-horizontal'
        super(AppForm, self).__init__(*args, **kwargs)
