from django.urls import path, register_converter

from private import views
from private.views import UUIDConverter

register_converter(UUIDConverter, 'uuid')

app_name = 'private'


urlpatterns = [
    path('you/', views.PrivatePageView.as_view(), name='private-page'),
    path('you/publish/', views.PostArticleView.as_view(), name='post-article'),
    path('you/articles/<uuid:id>/',
         views.ArticleDetailView.as_view(), name='article-detail')
]
