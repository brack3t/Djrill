from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class CreateSenderForm(forms.Form):
    email = forms.EmailField()
