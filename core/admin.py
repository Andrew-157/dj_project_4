from django.contrib import admin

from core.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title'
    ]
    list_filter = ['title']
    search_fields = ['title']
