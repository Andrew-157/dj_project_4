from django import forms
from django.core.exceptions import ValidationError

from users.models import CustomUser


class RegistrationStep1Form(forms.Form):
    username = forms.CharField(max_length=255,
                               min_length=5,
                               required=True)
    email = forms.EmailField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        user_with_username = CustomUser.objects.filter(username=username).first()
        user_with_email = CustomUser.objects.filter(email=email).first()

        if user_with_username:
            msg = 'User with this username already exists.'
            self.add_error('username', msg)

        if user_with_email:
            msg = 'User with this email already exists.'
            self.add_error('email', msg)
        
        return self.cleaned_data
    

class RegistrationStep2Form(forms.Form):
    # Allow users to have either both first and last name,
    # only first name or only last name
    first_name = forms.CharField(max_length=255,
                                 min_length=3,
                                 required=False)
    last_name = forms.CharField(max_length=255,
                                min_length=3,
                                required=False)
    

def validate_image(image):
    file_size = image.file.size

    limit_mb = 5
    if file_size > limit_mb * 1024**2:
        raise ValidationError(
            f"Maximum size of profile image is {limit_mb} MB")


class RegistrationStep3Form(forms.Form):
    position = forms.CharField(max_length=255,
                               min_length=5,
                               help_text='Optional: State your position. For example: teacher, student, scientist, etc..',
                               required=False)
    image = forms.ImageField(validators=[validate_image], 
                             required=False,
                             help_text='Optional.')
    

class RegistrationStep4Form(forms.Form):
    password = forms.CharField(min_length=8, widget=forms.PasswordInput())
    password_confirmation = forms.CharField(min_length=8, widget=forms.PasswordInput())


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            msg = 'Passwords do not match'
            self.add_error('password_confirmation', msg)

        return cleaned_data