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
    https://django.cowhite.com/blog/adding-and-editing-model-objects-using-django-class-based-views-and-forms/
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

    '''def form_valid(self, form):
        form.save(self.request.user)
        return super().form_valid(form)'''

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile_form = ProfileNewForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
            else:
                messages.error(request, _('Please correct the error below.'))
            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, _('Please correct the error below.'))
        return self.form_invalid(user_form)

    # def get_success_url(self, *args, **kwargs):
    #   return reverse("index")

    '''def post(self, request, *args, **kwargs):
        """
        Saving new user.
        """
        user_form = UserForm(request.POST)
        profile_form = ProfileNewForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            profile_instance = profile_form.save(commit=False)
            user_instance = user_form.save()
            profile_instance.user = user_instance
            profile_instance.user_id = user_instance.id
            profile_form.save()
            messages.success(request, _('Your profile was successfully created!'))
            return HttpResponseRedirect('/')
        else:
            messages.error(request, _('Please correct the error below.'))
        return super().post(request, *args, **kwargs)'''


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
