from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView
from django.views.generic.edit import CreateView, DeleteView

from private.forms import CreateArticleForm
from core.models import Article


class PrivatePageView(View):
    template_name = 'private/private_page.html'

    def get(self, request):
        return render(request, self.template_name)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PostArticleView(LoginRequiredMixin, CreateView):
    template_name = 'private/publish_article.html'
    form_class = CreateArticleForm
    success_url = reverse_lazy('private:private-page')
    model = Article

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        messages.success(
            self.request, 'Great! You posted new article. Now add some sections to it.')
        return super().form_valid(form)
