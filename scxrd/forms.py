from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, HTML, Button
from crispy_forms.layout import Layout, Submit, Row, Column
from django import forms
from django.contrib.auth.models import User
from django.db import OperationalError
from django.utils.translation import gettext_lazy as _

from scxrd.cif_model import CifFileModel
from scxrd.models import Experiment, Machine, CrystalSupport
from scxrd.utils import COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES


class ExperimentTableForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('experiment', 'number', 'measure_date')


class CustomCheckbox(Field):
    template = 'custom_checkbox.html'


class CifForm(forms.ModelForm):
    class Meta:
        model = CifFileModel
        fields = ('cif_file_on_disk',)


class ExperimentFormfieldsMixin(forms.ModelForm):
    measure_date = forms.DateTimeField(widget=DatePickerInput(format='%Y-%m-%d %H:%M'), required=True)
    submit_date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'), required=False,
                                  label=_("Sample submission date"))
    result_date = forms.DateField(widget=DatePickerInput(format="%Y-%m-%d"), required=False,
                                  label=_("Results sent date"))
    crystal_colour_mod = forms.TypedChoiceField(choices=COLOUR_MOD_CHOICES, label=_('Colour modifier'))
    crystal_colour_lustre = forms.TypedChoiceField(choices=COLOUR_LUSTRE_COICES, label=_('Colour lustre'))
    machine = forms.ModelChoiceField(queryset=Machine.objects.all(), required=True)
    operator = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
    crystal_size_x = forms.DecimalField(required=True, min_value=0, decimal_places=2, label=_("Crystal size max"))
    crystal_size_y = forms.DecimalField(required=True, min_value=0, decimal_places=2, label=_("Crystal size mid"))
    crystal_size_z = forms.DecimalField(required=True, min_value=0, decimal_places=2, label=_("Crystal size min"))
    base = forms.ModelChoiceField(queryset=CrystalSupport.objects.all(), required=True)
    cif = forms.FileField(required=False)


class ExperimentFormMixin(ExperimentFormfieldsMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # self.helper.form_action = reverse_lazy('scxrd:index', )
        self.helper.attrs = {'novalidate': 'novalidate'}
        self.helper.form_method = 'POST'
        self.helper.form_style = 'default'
        # Turn this off to see only mentioned form fields:
        self.helper.render_unmentioned_fields = False
        self.helper.help_text_inline = False  # both can not have the same value
        # self.helper.error_text_inline = True  # both can not have the same value
        self.helper.label_class = 'p-2'  # 'font-weight-bold'
        self.helper.field_class = 'p-2'
        self.backbutton = """
            <a role="button" class="btn btn-sm btn-outline-secondary float-right my-0 py-0" 
                href="{% url "scxrd:index"%}">Back to start</a>
            """

        self.experiment_layout = Layout(

            self.card(self.exp_title, self.backbutton),
            Row(
                Column('experiment', css_class='form-group col-md-4'),
                Column('number', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            Row(
                Column(Field('machine', css_class='custom-select'), css_class='form-group col-md-4'),
                Column(Field('operator', css_class='custom-select'), css_class='form-group col-md-4'),
                Column(Field('customer', css_class='custom-select'), css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            Row(
                Column(Field('base', css_class='custom-select'), css_class='col-md-4'),
                Column(Field('glue', css_class='custom-select'), css_class='col-md-4'),
                Column('measure_date', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            Row(
                Column(Field('crystal_size_x', css_class='custom'), css_class='col-md-4'),
                Column(Field('crystal_size_y'), css_class='col-md-4'),
                Column(Field('crystal_size_z'), css_class='col-md-4'),
                css_class='form-row'
            ),
        )

        self.crystal_layout = Layout(
            self.card('Crystal and Results', self.backbutton),
            # AppendedText('prelim_unit_cell', 'assumed formula', active=True),
            Row(
                Column(Field('sum_formula', css_class='col-12'), css_class='form-group col-md-12'),
                css_class='form-row form-sm'
            ),
            Row(
                Column(Field('solvents', css_class='col-12 mb-0'), css_class='form-group col-md-4'),
                Column(Field('conditions', css_class='col-12 mb-0'), css_class='form-group col-md-4'),
                Column(Field('crystal_habit'), css_class='form-group col-md-4'),
                css_class='form-row form-sm'
            ),
            Row(
                Column(Field('crystal_colour', css_class='custom-select'),
                       css_class='form-group'),
                Column(Field('crystal_colour_mod', css_class='custom-select'),
                       css_class='form-group'),
                Column(Field('crystal_colour_lustre', css_class='custom-select'),
                       css_class='form-group'),
                css_class='form-row'
            ),
            Row(
                Column('submit_date', css_class='form-group col-md-4'),
                Column('result_date', css_class='form-group col-md-4'),
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
            self.card(_('File upload')),
            Row(
                Column(
                    HTML('''{% include "scxrd/uploaded_files.html" %}'''),
                    HTML('''<a class="btn btn-secondary btn-small" href="{% url "scxrd:upload_cif_file" object.pk %}"> 
                            Upload a cif file </a>'''),
                    css_class='ml-2 mb-3 form-sm'
                ),
                HTML('</div>'),  # end of card
                css_class='form-row mt-3 form-sm'
            ),
            self.card(_('Miscellaneous'), self.backbutton),
            Row(
                Column(HTML('''<div id="upload_here"></div>''')),
                css_class='form-row ml-0 mb-0'
            ),
            Row(
                Column('exptl_special_details', css_class='col-12 mb-0'),
                css_class='form-row ml-0 mb-0'
            ),
            Row(
                Column(CustomCheckbox('publishable'), css_class='form-group col-md-4 ml-2 mt-0'),
                css_class='form-row ml-0 mb-0'
            ),
            Row(
                FormActions(
                    Submit('submit', 'Save', css_class='btn-primary mr-2'),
                    # Button('cancel', 'Cancel', css_class='btn btn-default'),
                    HTML('''<a name="cancel" class="btn btn-warning" id="button-id-cancel"
                            href="{% url 'scxrd:index' %}"/>Cancel</a>'''),
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

    def card(self, header_title, button=''):
        return HTML('<div class="card w-100 mb-3">  <div class="card-header">{} {}</div>'.format(header_title, button))


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
            # AppendedText('sum_formula', 'assumed formula', active=True),
            Row(
                Column('sum_formula', css_class='col-12 mb-0'),
                css_class='form-row ml-0 mb-0'
            ),
            Row(
                FormActions(
                    Submit('submit', 'Save', css_class='btn-primary mr-2'),
                    Button('cancel', 'Cancel', css_class='btn btn-default'),
                ),
                css_class='form-row ml-0 mb-0'
            ),
            HTML('</div>'),  # end of card
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
            HTML('</div>'),  # end of card
            # Crystal ######
            self.crystal_layout,
            HTML('</div>'),  # end of card
            # Files ########
            self.files_layout,
            HTML('</div>'),  # end of card
        )

    class Meta:
        model = Experiment
        fields = '__all__'
