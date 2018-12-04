from django import forms
from django.contrib.admin.widgets import AdminDateWidget

from scxrd.models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        #measure_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
        #fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula')
        fields = '__all__'
        measure_date = forms.DateField(widget=AdminDateWidget())
        #widgets = { 'measure_date': forms.DateInput(attrs={'class': 'datepicker'})}


