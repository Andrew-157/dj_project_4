from typing import Any, Dict, Optional
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.urls import converters
from django.http import HttpResponseForbidden
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from private.forms import CreateArticleForm
from core.models import Article


class UUIDConverter(converters.StringConverter):
    regex = '[0-9a-f-]+'


class PrivatePageView(View):
    template_name = 'private/private_page.html'

    def get(self, request):
        return render(request, self.template_name)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PostArticleView(LoginRequiredMixin, CreateView):
    template_name = 'private/publish_article.html'
    form_class = CreateArticleForm
    model = Article

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        self.object = form.save()
        messages.success(
            self.request, 'Great! You posted new article. Now add some sections to it.')
        return HttpResponseRedirect(reverse('private:article-detail',
                                            kwargs={'id': self.object.id}))


class ArticleDetailView(LoginRequiredMixin, DetailView):
    template_name = 'private/article_detail.html'
    context_object_name = 'article'

    def get_object(self):
        # Getting object like this is necessary because default implementation
        # does not understand uuid as id
        article = Article.objects.\
            select_related('author', 'category').filter(
                id=self.kwargs['id']).first()
        if not article:
            raise Http404
        return article

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        object: Article = self.get_object()
        if object.author != request.user:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)


class UpdateArticleView(LoginRequiredMixin, UpdateView):
    template_name = 'private/update_article.html'
    form_class = CreateArticleForm

    def get_object(self):
        article = get_object_or_404(Article, id=self.kwargs['id'])
        if article.author != self.request.user:
            raise PermissionDenied
        return article

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object: Article = form.save()
        messages.success(
            self.request, 'You successfully updated your article!')
        return HttpResponseRedirect(reverse('private:article-detail',
                                            kwargs={'id': self.object.id}))

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['article'] = self.object
        return context


class DeleteArticleView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('private:private-page')

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        messages.success(request, 'You successfully deleted your article!')
        return super().post(request, *args, **kwargs)

    def get_object(self):
        article = Article.objects.\
            select_related('author', 'category').filter(
                id=self.kwargs['id']).first()
        if not article:
            raise Http404
        if article.author != self.request.user:
            raise PermissionDenied
        return article


class ArticleListView(LoginRequiredMixin, ListView):
    template_name = 'private/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self) -> QuerySet[Any]:
        return Article.objects.\
            filter(author=self.request.user).\
            select_related('category').all().\
            annotate(sections_number=Count('sections'))
