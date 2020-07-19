from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.layout import Layout, Row, Column, HTML, Submit
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.form_utils import card, backbutton
from scxrd.forms.forms import MeasurementFormMixin
from scxrd.models.measurement_model import Measurement


class MeasurementFromSampleForm(MeasurementFormMixin, forms.ModelForm):
    number = forms.IntegerField(min_value=1, required=False)
    measure_date = forms.DateTimeField(widget=DatePickerInput(format='%Y-%m-%d %H:%M'), required=False,
                                       initial=timezone.now, label=_('measure date'))
    not_measured_cause = forms.CharField(widget=forms.Textarea, required=False, label=_('Not measured because'))
    was_measured = forms.BooleanField(label=_('Sample was not measured'),
                                      required=False,
                                      widget=forms.CheckboxInput(
                                          attrs={'data-toggle': "collapse", 'data-target': "#measure_box",
                                                 'id'         : "measure_check"})
                                      )

    def __init__(self, *args, **kwargs):
        user = User.objects.get(pk=kwargs.get('initial').get('customer'))
        self.exp_title = _('New measurement of a sample')
        if user.first_name and user.last_name:
            self.exp_title = _('New measurement of a sample by %(first)s %(last)s') % {'first': user.first_name, 'last': user.last_name}
        # pop the current user in order to save him as operator in Measurement model:
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.helper.render_unmentioned_fields = False
        try:
            self.fields['number'].initial = Measurement.objects.first().number + 1
        except AttributeError:
            self.fields['number'].initial = 1

        self.helper.layout = Layout(
            # Measurement ###
            card(self.exp_title, backbutton),
            Row(
                Column('measurement_name', css_class='col-4'),
                Column('measurement_temp', css_class='col-4'),
                # Column('customer', css_class='col-4 invisible'),  # handled in the view
            ),
            Row(
                Column('machine', css_class='col-4'),
                # Column('operator'), # done automatically in the view
                Column('measure_date', css_class='col-4'),
                Column('end_time', css_class='col-4'),
            ),
            Row(
                Column('base'),
                Column('glue'),
                Column('crystal_colour'),
                # Column('submit_date'),
            ),
            Row(
                Column('sum_formula', css_class='col-8'),
                Column('crystal_habit'),
            ),
            Row(
                Column('crystal_size_z'),
                Column('crystal_size_y'),
                Column('crystal_size_x'),
            ),
            Row(
                Column('exptl_special_details'),
            ),
            Row(
                Column('prelim_unit_cell', css_class='col-8'),
                Column('was_measured', css_class='col-4 mt-5'),
            ),
            Row(
                Column('not_measured_cause', css_id='measure_box', css_class="collapse col-12", ),
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
