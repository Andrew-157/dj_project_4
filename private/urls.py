from django.urls import path, register_converter
from django.views.generic import TemplateView

from private import views
from private.views import UUIDConverter

register_converter(UUIDConverter, 'uuid')

app_name = 'private'


urlpatterns = [
    path('you/', views.PrivatePageView.as_view(), name='private-page'),
    path('you/publish/', views.PostArticleView.as_view(), name='post-article'),
    path('you/articles/<uuid:id>/',
         views.ArticleDetailView.as_view(), name='article-detail'),
    path('you/articles/<uuid:id>/update/list/',
         views.UpdateArticleThroughArticleList.as_view(), name='update-article-through-list'),
    path('you/articles/<uuid:id>/update/detail/', views.UpdateArticleThroughArticleDetail.as_view(),
         name='update-article-through-detail'),
    path('you/article/<uuid:id>/delete/',
         views.DeleteArticleView.as_view(), name='delete-article'),
    path('you/articles/', views.ArticleListView.as_view(), name='article-list'),
    path('you/articles/<uuid:id>/sections/publish/', views.PostSectionView.as_view(),
         name='post-section'),
    path('you/articles/<uuid:id>/sections/<str:slug>/', views.SectionDetailView.as_view(),
         name='section-detail'),
    path('guide/', TemplateView.as_view(template_name='private/guide.html'), name='guide'),
    path('you/articles/<uuid:id>/sections/<str:slug>/update/article/',
         views.UpdateSectionThroughArticleDetailView.as_view(), name='update-section-article-detail'),
    path('you/articles/<uuid:id>/sections/<str:slug>/update/section/',
         views.UpdateSectionThroughSectionDetailView.as_view(), name='update-section-section-detail'),
    path('you/articles/<uuid:id>/sections/<str:slug>/delete/', views.DeleteSectionView.as_view(),
         name='delete-section'),
    path('you/articles/<uuid:id>/set_status/detail/', views.SetArticleStatusThroughArticleDetailView.as_view(),
         name='set-article-status-through-detail'),
    path('you/articles/<uuid:id>/set_status/list/', views.SetArticleStatusThroughArticleListView.as_view(),
         name='set-article-status-through-list'),
    path('you/articles/search/', views.search_for_articles, name='search-articles'),
]
