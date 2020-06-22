from django.contrib.auth.models import User
from django.forms import ModelForm

from scxrd.models import Person


class UserChangeForm(ModelForm):


    class Meta:
        model = Person
        fields = ('first_name', 'last_name',
                  'company',
                  #'work_group',
                  'email_address',
                  'street',
                  'house_number',
                  'phone_number',
                  )
        #field_classes = {'username': UsernameField}