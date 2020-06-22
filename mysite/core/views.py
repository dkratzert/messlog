from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView

from mysite.core.forms import UserChangeForm


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('scxrd:index')
    template_name = 'registration/new_user.html'


class UserEdit(UpdateView):
    form_class = UserChangeForm
    success_url = reverse_lazy('scxrd:index')
    model = User
    template_name = 'registration/edit_user.html'


class OptionsView(TemplateView):
    """
    Show details of an experiment

    TODO: Make real options page
    """
    template_name = 'registration/options.html'
    success_url = '/'
