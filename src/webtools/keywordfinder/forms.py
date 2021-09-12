from django import forms
from django.utils.translation import gettext as _

from keywordfinder.models import URL


class URLForm(forms.ModelForm):
    class Meta:
        model = URL
        fields = ['url']
        error_messages = {
            'url': {
                'required': _('Please enter an url'),
                'invalid': _('Please enter an valid url eg. https://www.google.com/')
            }
        }
