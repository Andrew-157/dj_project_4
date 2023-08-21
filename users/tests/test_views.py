from django.contrib import auth
from django.contrib.messages import get_messages
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.test import TestCase

from users.models import CustomUser
from users.forms import LoginWithEmailForm


class RegisterViewTest(TestCase):

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_correct_objects_in_context(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue('wizard' in response.context)

    def test_register_with_invalid_username_data_first_step(self):
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'First Step',
                                          'First Step-username': 'shor',
                                          'First Step-email': 'new_user@gmail.com'}
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']
                         ['management_form']['current_step'].value(), 'First Step')
        username_error_message = b'Username cannot be shorter than 5 characters.'
        self.assertTrue(username_error_message in response.content)

    def test_register_with_invalid_email_data_first_step(self):
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'First Step',
                                          'First Step-username': 'new_user',
                                          'First Step-email': 'invalid'}
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']
                         ['management_form']['current_step'].value(), 'First Step')
        email_error_message = b'Enter a valid email address.'
        self.assertTrue(email_error_message in response.content)

    def test_register_with_not_unique_email_first_step(self):
        email = 'random@gmail.com'
        CustomUser.objects.create_user(username='random_user',
                                       email=email,
                                       password='34somepassword34')
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'First Step',
                                          'First Step-username': 'new_user',
                                          'First Step-email': email})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['management_form']['current_step'].value(),
                         'First Step')
        error_message = b'A user with this email already exists.'
        self.assertTrue(error_message in response.content)

    def test_register_with_valid_data_first_step(self):
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'First Step',
                                          'First Step-username': 'new_user',
                                          'First Step-email': 'new_user@gmail.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['management_form']['current_step'].value(),
                         'Second Step')

    def test_register_with_invalid_first_name_second_step(self):
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'First Step',
                               'First Step-username': 'new_user',
                               'First Step-email': 'new_user@gmail.com'}
                         )
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'Second Step',
                                          'Second Step-first_name': 'Jo',
                                          'Second Step-last_name': 'Doe'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['management_form']['current_step'].value(),
                         'Second Step')
        error_message = b'First Name cannot be shorter than 3 characters.'
        self.assertTrue(error_message in response.content)

    def test_register_with_invalid_last_name_second_step(self):
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'First Step',
                               'First Step-username': 'new_user',
                               'First Step-email': 'new_user@gmail.com'})
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'Second Step',
                                          'Second Step-first_name': 'John',
                                          'Second Step-last_name': 'Do'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['management_form']['current_step'].value(),
                         'Second Step')
        error_message = b'Last Name cannot be shorter than 3 characters.'
        self.assertTrue(error_message in response.content)

    def test_register_with_valid_data_second_step(self):
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'First Step',
                               'First Step-username': 'new_user',
                               'First Step-email': 'new_user@gmail.com'})
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'Second Step',
                                          'Second Step-first_name': 'John',
                                          'Second Step-last_name': 'Doe'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['management_form']['current_step'].value(),
                         'Third Step')

    def test_register_with_invalid_position_third_step(self):
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'First Step',
                               'First Step-username': 'new_user',
                               'First Step-email': 'new_user@gmail.com'})
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'Second Step',
                               'Second Step-first_name': 'John',
                               'Second Step-last_name': 'Doe'})
        invalid_position = 'gh'
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'Third Step',
                                          'Third Step-position': invalid_position})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['management_form']['current_step'].value(),
                         'Third Step')
        error_message = f'Ensure this value has at least 3 characters (it has {len(invalid_position)}).'
        self.assertTrue(error_message.encode(
            encoding="utf-8") in response.content)

    def test_register_with_valid_data_third_step(self):
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'First Step',
                               'First Step-username': 'new_user',
                               'First Step-email': 'new_user@gmail.com'})
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'Second Step',
                               'Second Step-first_name': 'John',
                               'Second Step-last_name': 'Doe'})
        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'Third Step',
                                          'Third Step-position': 'Computer Science Student'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['management_form']['current_step'].value(),
                         'Fourth Step')

    def test_register_with_invalid_data_fourth_step(self):
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'First Step',
                               'First Step-username': 'new_user',
                               'First Step-email': 'new_user@gmail.com'})
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'Second Step',
                               'Second Step-first_name': 'John',
                               'Second Step-last_name': 'Doe'})
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'Third Step',
                               'Third Step-position': 'Computer Science Student'})

        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'Fourth Step',
                                          'Fourth Step-password1': 'tuioiuytyuiouy',
                                          'Fourth Step-password2': 'yguhijokiuyjk'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['management_form']['current_step'].value(),
                         'Fourth Step')

    def test_successful_registration(self):
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'First Step',
                               'First Step-username': 'new_user',
                               'First Step-email': 'new_user@gmail.com'})
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'Second Step',
                               'Second Step-first_name': 'John',
                               'Second Step-last_name': 'Doe'})
        self.client.post(reverse('users:register'),
                         data={'registration_wizard-current_step': 'Third Step',
                               'Third Step-position': 'Computer Science Student'})

        response = self.client.post(reverse('users:register'),
                                    data={'registration_wizard-current_step': 'Fourth Step',
                                          'Fourth Step-password1': '34somepassword34',
                                          'Fourth Step-password2': '34somepassword34'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:index'))
        self.assertEqual(str(messages[0]), 'You successfully registered.')
        new_user = CustomUser.objects.filter(username='new_user').first()
        self.assertTrue(new_user is not None)


class LoginTemplateViewTest(TestCase):

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login_links.html')


class LoginWithUsernameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        CustomUser.objects.create_user(
            username='new_user',
            email='new_user@gmail.com',
            password='34somepassword34')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('users:login-username'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_correct_objects_in_context(self):
        response = self.client.get(reverse('users:login-username'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertEqual(response.context['form'].__class__,
                         AuthenticationForm)
        self.assertTrue('username' in response.context)

    def test_correct_response_if_login_failed(self):
        response = self.client.post(reverse('users:login-username'),
                                    data={'username': 'new_user',
                                          'password': 'wrongpassword34'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_successful_login(self):
        response = self.client.post(reverse('users:login-username'),
                                    data={'username': 'new_user',
                                          'password': '34somepassword34'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Welcome Back")
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'new_user')


class LoginWithEmailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        CustomUser.objects.create_user(username='new_user',
                                       email='new_user@gmail.com',
                                       password='34somepassword34')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('users:login-email'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_correct_objects_in_context(self):
        response = self.client.get(reverse('users:login-email'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertEqual(
            response.context['form'].__class__, LoginWithEmailForm)
        self.assertTrue('email' in response.context)

    def test_correct_response_if_login_failed(self):
        response = self.client.post(reverse('users:login-email'),
                                    data={'username': 'new_user@gamil.com',
                                          'password': 'dfghjkccfghg'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        error_message = b"Please enter a correct email and password. Note that both fields may be case-sensitive."
        self.assertTrue(error_message in response.content)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_successful_login(self):
        response = self.client.post(reverse('users:login-email'),
                                    data={'username': 'new_user@gmail.com',
                                          'password': '34somepassword34'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Welcome Back")
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.email, 'new_user@gmail.com')
