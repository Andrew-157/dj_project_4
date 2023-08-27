from typing import Any, Dict
from django import forms

from core.models import Article, Section


class CreateUpdateArticleForm(forms.ModelForm):
    title = forms.CharField(help_text="Title may be something like this: Ionic compounds' role in nutrition.",
                            max_length=255,
                            min_length=5)

    class Meta:
        model = Article
        fields = ['title', 'category']


class CreateUpdateSectionForm(forms.ModelForm):

    number = forms.IntegerField(
        min_value=1
    )

    class Meta:
        model = Section
        fields = ['title', 'number', 'content']
