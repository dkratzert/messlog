from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.layout import Layout, Row, Column, HTML, Submit
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.form_utils import card, backbutton
from scxrd.forms.forms import ExperimentFormMixin
from scxrd.models import Experiment


class ExperimentFromSampleForm(ExperimentFormMixin, forms.ModelForm):
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
        self.exp_title = _('New Experiment from sample')
        if user.first_name and user.last_name:
            self.exp_title = _('New experiment from sample by {} {}'.format(user.first_name, user.last_name))
        # pop the current user in order to save him as operator in Experiment model:
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.helper.render_unmentioned_fields = False
        try:
            self.fields['number'].initial = Experiment.objects.first().number + 1
        except AttributeError:
            self.fields['number'].initial = 1

        self.helper.layout = Layout(
            # Experiment ###
            card(self.exp_title, backbutton),
            Row(
                Column('experiment_name', css_class='col-4'),
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
                Column('crystal_colour'),
                Column('base'),
                Column('glue'),
                # Column('submit_date'),
            ),
            Row(
                Column('crystal_size_z'),
                Column('crystal_size_y'),
                Column('crystal_size_x'),
            ),
            Row(
                Column('sum_formula', css_class='col-8'),
                Column('crystal_habit'),
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
            Submit('Save', 'Save', css_class='btn-primary mr-2'),
            HTML('''<a href="{% url 'scxrd:index' %}" class="btn btn-outline-danger" 
                        formnovalidate="formnovalidate">Cancel</a>
                        '''),
            HTML("<div class='mb-5'></div>"),

        )

    class Meta:
        model = Experiment
        fields = '__all__'
