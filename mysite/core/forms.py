from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from scxrd.models import Profile, WorkGroup


class ProfileEditForm(forms.ModelForm):
    phone_number = forms.CharField(required=True, label=_('phone number'))
    street = forms.CharField(required=False, label=_('street'))
    house_number = forms.CharField(required=False, label=_('house number'))
    building = forms.CharField(required=False, label=_('building'))
    town = forms.CharField(required=False, label=_('town'))
    country = forms.CharField(required=False, label=_('country'))
    postal_code = forms.CharField(required=False, label=_('postal code'))
    work_group = forms.ModelChoiceField(required=True, queryset=WorkGroup.objects.all(), label=_('Member of Group'))

    class Meta:
        model = Profile
        fields = ('phone_number', 'work_group', 'company', 'street', 'house_number', 'building', 'town',
                  'country', 'postal_code', 'comment')


class SignupForm(UserCreationForm):
    """The form to create a new user (attached to a profile)"""
    email = forms.EmailField(label=_('email address'), required=True)
    first_name = forms.CharField(label=_('first name'), required=True)
    last_name = forms.CharField(label=_('last name'), required=True)
    phone_number = forms.CharField(required=True, label=_('phone number'))
    work_group = forms.ModelChoiceField(required=True, queryset=WorkGroup.objects.all(), label=_('Member of Group'))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email')


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(label=_('email address'), required=True)

    class Meta:
        model = User
        field_classes = {'user_form'   : User,
                         'profile_form': Profile}
        fields = ('username', 'first_name', 'last_name', 'email')
