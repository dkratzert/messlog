from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from scxrd.models import Profile


class ProfileNewForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)

    class Meta:
        model = Profile
        #'work_group',
        fields = ('phone_number',
                  #'company', 'street', 'house_number', 'building', 'town',
                  #'country', 'postal_code',
                  'comment')
        # fields = ('__all__')


class ProfileEditForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)

    class Meta:
        model = Profile
        #'work_group',
        fields = ('phone_number', 'company', 'street', 'house_number', 'building', 'town',
                  'country', 'postal_code', 'comment')
        # fields = ('__all__')


class UserForm(UserCreationForm):
    """The form to create a new user"""
    email = forms.EmailField(label=_('email address'), required=True)
    first_name = forms.CharField(label=_('first name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('last name'), max_length=150, required=True)

    class Meta:
        model = User
        #field_classes = {'user_form'   : User,
        #                 'profile_form': ProfileNewForm}
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email')
        # fields = ('__all__')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(label=_('email address'), required=True)

    class Meta:
        model = User
        field_classes = {'user_form'   : User,
                         'profile_form': Profile}
        fields = ('username', 'first_name', 'last_name', 'email')
        # fields = ('__all__')
