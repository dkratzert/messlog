from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from django import forms

from scxrd.models import Experiment, Solvent


class ExperimentForm(forms.ModelForm):
    solvents_used = forms.ModelMultipleChoiceField(
        queryset=Solvent.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Experiment
        # fields = ('experiment', 'solvents_used', 'number', 'measure_date', 'machine', 'sum_formula', 'submit_date')
        fields = '__all__'
        widgets = {
            'submit_date': DatePickerInput(format='%Y-%m-%d'),
            'result_date': DatePickerInput(format='%Y-%m-%d'),
            'measure_date': DateTimePickerInput(format="%Y-%m-%d %H:%M"),
        }


class ExperimentTableForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('experiment', 'number', 'measure_date')
