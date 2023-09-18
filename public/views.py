from typing import Any
from django.views.generic import ListView
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count
from django.urls import converters

from core.models import Category


class UUIDConverter(converters.StringConverter):
    regex = '[0-9a-f-]+'


class ArticlesByCategoryView(ListView):
    template_name = 'public/articles_by_category.html'
    context_object_name = 'articles'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        category = get_object_or_404(Category, id=self.kwargs['id'])
        self.category = category
        return super().get(request, *args, **kwargs)
