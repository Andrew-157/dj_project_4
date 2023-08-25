from django import forms

from core.models import Article


class CreateArticleForm(forms.ModelForm):
    title = forms.CharField(help_text="Title may be something like this: Ionic compounds' role in nutrition.",
                            max_length=255,
                            min_length=5)

    class Meta:
        model = Article
        fields = ['title', 'category']
