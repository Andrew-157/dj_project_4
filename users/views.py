from django.shortcuts import render
from formtools.wizard.views import SessionWizardView


class RegistrationWizard(SessionWizardView):
    def done(self, form_list, **kwargs):
        return render(self.request, 'done.html',
                    {'form_data': [form.cleaned_data for form in form_list],
        })