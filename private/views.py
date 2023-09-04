from typing import Any, Dict, Optional, Type
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models.query_utils import Q
from django.db.models import Count
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.urls import converters
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.forms import Form
from django.http import HttpRequest

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
        object: Article = form.save()
        messages.success(
            self.request, 'You successfully updated your article!')
        return HttpResponseRedirect(reverse('private:article-detail',
                                            kwargs={'id': object.id}))

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        article = self.get_object()
        self.object = article
        if article.is_ready == True:
            messages.info(
                request, "You cannot update article while it's status is 'Ready'.")
            return HttpResponseRedirect(reverse('private:article-detail',
                                                kwargs={'id': article.id}))
        return self.render_to_response(self.get_context_data())

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        article = self.get_object()
        self.object = article
        if article.is_ready == True:
            messages.info(
                request, "You cannot update article while it's status is 'Ready'.")
            return HttpResponseRedirect(reverse('private:article-detail',
                                                kwargs={'id': article.id}))
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class DeleteArticleView(LoginRequiredMixin, DeleteView):
    http_method_names = ['post']
    success_url = reverse_lazy('private:private-page')

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        messages.success(request, 'You successfully deleted your article!')
        return super().post(request, *args, **kwargs)

    def get_object(self):
        article = Article.objects.filter(id=self.kwargs['id']).first()
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

    def add_error_if_section_number_is_not_unique(self, form_data, article, form: Form):
        sections: list[Section] = article.sections.all()
        numbers_of_sections = [
            section.number for section in sections]
        section_number = int(form_data['number'][0])
        if section_number in numbers_of_sections:
            form.add_error(
                'number', f'Article already has section with number {section_number}.')

    def add_error_if_not_unique_title_for_section(self, form_data, article, form: Form):
        sections: list[Section] = article.sections.all()
        titles_of_sections = [section.title for section in sections]
        section_title = form_data['title']
        if section_title in titles_of_sections:
            form.add_error(
                'title', f'Article already has section with this title.'
            )

    def get(self, request, *args, **kwargs):
        article = get_object_or_404(Article, id=self.kwargs['id'])
        if article.author != self.request.user:
            raise PermissionDenied
        form = self.form_class()
        context = {'form': form,
                   'article': article}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, *args, **kwargs):
        article = get_object_or_404(Article, id=self.kwargs['id'])
        if article.author != request.user:
            raise PermissionDenied
        form = self.form_class(request.POST)
        self.add_error_if_section_number_is_not_unique(form_data=request.POST,
                                                       article=article,
                                                       form=form)
        self.add_error_if_not_unique_title_for_section(form_data=request.POST,
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


class SectionDetailView(LoginRequiredMixin, DetailView):
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
        section = Section.objects.filter(
            Q(slug=section_slug) &
            Q(article=article)
        ).first()
        return section

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['article'] = self.article
        return context


class UpdateSectionBase(LoginRequiredMixin, View):
    redirect_to = ''
    send_post_to = ''
    template_name = 'private/update_section.html'
    form_class = CreateUpdateSectionForm
    success_message = 'You successfully updated a section!'

    def get_section(self, article: Article, slug: str):
        return Section.objects.filter(
            Q(article=article) &
            Q(slug=slug)
        ).first()

    def add_error_if_not_unique_number_for_section(self, form_data, article: Article, form: Form, section: Section):
        sections: list[Section] = article.sections.all()
        numbers_of_sections = [
            section.number for section in sections]
        numbers_of_sections.remove(section.number)
        section_number = int(form_data['number'][0])
        if (section_number in numbers_of_sections):
            form.add_error(
                'number', f'Article already has section with number {section_number}.')

    def add_error_if_not_unique_title_for_section(self, form_data, article: Article, form: Form, section: Section):
        sections: list[Section] = article.sections.all()
        titles_of_sections = [
            section.title for section in sections]
        titles_of_sections.remove(section.title)
        section_title = form_data['title']
        if (section_title in titles_of_sections):
            form.add_error(
                'title', f'Article already has section with this title.'
            )

    def get(self, request, *args, **kwargs):
        article = get_object_or_404(Article, id=self.kwargs['id'])
        current_user = self.request.user
        if article.author != current_user:
            raise PermissionDenied
        section_slug = self.kwargs['slug']
        sections: list[Section] = article.sections.all()
        sections_slugs = [section.slug for section in sections]
        if section_slug not in sections_slugs:
            raise Http404
        section = self.get_section(article=article, slug=self.kwargs['slug'])
        form = self.form_class(instance=section)
        context = {'article': article,
                   'form': form,
                   'section': section,
                   'send_post_to': self.send_post_to}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, id=self.kwargs['id'])
        current_user = self.request.user
        if article.author != current_user:
            raise PermissionDenied
        section_slug = self.kwargs['slug']
        sections: list[Section] = article.sections.all()
        sections_slugs = [section.slug for section in sections]
        if section_slug not in sections_slugs:
            raise Http404
        section = self.get_section(article=article, slug=self.kwargs['slug'])
        form = self.form_class(request.POST, instance=section)
        self.add_error_if_not_unique_number_for_section(form_data=request.POST,
                                                        article=article,
                                                        form=form,
                                                        section=section)
        self.add_error_if_not_unique_title_for_section(form_data=request.POST,
                                                       article=article,
                                                       form=form,
                                                       section=section)
        if form.is_valid():
            form.save()
            messages.success(request, self.success_message)
            if self.redirect_to == 'private:section-detail':
                return HttpResponseRedirect(reverse('private:section-detail',
                                                    kwargs={'id': article.id,
                                                            'slug': section.slug}))
            if self.redirect_to == 'private:article-detail':
                return HttpResponseRedirect(reverse('private:article-detail',
                                                    kwargs={'id': article.id}))
        context = {'article': article,
                   'form': form,
                   'section': section,
                   'send_post_to': self.send_post_to}
        return render(request, self.template_name, context=context)


class UpdateSectionThroughArticleDetailView(UpdateSectionBase):
    redirect_to = 'private:article-detail'
    send_post_to = 'private:update-section-article-detail'


class UpdateSectionThroughSectionDetailView(UpdateSectionBase):
    redirect_to = 'private:section-detail'
    send_post_to = 'private:update-section-section-detail'


class DeleteSectionView(LoginRequiredMixin, DeleteView):
    http_method_names = ['post']

    def get_success_url(self) -> str:
        article = self.article
        success_url = reverse('private:article-detail',
                              kwargs={
                                  'id': article.id})
        return success_url

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        messages.success(
            request, 'You successfully deleted a section for the article.')
        return super().post(request, *args, **kwargs)

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
        section = Section.objects.filter(
            Q(slug=section_slug) &
            Q(article=article)
        ).first()
        return section


@login_required
@require_http_methods(request_method_list=['POST'])
def set_article_status(request: HttpRequest, id):
    article = get_object_or_404(Article, id=id)
    current_user = request.user
    if article.author != current_user:
        raise PermissionDenied
    if article.is_ready == True:
        article.is_ready = False
        success_message = "Now article won't be shown to other users and you can modify it."
    elif article.is_ready == False:
        article.is_ready = True
        success_message = "Now article will be shown to others."
    article.save()
    messages.success(request, success_message)
    return HttpResponseRedirect(reverse('private:article-detail',
                                        kwargs={'id': article.id}))
