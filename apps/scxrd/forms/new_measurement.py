from crispy_forms.layout import Layout, Row, Column, HTML, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.scxrd.form_utils import card, backbutton
from apps.scxrd.forms.forms import MeasurementFormMixin
from apps.scxrd.models.measurement_model import Measurement


class MeasurementNewForm(MeasurementFormMixin, forms.ModelForm):
    number = forms.IntegerField(min_value=1, required=False)
    resolution = forms.FloatField(min_value=0.0, max_value=999.0, label=_('Resolution [Å]'))
    # customer = forms.CharField(max_length=150, required=False, label=_('Customer (for service only)'))

    def __init__(self, *args, **kwargs):
        self.exp_title = _('New Measurement')
        # This is essential:
        # pop the current user in orde to save him as operator in Measurement model:
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            # Measurement ###
            card(self.exp_title, backbutton),
            Row(
                Column('measurement_name', css_class='col-4'),
                Column('measure_date'),
                Column('end_time', css_class='col-4'),
            ),
            Row(
                Column('machine'),
                # Column('operator'), # done automatically in the view
                Column('measurement_temp', css_class='col-4'),
                Column('customer'),
            ),
            Row(
                Column('base'),
                Column('glue'),
                Column('crystal_habit'),
            ),
            Row(
                Column('sum_formula', css_class='col-8'),
                Column('crystal_colour'),
                # Column('crystal_colour_mod'),
                # Column('crystal_colour_lustre'),
            ),
            Row(
                Column('crystal_size_z'),
                Column('crystal_size_y'),
                Column('crystal_size_x'),
            ),
            Row(
                Column('prelim_unit_cell', css_class='col-8'),
                Column('resolution', css_class='col-4'),
            ),
            Row(
                Column('exptl_special_details'),
            ),
            HTML('</div>'),  # end of card

            Submit('Save', _('Save'), css_class='btn-primary mr-2'),
            HTML('''
            {% load i18n %}
            {% trans "Cancel" as myvar %}
            <a href="{% url 'scxrd:index' %}" class="btn btn-outline-danger" 
                    formnovalidate="formnovalidate">{{ myvar }}</a>'''),
            HTML("<div class='mb-5'></div>"),
        )

    class Meta:
        model = Measurement
        fields = '__all__'
