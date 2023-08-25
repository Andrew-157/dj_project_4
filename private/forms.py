from django import forms

from core.models import Article


class CreateArticleForm(forms.ModelForm):
    fields = forms.CharField(help_text='Some text',
                             max_length=255,
                             min_length=5)

    class Meta:
        model = Article
        fields = ['title', 'category']
