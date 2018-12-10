from django import forms
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from django.forms import FileField

from scxrd.models import Experiment, Machine
from scxrd.widgets import DateTimeInput, DateInput
from uploadman.models import Upload


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        # fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'submit_date')
        fields = '__all__'
        widgets = {
            'submit_date' : DatePickerInput(format='%Y-%m-%d'),
            'result_date' : DatePickerInput(format='%Y-%m-%d'),
            'measure_date': DateTimePickerInput(format="%Y-%m-%d %H:%M"),
            'upload': FileField(),
        }


class ExperimentTableForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('experiment', 'number', 'measure_date')
