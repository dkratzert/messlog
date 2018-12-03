from django import forms
from django.forms import DateTimeField

from scxrd.models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        measure_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
        #fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula')
        fields = '__all__'
        widgets = { 'measure_date': forms.DateTimeInput(attrs={'class': 'datepicker'})}


