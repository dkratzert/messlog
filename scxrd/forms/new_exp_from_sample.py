from crispy_forms.layout import Layout, Row, Column, HTML, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from scxrd.form_utils import card, backbutton
from scxrd.forms.forms import ExperimentFormMixin
from scxrd.models import Experiment


class ExperimentFromSampleForm(ExperimentFormMixin, forms.ModelForm):
    number = forms.IntegerField(min_value=1)
    not_measured_cause = forms.CharField(widget=forms.Textarea, required=False, label=_('Not measured because'))
    was_measured = forms.BooleanField(label=_('Sample was not measured'),
                                      required=False,
                                      widget=forms.CheckboxInput(
                                          attrs={'data-toggle': "collapse", 'data-target': "#measure_box",
                                                 'id'         : "measure_check"})
                                      )

    def __init__(self, *args, **kwargs):
        self.exp_title = _('New Experiment')
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
                Column('experiment_name'),
                Column('number'),
                Column('measurement_temp'),
            ),
            Row(
                Column('machine', css_class='col-4'),
                # Column('operator'), # done automatically in the view
                Column('measure_date', css_class='col-4'),  # TODO: make it invisible?
                Column('customer', css_class='col-4 invisible'),
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
