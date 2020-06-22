from pprint import pprint

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView
from django.utils.translation import gettext_lazy as _
from mysite.core.forms import UserChangeForm, ProfileForm, UserForm


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('scxrd:index')
    template_name = 'registration/new_user.html'


class UserEdit(UpdateView):
    form_class = UserForm
    success_url = reverse_lazy('scxrd:index')
    model = User
    template_name = 'registration/edit_user.html'

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('index')
        else:
            messages.error(request, _('Please correct the error below.'))
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

        return render(request, 'registration/edit_user.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })

class OptionsView(TemplateView):
    """
    Show details of an experiment

    TODO: Make real options page
    """
    template_name = 'registration/options.html'
    success_url = '/'
