from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

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
                                 help_text='Optional.', label='First Name*')
    last_name = forms.CharField(max_length=255, required=False, min_length=3,
                                help_text='Optional.', label='Last Name*')

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']


class RegistrationStep3Form(forms.Form):
    position = forms.CharField(max_length=255,  required=False,
                               help_text='Optional. For example: Computer Science Student, Arts Teacher, Rocket Engineer.',
                               label='Position*')


class RegistrationStep4Form(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ['password1', 'password2']
