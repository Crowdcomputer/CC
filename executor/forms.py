__author__ = 'stefanotranquillini'
from crispy_forms.helper import FormHelper
from django.contrib.auth.models import User
from crispy_forms.layout import Submit, Fieldset, Layout
from django import forms
from django.forms.forms import Form

class BidForm(Form):
    amount  = forms.DecimalField(label=(u'Your bid'))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', 'Save'))
        super(BidForm, self).__init__(*args, **kwargs)