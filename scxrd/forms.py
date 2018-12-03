from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import StrictButton
from scxrd.models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        measure_date = forms.DateField(
            widget=forms.TextInput(
                attrs={'type': 'date'}
            )
        )
        fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula')
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save Experiment'))


