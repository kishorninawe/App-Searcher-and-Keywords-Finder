from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

package_name_validator = RegexValidator(r'^([A-Za-z]{1}[A-Za-z\d_]*\.)+[A-Za-z][A-Za-z\d_]*$')


class AppSearcherForm(forms.Form):
    store = forms.ChoiceField(
        label='Store',
        choices=(('google', 'Play Store'), ('apple', 'App Store')),
        widget=forms.RadioSelect,
        initial='google',
        required=False,
        error_messages={
            'invalid_choice': _('Please select a valid store')
        }
    )
    package_name = forms.CharField(
        label='Package Name',
        widget=forms.TextInput(attrs={'placeholder': 'Package Name'}),
        required=False,
        validators=[package_name_validator],
        error_messages={
            'invalid': _('Invalid package name')
        }
    )
    app_name = forms.CharField(
        label='Application Name',
        widget=forms.TextInput(attrs={'placeholder': 'Application Name'}),
        required=False
    )
    app_id = forms.CharField(
        label='Application Id',
        widget=forms.TextInput(attrs={'placeholder': 'Application Id'}),
        required=False)

    def clean(self):
        cleaned_data = super().clean()
        store = cleaned_data.get('store')
        package_name = cleaned_data.get('package_name')
        app_name = cleaned_data.get('app_name')
        app_id = cleaned_data.get('app_id')

        if store == 'google':
            if not package_name:
                self.add_error('package_name', _('Please enter a package name'))
        elif store == 'apple':
            if not app_name:
                self.add_error('app_name', _('Please enter an application name'))
            if not app_id:
                self.add_error('app_id', _('Please enter an application id'))
