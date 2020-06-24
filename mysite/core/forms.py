from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from scxrd.models import Profile


class UserForm(UserCreationForm):
    """The form to create a new user"""
    email = forms.EmailField(label=_('email address'), required=True)
    first_name = forms.CharField(label=_('first name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('last name'), max_length=150, required=True)

    class Meta:
        model = User
        field_classes = {'user_form'   : User,
                         'profile_form': Profile}
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email')
        # fields = ('__all__')


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(label=_('email address'), required=True)

    class Meta:
        model = User
        field_classes = {'user_form'   : User,
                         'profile_form': Profile}
        fields = ('username', 'first_name', 'last_name', 'email')
        # fields = ('__all__')


class ProfileNewForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)

    class Meta:
        model = Profile
        fields = ('phone_number',
                  #'company', 'street', 'house_number', 'building', 'town',
                  #'country', 'postal_code',
                  'comment')
        # fields = ('__all__')


class ProfileEditForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)

    class Meta:
        model = Profile
        fields = ('phone_number', 'company', 'street', 'house_number', 'building', 'town',
                  'country', 'postal_code', 'comment')
        # fields = ('__all__')