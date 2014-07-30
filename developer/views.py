'''
Created on Feb 1, 2013

@author: stefanotranquillini
'''
from developer.forms import AppForm
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from general.models import Application
from uuid import uuid4

class ApplicationCreation(CreateView):
    template_name = 'developer/creation.html'
    form_class = AppForm
    
    def get_initial(self):
        initial = {}
        initial['user']=self.request.user
        return initial
    
    def form_valid(self, form):
        app = form.save()
        app.token=str(uuid4()).replace('-','')
        app.save()
        print app.user.username
        return redirect(reverse_lazy('d-application-list'))
    
class ApplicationList(ListView):
    template_name='developer/application_list.html'
    context_object_name="application_list"
    def get_queryset(self, **kwargs):
        application_list=Application.objects.all()
        return application_list
