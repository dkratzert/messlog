from django.forms import ModelForm

from polls.models import Machine, Measurement


class MyModelForm(ModelForm):
    class Meta:
        model = Measurement
        fields = ['used_machine']

