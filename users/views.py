from django.contrib import messages
from django.contrib.auth import login
from django.forms import Form
from django.shortcuts import render, redirect
from django.utils import timezone
from formtools.wizard.views import SessionWizardView

from users.models import CustomUser
from users.forms import RegistrationStep1Form, RegistrationStep2Form, RegistrationStep3Form, \
    RegistrationStep4Form


def process_form_data(form_list: list[Form]) -> CustomUser:
    form_step_1 = form_list[0]
    form_step_2 = form_list[1]
    form_step_3 = form_list[2]
    form_step_4 = form_list[3]
    username = form_step_1.cleaned_data['username']
    email = form_step_1.cleaned_data['email']
    first_name = form_step_2.cleaned_data['first_name']
    last_name = form_step_2.cleaned_data['last_name']
    position = form_step_3.cleaned_data['position']
    position = position if position else None
    password = form_step_4.cleaned_data['password1']

    new_user = CustomUser.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        position=position,
        password=password,
        last_login=timezone.now()
    )
    return new_user


class RegistrationWizard(SessionWizardView):
    template_name = 'users/register.html'
    form_list = [RegistrationStep1Form, RegistrationStep2Form,
                 RegistrationStep3Form, RegistrationStep4Form]

    def done(self, form_list, **kwargs):
        new_user = process_form_data(form_list)
        login(self.request, new_user)
        messages.success(self.request, 'You successfully registered.')
        return redirect('core:index')
