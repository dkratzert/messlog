from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('scxrd:index')
    template_name = 'registration/new_user.html'


class OptionsView(TemplateView):
    """
    Show details of an experiment

    TODO: Make real options page
    """
    template_name = 'registration/options.html'
    success_url = '/'
