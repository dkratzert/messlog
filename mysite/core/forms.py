from django.contrib.auth.models import User
from django.forms import ModelForm

from scxrd.models import Profile


class UserChangeForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        # fields = ('first_name', 'last_name',
        #          'company',)
        #          'work_group',
        #          'email_address',
        #          'street',
        #          'house_number',
        #          'phone_number',
        #          )
        # field_classes = {'username': UsernameField}


class UserForm(ModelForm):
    class Meta:
        model = User
        field_classes = {'user_form': User,
                         'profile_form': Profile}
        fields = ('username', 'first_name', 'last_name', 'email')
        #fields = ('__all__')


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('company', 'street', 'house_number', 'building', 'town', 'country', 'postal_code',
                  'phone_number', 'comment')
        #fields = ('__all__')
