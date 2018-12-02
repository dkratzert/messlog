from django.forms import ModelForm

from scxrd.models import Experiment


class MyModelForm(ModelForm):
    class Meta:
        model = Experiment
        fields = ['machine']

