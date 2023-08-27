from typing import Any, Optional
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.urls import converters
from django.http import HttpResponseForbidden
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView, DetailView
from django.views.generic.edit import CreateView, DeleteView
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
    success_url = reverse_lazy('private:article-detail',
                               )
    model = Article

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        self.object = form.save()
        messages.success(
            self.request, 'Great! You posted new article. Now add some sections to it.')
        return HttpResponseRedirect(reverse('private:article-detail',
                                            kwargs={'id': self.object.id}))


class ArticleDetailView(LoginRequiredMixin, DetailView):
    queryset = Article.objects.select_related('author', 'category').all()
    template_name = 'private/article_detail.html'
    context_object_name = 'article'

    def get_object(self):
        return get_object_or_404(Article, id=self.kwargs['id'])

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        object: Article = self.get_object()
        if object.author != request.user:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)
