from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    UserChangeForm as BaseUserChangeForm

from users.models import CustomUser


class RegistrationStep1Form(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        if username and len(username) < 5:
            msg = 'Username cannot be shorter than 5 characters.'
            self.add_error('username', msg)

        return self.cleaned_data


class RegistrationStep2Form(forms.Form):

    first_name = forms.CharField(max_length=255, required=False, min_length=3,
                                 help_text='Optional.')
    last_name = forms.CharField(max_length=255, required=False, min_length=3,
                                help_text='Optional.')

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']


class RegistrationStep3Form(forms.Form):
    position = forms.CharField(max_length=255,  required=False, min_length=3,
                               help_text='Optional. For example: Computer Science Student, Arts Teacher, Rocket Engineer.')


class RegistrationStep4Form(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ['password1', 'password2']


class LoginWithEmailForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.error_messages = {
            'invalid_login': "Please enter a correct email and password. Note that both fields may be case-sensitive.",
            'inactive': "This account is inactive.",
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if email and password:
            self.cleaned_data['email'] = email.lower()

        return self.cleaned_data


class UserChangeForm(BaseUserChangeForm):
    password = None
    position = forms.CharField(max_length=255, min_length=3, required=False,
                               help_text='Optional. For example: Computer Science Student, Arts Teacher, Rocket Engineer.')
    first_name = forms.CharField(max_length=255, required=False, min_length=3,
                                 help_text='Optional.')
    last_name = forms.CharField(max_length=255, required=False, min_length=3,
                                help_text='Optional.')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'position']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        if username and len(username) < 5:
            msg = 'Username cannot be shorter than 5 characters.'

            self.add_error('username', msg)

        return self.cleaned_data
