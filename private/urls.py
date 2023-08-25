from django.urls import path

from private import views

app_name = 'private'


urlpatterns = [
    path('you/', views.PrivatePageView.as_view(), name='private-page'),
    path('publish/', views.PostArticleView.as_view(), name='post-article')
]
