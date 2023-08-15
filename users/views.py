from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.forms import Form
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from formtools.wizard.views import SessionWizardView
from django.http.request import HttpRequest

from users.models import CustomUser
from users.forms import RegistrationStep1Form, RegistrationStep2Form, RegistrationStep3Form, \
    RegistrationStep4Form, LoginWithEmailForm, UserChangeForm


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
        login(self.request, new_user,
              backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, 'You successfully registered.')
        return redirect('core:index')


class LoginWithUsernameView(View):
    template_name = 'users/login.html'
    form_class = AuthenticationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name,
                      {'form': form,
                       'username': True})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Welcome Back')
                return redirect('core:index')
        return render(request, self.template_name, {'form': form,
                                                    'username': True})


class LoginWithEmailView(View):
    template_name = 'users/login.html'
    form_class = LoginWithEmailForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form,
                                                    'email': True})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Welcome back')
                return redirect('core:index')
        return render(request, self.template_name, {'form': form,
                                                    'email': True})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect('core:index')


class ChangeUserView(View):
    template_name = 'users/change_user.html'
    form_class = UserChangeForm

    def get(self, request: HttpRequest, *args, **kwargs):
        current_user = request.user
        form = self.form_class(instance=current_user)
        return render(request, self.template_name, {'form': form})

    def post(self, request: HttpRequest, *args, **kwargs):
        current_user = request.user
        form = self.form_class(request.POST, instance=current_user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'You successfully updated your profile')
            return redirect('core:index')
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
