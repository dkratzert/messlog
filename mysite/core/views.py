from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView, CreateView

from mysite.core.forms import UserForm, UserEditForm, ProfileNewForm, ProfileEditForm
from scxrd.models import Profile


class SignUp(CreateView):
    """Create a new user
    """
    form_class = UserForm
    success_url = reverse_lazy('index')
    template_name = 'registration/new_user.html'

    def get(self, request, *args, **kwargs):
        """
        Initializing empty Forms:
        """
        context = {
            'user_form'   : UserForm(),
            'profile_form': ProfileNewForm()
        }
        return render(request, 'registration/new_user.html', context)

    def form_invalid(self, context):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(context=context)

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        profile_form = ProfileNewForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile_form = ProfileNewForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
            else:
                messages.error(request, _('Please correct the error below.'))
                return self.form_invalid(context={
                    'user_form': user_form,
                    'profile_form': profile_form
                })
            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
        return self.form_invalid(context={
            'user_form'   : user_form,
            'profile_form': profile_form
        })


class UserEdit(UpdateView):
    form_class = UserEditForm
    success_url = reverse_lazy('index')
    model = User
    template_name = 'registration/edit_user.html'

    def post(self, request, *args, **kwargs):
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('index')
        else:
            messages.error(request, _('Please correct the error below.'))
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

        return render(request, 'registration/edit_user.html', {
            'user_form'   : user_form,
            'profile_form': profile_form
        })


class OptionsView(TemplateView):
    """
    Show details of an experiment

    TODO: Make real options page
    """
    template_name = 'registration/options.html'
    success_url = '/'
