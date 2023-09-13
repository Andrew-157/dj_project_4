from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    UserChangeForm as BaseUserChangeForm

from users.models import CustomUser


class RegistrationStep1Form(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'})}

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if username and len(username) < 5:
            msg = 'Username cannot be shorter than 5 characters.'
            self.add_error('username', msg)

        if CustomUser.objects.filter(email=email).first():
            msg = 'A user with this email already exists.'
            self.add_error('email', msg)

        return self.cleaned_data


class RegistrationStep2Form(forms.Form):

    first_name = forms.CharField(max_length=255, required=False,
                                 help_text='Optional.',
                                 widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=255, required=False,
                                help_text='Optional.',
                                widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if first_name and len(first_name) < 3:
            msg = 'First Name cannot be shorter than 3 characters.'
            self.add_error('first_name', msg)

        if last_name and len(last_name) < 3:
            msg = 'Last Name cannot be shorter than 3 characters.'
            self.add_error('last_name', msg)

        return self.cleaned_data


class RegistrationStep3Form(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['position']
        widgets = {
            'position': forms.TextInput(attrs={'placeholder': 'Enter your position'})
        }


class RegistrationStep4Form(UserCreationForm):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(RegistrationStep4Form, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={"autocomplete": "new-password",
                   "placeholder": "Enter your password"}
        )
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={"autocomplete": "new-password",
                   "placeholder": "Enter the same password", }
        )

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
        self.fields['username'].widget = forms.EmailInput(
            attrs={'placeholder': 'Enter email you used during registration'}
        )
        self.fields['password'].widget = forms.PasswordInput(
            attrs={'placeholder': 'Enter password you used during registration'}
        )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if email and password:
            self.cleaned_data['email'] = email.lower()

        return self.cleaned_data


class UserChangeForm(BaseUserChangeForm):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = kwargs['instance']

    password = None
    # position = forms.CharField(max_length=255, min_length=3, required=False,
    #                            help_text='Optional. For example: Computer Science Student, Arts Teacher, Rocket Engineer.')
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
        email = cleaned_data.get('email')

        if username and len(username) < 5:
            msg = 'Username cannot be shorter than 5 characters.'
            self.add_error('username', msg)

        user_with_email = CustomUser.objects.filter(email=email).first()
        if user_with_email and (user_with_email != self.user):
            msg = 'A user with this email already exists.'
            self.add_error('email', msg)

        return self.cleaned_data
