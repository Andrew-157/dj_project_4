from typing import Any, Dict, Mapping, Optional, Type, Union
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList

from core.models import Article, Section


class CreateUpdateArticleForm(forms.ModelForm):
    title = forms.CharField(help_text="Title may be something like this: Ionic compounds' role in nutrition.",
                            max_length=255,
                            min_length=5,
                            widget=forms.TextInput(attrs={'placeholder': 'Enter title for your article'}))
    tags_string = forms.CharField(help_text="Enter tags, separating them with comma.#-sign is not necessary.",
                                  max_length=500,
                                  min_length=2,
                                  label='Tags', required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Enter some tags'}))

    class Meta:
        model = Article
        fields = ['title', 'category', 'tags_string']


class CreateUpdateSectionForm(forms.ModelForm):

    number = forms.IntegerField(
        min_value=1
    )

    class Meta:
        model = Section
        fields = ['title', 'number', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter title of the section'}),
            'content': forms.Textarea(attrs={'placeholder': 'Enter content of the section'})
        }
