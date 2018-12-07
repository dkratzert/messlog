from django import forms
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput

from scxrd.models import Experiment, Machine


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        # fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'submit_date')
        fields = '__all__'
        widgets = {
            'submit_date' : DateTimePickerInput(format='%Y-%m-%d'),
            'result_date' : DateTimePickerInput(format='%Y-%m-%d'),
            'measure_date': DateTimePickerInput(format="%Y-%m-%d %H:%M",),
        }


class ExperimentTableForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('experiment', 'number', 'measure_date')
