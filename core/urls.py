from django.urls import path
from django.views.generic import TemplateView
from core import views


app_name = 'core'

urlpatterns = [
    path('', TemplateView.as_view(template_name='core/index.html'), name='index')
]