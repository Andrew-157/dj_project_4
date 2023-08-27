from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from django.http import HttpResponseNotAllowed

from core.models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title'
    ]
    list_filter = ['title']
    search_fields = ['title']
