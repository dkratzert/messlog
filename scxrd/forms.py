from django import forms
from bootstrap_datepicker_plus import DatePickerInput
from scxrd.models import Experiment


class ExperimentForm(forms.ModelForm):

    class Meta:
        model = Experiment
        # fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula')
        fields = '__all__'
        widgets = {'measure_date': DatePickerInput(
            options={
                "format": "YYYY-MM-DD",
                "locale": "de",
            }),
        }



class ExperimentTableForm(forms.ModelForm):

    class Meta:
        model = Experiment
        fields = ('experiment', 'number', 'measure_date')


