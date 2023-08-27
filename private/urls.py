from django.urls import path, register_converter

from private import views
from private.views import UUIDConverter

register_converter(UUIDConverter, 'uuid')

app_name = 'private'


urlpatterns = [
    path('you/', views.PrivatePageView.as_view(), name='private-page'),
    path('you/publish/', views.PostArticleView.as_view(), name='post-article'),
    path('you/articles/<uuid:id>/',
         views.ArticleDetailView.as_view(), name='article-detail'),
    path('you/articles/<uuid:id>/update/',
         views.UpdateArticleView.as_view(), name='update-article'),
    path('you/article/<uuid:id>/delete/',
         views.DeleteArticleView.as_view(), name='delete-article'),
    path('you/articles/', views.ArticleListView.as_view(), name='article-list'),
    path('you/articles/<uuid:id>/sections/publish/', views.PostSectionView.as_view(),
         name='post-section'),
    path('you/articles/<uuid:id>/sections/<str:slug>/', views.SectionDetail.as_view(),
         name='section-detail')
]