from django.urls import path
from django.views.generic import TemplateView

from users import views

app_name = 'users'


urlpatterns = [
    path('register/', views.RegistrationWizard.as_view(
        views.REGISTRATION_WIZARD_FORMS), name='register'),
    path('login/username/', views.LoginWithUsernameView.as_view(),
         name='login-username'),
    path('login/email', views.LoginWithEmailView.as_view(), name='login-email'),
    path('login/', TemplateView.as_view(template_name='users/login_links.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('authenticate/',
         TemplateView.as_view(template_name='users/become_user.html'), name='become-user'),
    path('profile/update', views.ChangeUserView.as_view(), name='change-user')
]
