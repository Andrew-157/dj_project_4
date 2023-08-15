from django.urls import path
from django.views.generic import TemplateView

from users import views

app_name = 'users'


urlpatterns = [
    path('register/', views.RegistrationWizard.as_view(), name='register'),
    path('login/username/', views.LoginWithUsernameView.as_view(),
         name='login-username'),
    path('login/email', views.LoginWithEmailView.as_view(), name='login-email'),
    path('login/', TemplateView.as_view(template_name='users/login_links.html'), name='login')
]
