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
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
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
from core.models import Article, Section, Tag


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

    def parse_tags(self, tags_str: str) -> list[str]:
        result = []
        splitted_tags_str = tags_str.split(',')
        for tag in splitted_tags_str:
            if not tag:
                continue
            elif tag.isspace():
                continue
            else:
                result.append(tag.strip())

        return result

    def get_tags_objects(self, tags_str: str) -> list[Tag]:
        tag_objects = []
        tags_str_list = self.parse_tags(tags_str=tags_str)
        for tag in tags_str_list:
            tag = '-'.join(tag.split(' ')).lower()
            tag_object = Tag.objects.filter(name=tag).first()
            if tag_object:
                tag_objects.append(tag_object)
            else:
                tag_object = Tag(name=tag)
                tag_object.save()
                tag_objects.append(tag_object)

        return tag_objects

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        self.object: Article = form.save()
        tag_objects = self.get_tags_objects(
            tags_str=self.request.POST['tags_string'])
        self.object.tags.set(tag_objects)
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
            select_related('author', 'category').\
            filter(
                id=self.kwargs['id']).first()
        if not article:
            raise Http404
        return article

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        object: Article = self.get_object()
        if object.author != request.user:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)


class UpdateArticleBase(LoginRequiredMixin, View):
    template_name = 'private/update_article.html'
    form_class = CreateUpdateArticleForm
    redirect_to = ''
    send_post_to = ''
    info_message = """You cannot update article while its status is "Ready"."""
    success_message = 'You successfully updated your article.'

    def get_redirect_url(self):
        if self.redirect_to == 'private:article-detail':
            return reverse('private:article-detail', kwargs={'id': self.article.id})
        elif self.redirect_to == 'private:article-list':
            return reverse('private:article-list')

    def get_object(self):
        article = Article.objects.\
            filter(id=self.kwargs['id']).\
            select_related('author').first()
        if article.author != self.request.user:
            raise PermissionDenied
        self.article = article
        return article

    def parse_tags(self, tags_str: str) -> list[str]:
        result = []
        splitted_tags = tags_str.split(',')
        for tag in splitted_tags:
            if tag.isspace():
                continue
            elif not tag:
                continue
            else:
                result.append(tag.strip())

        return result

    def get_tags_objects(self, tags_str: str) -> list[Tag]:
        tag_objects = []
        tags_str_list = self.parse_tags(tags_str=tags_str)
        for tag in tags_str_list:
            tag = tag.replace(' ', '-').lower()
            tag_object = Tag.objects.filter(name=tag).first()
            if tag_object:
                tag_objects.append(tag_object)
            else:
                tag_object = Tag(name=tag)
                tag_object.save()
                tag_objects.append(tag_object)

        return tag_objects

    def get(self, request, *args, **kwargs):
        article = self.get_object()
        if article.is_ready == True:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(self.get_redirect_url())
        tags_string = ', '.join([tag.name for tag in article.tags.all()])
        form = self.form_class(
            instance=article, initial={'tags_string': tags_string})
        context = {'article': article,
                   'form': form,
                   'send_post_to': self.send_post_to}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        if article.is_ready == True:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(self.get_redirect_url())
        form = self.form_class(request.POST, instance=article)
        if form.is_valid():
            obj: Article = form.save()
            tag_objects = self.get_tags_objects(
                tags_str=self.request.POST['tags_string'])
            obj.tags.set(tag_objects)
            messages.success(request, self.success_message)
            return HttpResponseRedirect(self.get_redirect_url())
        context = {'article': article,
                   'form': form,
                   'send_post_to': self.send_post_to}
        return render(request, self.template_name, context=context)


class UpdateArticleThroughArticleList(UpdateArticleBase):
    redirect_to = 'private:article-list'
    send_post_to = 'private:update-article-through-list'


class UpdateArticleThroughArticleDetail(UpdateArticleBase):
    redirect_to = 'private:article-detail'
    send_post_to = 'private:update-article-through-detail'


class DeleteArticleView(LoginRequiredMixin, DeleteView):
    http_method_names = ['post']
    success_url = reverse_lazy('private:article-list')

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
    allowed_orderings = ['sections', '-sections', 'published', '-published']

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        ordering = self.request.GET.get('ordering')
        if ordering and ordering not in self.allowed_orderings:
            return HttpResponseBadRequest()
        self.ordering = ordering
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Article.objects.\
            filter(author=self.request.user).\
            select_related('category').\
            prefetch_related('tags').all().\
            annotate(sections_number=Count('sections'))
        ordering = self.ordering
        if not ordering:
            return queryset.order_by('-id')
        else:
            return queryset.order_by(ordering)


class PostSectionView(LoginRequiredMixin, View):
    template_name = 'private/post_section.html'
    form_class = CreateUpdateSectionForm
    info_message = 'You cannot post new section for article while its status is "Ready".'

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
        if article.is_ready == True:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(reverse('private:article-detail',
                                                kwargs={'id': article.id}))
        form = self.form_class()
        context = {'form': form,
                   'article': article}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, *args, **kwargs):
        article = get_object_or_404(Article, id=self.kwargs['id'])
        if article.author != request.user:
            raise PermissionDenied
        if article.is_ready == True:
            messages.info(request, self.info_message)
            return HttpResponseRedirect(reverse('private:article-detail',
                                                kwargs={'id': article.id}))
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
    info_message = """You cannot update a section while article's status is "Ready"."""

    def get_section(self, article: Article, slug: str) -> Http404 | Section:
        section = Section.objects.filter(
            Q(article=article) &
            Q(slug=slug)
        ).first()
        if not section:
            raise Http404
        else:
            return section

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
        section = self.get_section(article=article, slug=self.kwargs['slug'])
        if article.is_ready == True:
            messages.info(self.request, self.info_message)
            return HttpResponseRedirect(reverse('private:article-detail',
                                                kwargs={'id': article.id}))
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
        section = self.get_section(article=article, slug=self.kwargs['slug'])
        if article.is_ready == True:
            messages.info(self.request, self.info_message)
            return HttpResponseRedirect(reverse('private:article-detail',
                                                kwargs={'id': article.id}))
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

    def form_valid(self, form):
        success_url = self.get_success_url()
        if self.article.is_ready == True:
            messages.info(
                self.request, """You cannot delete a section while article's status is "Ready".""")
            return HttpResponseRedirect(success_url)
        self.object.delete()
        messages.success(
            self.request, 'You successfully deleted a section for the article.')
        return HttpResponseRedirect(success_url)

    def get_object(self):
        article_id = self.kwargs['id']
        section_slug = self.kwargs['slug']
        article = Article.objects.filter(id=article_id).first()
        if not article:
            raise Http404
        if article.author != self.request.user:
            raise PermissionDenied
        self.article = article
        section = Section.objects.filter(
            Q(slug=section_slug) &
            Q(article=article)
        ).first()
        return section


class SetArticleStatusBase(LoginRequiredMixin, View):
    http_method_names = ['post']

    def sections_numbers_has_1(self, sections: list[Section]):
        numbers_of_sections = [section.number for section in sections]

        if 1 not in numbers_of_sections:
            return False
        return True

    def sections_numbers_are_consecutive_integers(self, sections: list[Section]):
        numbers_of_sections = [section.number for section in sections]
        numbers_of_sections = sorted(numbers_of_sections)

        first_number = numbers_of_sections[0]
        last_number = numbers_of_sections[-1]

        expected_numbers = []
        expected_numbers.append(first_number)

        while first_number != last_number:
            first_number += 1
            expected_numbers.append(first_number)

        if expected_numbers != numbers_of_sections:
            return False
        return True

    def get_redirect_url(self) -> HttpResponseRedirect:
        pass

    def post(self, request: HttpRequest, *args, **kwargs):
        current_user = request.user
        article = get_object_or_404(Article, id=self.kwargs['id'])
        if article.author != current_user:
            raise PermissionDenied
        self.article = article
        if article.is_ready == False:
            # If status 'Not Ready', then it means user wants to
            # change it to 'Ready' and some checks will we done
            sections: list[Section] = article.sections.all()
            if not sections:
                messages.info(request,
                              message='Create at least one section before setting status to "Ready".')
                return self.get_redirect_url()
            if not self.sections_numbers_has_1(sections=sections):
                messages.info(
                    request,
                    message='Make sure that there is a section with number 1 among sections of this article.'
                )
                return self.get_redirect_url()
            if not self.sections_numbers_are_consecutive_integers(sections=sections):
                messages.info(
                    request,
                    message='Make sure numbers of your sections are consecutive integers.'
                )
                return self.get_redirect_url()
            article.is_ready = True
            article.save()
            messages.success(
                request, message="Now article will be shown to others.")
            return self.get_redirect_url()
        if article.is_ready == True:
            article.is_ready = False
            article.save()
            messages.success(
                request, message="Now article won't be shown to other users and you can modify it.")
            return self.get_redirect_url()


class SetArticleStatusThroughArticleDetailView(SetArticleStatusBase):

    def get_redirect_url(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(reverse('private:article-detail',
                                            kwargs={'id': self.article.id}))


class SetArticleStatusThroughArticleListView(SetArticleStatusBase):

    def get_redirect_url(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(reverse('private:article-list'))


@login_required
@require_http_methods(request_method_list=['GET'])
def search_for_articles(request: HttpRequest):
    query = request.GET.get('query')
    if not query:
        return redirect('private:article-list')
    current_user = request.user
    articles = Article.objects.\
        filter(
            Q(title__icontains=query) &
            Q(author=current_user)).\
        select_related('category').prefetch_related('tags').all().\
        order_by('-published')
    return render(request, 'private/search_results.html',
                  context={'articles': articles,
                           'query': query})
