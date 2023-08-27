from typing import Any, Dict, Optional
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
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
from django.forms import Form

from private.forms import CreateUpdateArticleForm, CreateUpdateSectionForm
from core.models import Article, Section


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
    form_class = CreateUpdateArticleForm
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
    form_class = CreateUpdateArticleForm

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


class PostSectionView(LoginRequiredMixin, View):
    template_name = 'private/post_section.html'
    form_class = CreateUpdateSectionForm

    def get_article(self, id):
        article = Article.objects.filter(id=id).first()
        # return get_object_or_404(Article, id=id)
        if not article:
            raise Http404
        return article

    def add_error_if_section_number_is_not_unique(self, form_data, article, form: Form):
        numbers_of_sections = [
            section.number for section in article.sections.all()]
        section_number = int(form_data['number'][0])
        if section_number in numbers_of_sections:
            form.add_error(
                'number', f'Article already has section with number {section_number}.')

    def get(self, request, *args, **kwargs):
        article = self.get_article(kwargs['id'])
        if article.author != self.request.user:
            raise PermissionDenied
        form = self.form_class()
        context = {'form': form,
                   'article': article}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, *args, **kwargs):
        article = self.get_article(kwargs['id'])
        if article.author != request.user:
            raise PermissionDenied
        form = self.form_class(request.POST)
        self.add_error_if_section_number_is_not_unique(form_data=request.POST,
                                                       article=article,
                                                       form=form)
        if form.is_valid():
            form.instance.article = article
            form.save()
            messages.success(
                request, 'You successfully added new section to your article!')
            return HttpResponseRedirect(reverse('private:article-detail', kwargs={'id': article.id}))
        context = {'form': form,
                   'article': article}
        return render(request, self.template_name, context=context)


class SectionDetail(LoginRequiredMixin, DetailView):
    template_name = 'private/section_detail.html'
    context_object_name = 'section'

    def get_object(self):
        article_id = self.kwargs['id']
        section_slug = self.kwargs['slug']
        article = Article.objects.filter(id=article_id).first()
        if not article:
            raise Http404
        if article.author != self.request.user:
            raise PermissionDenied
        sections: list[Section] = article.sections.all()
        sections_slugs = [section.slug for section in sections]
        if section_slug not in sections_slugs:
            raise Http404
        self.article = article

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['article'] = self.article
        return context
