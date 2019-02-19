from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, HTML
from crispy_forms.layout import Layout, Submit, Row, Column
from django import forms
from django.contrib.auth.models import User
from django.db import OperationalError

from scxrd.datafiles.sadabs_model import SadabsModel
from scxrd.models import Experiment, Machine
from scxrd.utils import COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES, COLOUR_CHOICES


class ExperimentTableForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('experiment', 'number', 'measure_date')


class CustomCheckbox(Field):
    template = 'custom_checkbox.html'


class SadabsForm(forms.ModelForm):
    class Meta:
        model = SadabsModel
        fields = ('abs_file',)


class ExperimentFormfieldsMixin(forms.ModelForm):
    # solvents_used = forms.ModelMultipleChoiceField(queryset=Solvent.objects.all(),
    #                                               widget=forms.CheckboxSelectMultiple)
    measure_date = forms.DateTimeField(widget=DatePickerInput(format='%Y-%m-%d %H:%M'), required=True)
    submit_date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'), required=False,
                                  label="Sample submission date")
    result_date = forms.DateField(widget=DatePickerInput(format="%Y-%m-%d"), required=False, label="Results sent date")
    crystal_colour_mod = forms.TypedChoiceField(choices=COLOUR_MOD_CHOICES, label='Colour modifier')
    crystal_colour_lustre = forms.TypedChoiceField(choices=COLOUR_LUSTRE_COICES, label='Colour lustre')
    machine = forms.ModelChoiceField(queryset=Machine.objects.all(), required=True)
    operator = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
    crystal_size_x = forms.DecimalField(required=True, min_value=0, decimal_places=2)
    crystal_size_y = forms.DecimalField(required=True, min_value=0, decimal_places=2)
    crystal_size_z = forms.DecimalField(required=True, min_value=0, decimal_places=2)


class ExperimentFormMixin(ExperimentFormfieldsMixin, forms.ModelForm):

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

        self.experiment_layout = Layout(
            self.card(self.exp_title),
            Row(
                Column('experiment', css_class='form-group col-md-4 mb-0 mt-0'),
                Column('number', css_class='form-group col-md-4 mb-0 mt-0'),
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
                Column('measure_date', css_class='form-group col-md-4 mb-0 mt-0'),
                css_class='form-row'
            ),
            Row(
                Column(Field('crystal_size_x', css_class='custom'), css_class='col-md-4 mb-0 mt-0'),
                Column(Field('crystal_size_y'), css_class='col-md-4 mb-0 mt-0'),
                Column(Field('crystal_size_z'), css_class='col-md-4 mb-0 mt-0'),
                css_class='form-row'
            ),
        )

        self.crystal_layout = Layout(
            self.card('Crystal and Results'),
            AppendedText('sum_formula', 'assumed formula', active=True),
            Row(
                Column(Field('solvent1', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('solvent2', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('solvent3', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                css_class='form-row mt-0 mb-0 form-sm'
            ),
            Row(
                Column(Field('crystal_colour', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('crystal_colour_mod', css_class='custom-select'), css_class='form-group '
                                                                                         'col-md-4 mb-0 mt-0'),
                Column(Field('crystal_colour_lustre', css_class='custom-select'),
                       css_class='form-group col-md-4 mb-0 mt-0'),
                css_class='form-row'
            ),
            Row(
                Column('submit_date', css_class='form-group col-md-4 mb-0 mt-0'),
                Column('result_date', css_class='form-group col-md-4 mb-0 mt-0'),
                Column(),
                css_class='form-row'
            ),
            # Row(
            #    FormActions(
            #        Submit('submit', 'Save', css_class='btn-primary mr-2'),
            #        Submit('cancel', 'Cancel', css_class='btn-danger'),
            #    ),
            #    css_class='form-row ml-0 mb-0'
            # ),
        )

        self.files_layout = Layout(
            self.card('Files and Comments'),
            # TODO: add drag&drop file upload:
            Field('cif', css_class='custom-select'),
            Row(
                #    FormActions(
                #        Submit('submit', 'Save', css_class='btn-primary mr-2'),
                #        Submit('cancel', 'Cancel', css_class='btn-danger'),
                #        ),
                Column(CustomCheckbox('publishable'), css_class='form-group col-md-4 ml-2'),
                css_class='form-row ml-0 mb-0'
            ),
            'exptl_special_details',
            Row(
                FormActions(
                    Submit('submit', 'Save', css_class='btn-primary mr-2'),
                    Submit('cancel', 'Cancel', css_class='btn-danger'),
                ),
                css_class='form-row ml-0 mb-0'
            ),
        )

        self.crystal_colour_layout = Layout(
            Row(
                Column(Field('crystal_colour', css_class='custom-select'), css_class='form-group col-md-4 mb-0 mt-0'),
                Column(Field('crystal_colour_mod', css_class='custom-select'), css_class='form-group '
                                                                                         'col-md-4 mb-0 mt-0'),
                Column(Field('crystal_colour_lustre', css_class='custom-select'),
                       css_class='form-group col-md-4 mb-0 mt-0'),
                css_class='form-row'
            ),
        )

    def card(self, header_title):
        return HTML('<div class="card w-100 mb-3">  <div class="card-header">{}</div>'.format(header_title))


class ExperimentNewForm(ExperimentFormMixin, forms.ModelForm):
    try:
        number = forms.IntegerField(min_value=1, initial=Experiment.objects.first().number + 1)
    except (AttributeError, OperationalError):
        number = 1

    def __init__(self, *args, **kwargs):
        self.exp_title = 'New Experiment'
        super().__init__(*args, **kwargs)
        self.helper.render_unmentioned_fields = False

        self.helper.layout = Layout(
            # Experiment ###
            self.experiment_layout,
            self.crystal_colour_layout,
            AppendedText('sum_formula', 'assumed formula', active=True),
            Row(
                FormActions(
                    Submit('submit', 'Save', css_class='btn-primary mr-2'),
                    Submit('cancel', 'Cancel', css_class='btn-danger'),
                ),
                css_class='form-row ml-0 mb-0'
            ),
            HTML('</div>'),
        )

    class Meta:
        model = Experiment
        fields = '__all__'


class ExperimentEditForm(ExperimentFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.exp_title = 'Experiment'
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            # Experiment ###
            self.experiment_layout,
            HTML('</div>'),
            # Crystal ######
            self.crystal_layout,
            HTML('</div>'),
            # Files ########
            self.files_layout,
            HTML('</div>'),
        )

    class Meta:
        model = Experiment
        fields = '__all__'


class FinalizeCifForm(ExperimentFormMixin, forms.ModelForm):
    """
    New Idea:
    - The database is the master of information. During Save(), I compare the database and the cif values.
      The differ items are displayed in a card with the title "Unclear cif items"
    - every empty cif key/value is taken from the db.
    - during file upload, I show a page with conflicting item if there are any.

    -----------------------------------------------------------------------------
    CrispyForm class to generate a cif report.

    TODO: - Make an example where only crystal color, operator and absorption correction appear.
          - work this out until the you can choose between the alternatives and the form is valid.
          - add all the other aspects

    https://stackoverflow.com/questions/17754295/can-i-have-a-django-form-without-model

    TODO: Maybe add two columns. One with the information that is alredy there, and one with the
          controls to modify/add more information.

          View goes through all submitted form data and merges the information to a new cif.
    """
    exptl_crystal_colour = forms.ChoiceField(choices=COLOUR_CHOICES, label='Crystal Colour')

    def __init__(self, *args, **kwargs):
        self.exp_title = 'Report'
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            # Experiment ###
            self.experiment_layout,
            HTML('</div>'),
            # Crystal ######
            self.crystal_layout,
            HTML('</div>'),
            # Files ########
            self.files_layout,
            HTML('</div>'),
        )

    """    
    def clean(self):
        cleaned_data = super().clean()
        exptl_crystal_colour = cleaned_data.get('exptl_crystal_colour')
        if not exptl_crystal_colour:
            raise forms.ValidationError('You have to give a color.')"""

    class Meta:
        model = Experiment
        fields = '__all__'
