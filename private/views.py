from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View


class PrivatePageView(View):
    template_name = 'private/private_page.html'

    def get(self, request):
        return render(request, self.template_name)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
