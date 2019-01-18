from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field
from crispy_forms.layout import Layout, Submit, Row, Column
from django import forms
from django.contrib.auth.models import User

from scxrd.models import Experiment, Solvent, Machine, Person


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


class CustomCheckbox(Field):
    template = 'custom_checkbox.html'


class ExperimentnewForm(forms.ModelForm):
    solvents_used = forms.ModelMultipleChoiceField(queryset=Solvent.objects.all(),
                                                   widget=forms.CheckboxSelectMultiple)

    experiment = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Experiment name'}))
    number = forms.IntegerField(required=True)
    machine = forms.ModelChoiceField(queryset=Machine.objects.all(), required=True)
    operator = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
    customer = forms.ModelChoiceField(queryset=Person.objects.all(), required=False)
    publishable = CustomCheckbox('publishable')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_action = reverse_lazy('scxrd:index', )
        self.helper.attrs = {'novalidate': 'novalidate'}
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column('experiment', css_class='form-group col-md-4 mb-0'),
                Column('number', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            CustomCheckbox('publishable'),
            Row(
                Column('machine', css_class='form-group col-md-4 mb-0'),
                Column('operator', css_class='form-group col-md-4 mb-0'),
                Column('customer', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            # Submit('submit', 'Save'),
            # Submit('submit', 'Cancel', css_class='btn btn-danger', href=reverse_lazy('scxrd:index'))
        )
        self.helper.add_input(Submit('submit', 'Save', css_class='btn-primary'))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class='btn-danger'))

    class Meta:
        model = Experiment
        fields = '__all__'
