from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from crispy_forms.bootstrap import FormActions, AppendedText, InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, HTML
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
    # solvents_used = forms.ModelMultipleChoiceField(queryset=Solvent.objects.all(),
    #                                               widget=forms.CheckboxSelectMultiple)
    measure_date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'), required=True)
    submit_date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'), required=False)
    result_date = forms.DateTimeField(widget=DatePickerInput(format="%Y-%m-%d %H:%M"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # self.helper.form_action = reverse_lazy('scxrd:index', )
        self.helper.attrs = {'novalidate': 'novalidate'}
        self.helper.form_method = 'POST'
        self.helper.form_style = 'default'
        self.helper.render_unmentioned_fields = True
        self.helper.help_text_inline = False
        self.helper.label_class = 'p-2'  # 'font-weight-bold'
        self.helper.field_class = 'p-2'

        self.helper.layout = Layout(
            HTML('<div class="card w-100"><div class="card-header">Experiment</div>'),
            Row(
                Column('experiment', css_class='form-group col-md-4 mb-0 mt-0'),
                Column('number', css_class='form-group col-md-4 mb-0 mt-0'),
                Column(CustomCheckbox('publishable'), css_class='form-inline col-md-4'),
                css_class='form-row'
            ),
            Row(
                Column(Field('machine', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('operator', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('customer', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('base', css_class='custom-select'), css_class='col-md-4 mb-0 mt-0'),
                Column(Field('glue', css_class='custom-select'), css_class='col-md-4 mb-0 mt-0'),
                Column(
                ),
                css_class='form-row'
            ),
            HTML('</div>'),
            #HTML("<hr>"),
            HTML('<div class="card w-100 mt-3"><div class="card-header">Crystal</div>'),
            AppendedText('sum_formula', 'assumed formula', active=True),
            Row(
                Column('measure_date', css_class='form-group col-md-4 mb-0 mt-0'),
                Column('submit_date', css_class='form-group col-md-4 mb-0 mt-0'),
                Column('result_date', css_class='form-group col-md-4 mb-0 mt-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('solvent1', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('solvent2', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('solvent3', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                css_class='form-row mt-0 mb-0 form-sm'
            ),
            Row(
                Column(Field('crystal_colour', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('crystal_colour_mod', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('crystal_colour_lustre', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                css_class='form-row'
            ),
            HTML('</div>'),
            Field('cif', css_class='custom-select'),
            #'publishable',
            'special_details',  # important
            FormActions(
                Submit('submit', 'Save', css_class='btn-primary mr-2'),
                Submit('cancel', 'Cancel', css_class='btn-danger'),
                css_class='form-row mb-4 ml-0'
            ),
        )

    class Meta:
        model = Experiment
        fields = '__all__'
