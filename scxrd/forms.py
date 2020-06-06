from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, HTML, ButtonHolder, Button
from crispy_forms.layout import Layout, Submit, Row, Column
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.models import Experiment, Machine, CrystalSupport, Person
from scxrd.utils import COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES, COLOUR_CHOICES


class ExperimentTableForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('experiment', 'number', 'measure_date')


class CustomCheckbox(Field):
    template = 'custom_checkbox.html'


class MyDecimalField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['step'] = '0.01'
        return attrs


class ExperimentFormfieldsMixin(forms.ModelForm):
    measure_date = forms.DateTimeField(widget=DatePickerInput(format='%Y-%m-%d %H:%M'), required=True,
                                       initial=timezone.now)
    submit_date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'), required=False,
                                  label=_("Sample submission date (for service)"))
    result_date = forms.DateField(widget=DatePickerInput(format="%Y-%m-%d"), required=False,
                                  label=_("Results sent date (for service)"))
    measurement_temp = forms.FloatField(label=_('Measurement temp. [K]'), required=False)
    crystal_colour = forms.TypedChoiceField(choices=COLOUR_CHOICES, label=_('Crystal Color'), required=True)
    crystal_colour_mod = forms.TypedChoiceField(choices=COLOUR_MOD_CHOICES, label=_('Colour Modifier'), required=False)
    crystal_colour_lustre = forms.TypedChoiceField(choices=COLOUR_LUSTRE_COICES, label=_('Colour Lustre'),
                                                   required=False)
    machine = forms.ModelChoiceField(queryset=Machine.objects.all(), required=True)
    operator = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
    customer = forms.ModelChoiceField(queryset=Person.objects.all(), required=False, label=_('Customer (for service)'))
    crystal_size_z = MyDecimalField(required=True, min_value=0, label=_("Crystal size min"))
    crystal_size_y = MyDecimalField(required=True, min_value=0, label=_("Crystal size mid"))
    crystal_size_x = MyDecimalField(required=True, min_value=0, label=_("Crystal size max"))
    base = forms.ModelChoiceField(queryset=CrystalSupport.objects.all(), required=True)
    cif_file_on_disk = forms.FileField(required=False, label=_("CIF file"))


class ExperimentFormMixin(ExperimentFormfieldsMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # self.helper.form_action = reverse_lazy('scxrd:index', )
        self.helper.attrs = {'novalidate': 'novalidate'}
        self.helper.form_method = 'POST'
        self.helper.form_style = 'default'
        self.helper.use_custom_control = True
        self.helper.render_required_fields = True
        # Turn this off to see only mentioned form fields:
        self.helper.render_unmentioned_fields = False
        self.helper.help_text_inline = False  # both can not have the same value
        # self.helper.error_text_inline = True  # both can not have the same value
        self.helper.label_class = 'pl-3 pr-3 pt-2 pb-0 mt-1 mb-1 ml-0'  # 'font-weight-bold'
        self.helper.field_class = 'pl-3 pr-3 pb-0 pt-0'
        self.backbutton = """
            <a role="button" class="btn btn-sm btn-outline-secondary float-right my-0 py-0" 
                href="{% url "scxrd:index"%}">Back to start</a>
            """

        self.save_button = ButtonHolder(
            Submit('Save', 'Save', css_class='btn-primary mr-2 ml-0 mb-3'),
            # This cancel button works in combination with the FormActionMixin in views.py
            # the view is redirected to the index page if the request contains 'cancel'
            Submit('cancel', 'Cancel', css_class='btn btn-danger ml-2 mb-3', formnovalidate='formnovalidate'),
            HTML('<br>'),
        )

        self.experiment_layout = Layout(

            self.card(self.exp_title, self.backbutton),
            Row(
                Column('experiment'),
                Column('number'),
                Column('measurement_temp'),
            ),
            Row(
                Column('machine'),
                Column('operator'),
                Column('customer'),
            ),
            Row(
                Column('base'),
                Column('glue'),
                Column('measure_date'),
            ),
            Row(
                Column('crystal_size_z'),
                Column('crystal_size_y'),
                Column('crystal_size_x'),
            ),
            # HTML('</div>'),  # end of card, done later
        )

        self.crystal_layout = Layout(
            self.card('Crystal and Results', self.backbutton),
            # AppendedText('prelim_unit_cell', 'assumed formula', active=True),
            Row(
                Column('sum_formula', css_class='col-8'),
                Column('submit_date', css_class='col-4'),
            ),
            Row(
                Column('prelim_unit_cell', css_class='col-8'),
                Column('result_date', css_class='col-4'),
            ),
            Row(
                Column('solvents'),
                Column('conditions'),
                Column('crystal_habit'),
            ),
            Row(
                Column('crystal_colour'),
                Column('crystal_colour_mod'),
                Column('crystal_colour_lustre'),
            ),
            HTML('</div>'),  # end of card
        )

        self.files_layout = Layout(
            self.card(_('File upload')),
            Row(
                Column(
                    # Field('cif'), css_class='col-12'
                    Field('cif_file_on_disk'), css_class='col-8'
                ),
            ),
            HTML('</div>'),  # end of card
        )

        self.misc_layout = Layout(
            self.card(_('Miscellaneous'), self.backbutton),
            Row(
                Column('exptl_special_details'),
            ),
            Row(
                Column('publishable'),
            ),
            HTML('</div>'),  # end of card
        )

        self.crystal_colour_layout = Layout(
            Row(
                Column('crystal_colour'),
                Column('crystal_colour_mod'),
                Column('crystal_colour_lustre'),
            ),
        )

        self.sumform_row = Row(
            Column('sum_formula', css_class='col-4'),
            Column('submit_date', css_class='col-4'),
        )

    def card(self, header_title, button=''):
        return HTML('<div class="card w-100 mb-3">  <div class="card-header">{} {}</div>'.format(header_title, button))


class ExperimentNewForm(ExperimentFormMixin, forms.ModelForm):
    number = forms.IntegerField(min_value=1)

    def __init__(self, *args, **kwargs):
        self.exp_title = 'New Experiment'
        super().__init__(*args, **kwargs)
        self.fields['number'].initial = Experiment.objects.first().number + 1
        self.helper.render_unmentioned_fields = False

        self.helper.layout = Layout(
            # Experiment ###
            self.experiment_layout,
            self.crystal_colour_layout,
            self.sumform_row,
            HTML('</div>'),  # end of card
            self.save_button,
            # HTML('</div>'),  # end of card
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
            self.save_button,
            # Crystal ######
            self.crystal_layout,
            # HTML('</div>'),  # end of card
            # Files ########
            self.files_layout,
            # HTML('</div>'),  # end of card
            self.save_button,
            # HTML('</div>'),  # end of card
            self.misc_layout,
        )

    class Meta:
        model = Experiment
        fields = '__all__'
