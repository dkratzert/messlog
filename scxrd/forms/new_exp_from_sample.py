from crispy_forms.layout import Layout, Row, Column, HTML, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from scxrd.form_utils import card, backbutton
from scxrd.forms.forms import ExperimentFormMixin
from scxrd.models import Experiment


class ExperimentFromSampleForm(ExperimentFormMixin, forms.ModelForm):
    number = forms.IntegerField(min_value=1)
    not_measured_cause = forms.CharField(widget=forms.Textarea, required=False)
    was_measured = forms.BooleanField(label=_('Was not Measured'),
                                      required=False,
                                      widget=forms.CheckboxInput(
                                          attrs={'data-toggle': "collapse", 'data-target': "#measurebox",
                                                 'id'         : "measurecheck"})
                                      )

    def __init__(self, *args, **kwargs):
        self.exp_title = _('New Experiment')
        # pop the current user in order to save him as operator in Experiment model:
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        try:
            self.fields['number'].initial = Experiment.objects.first().number + 1
        except AttributeError:
            self.fields['number'].initial = 1

        self.crystal_colour_row = Layout(
            Row(
                Column('crystal_colour'),
                Column('crystal_colour_mod'),
                Column('crystal_colour_lustre'),
            ),
        )

        self.experiment_layout = Layout(

            card(self.exp_title, backbutton),
            Row(
                Column('experiment_name'),
                Column('number'),
                Column('measurement_temp'),
            ),
            Row(
                Column('machine'),
                # Column('operator'), # done automatically in the view
                Column('measure_date'),  # TODO: make it invisible?
                Column('customer'),
            ),
            Row(
                Column('base'),
                Column('glue'),
                # Column('submit_date'),
            ),
            Row(
                Column('crystal_size_z'),
                Column('crystal_size_y'),
                Column('crystal_size_x'),
            ),
            # HTML('</div>'),  # end of card, done later
        )

        self.helper.layout = Layout(
            # Experiment ###
            self.experiment_layout,
            self.crystal_colour_row,
            Row(
                Column('sum_formula', css_class='col-8'),
                Column('crystal_habit'),
            ),
            Row(
                Column('exptl_special_details'),
            ),
            Row(
                Column('was_measured',
                       )
            ),
            Row(
                Column('not_measured_cause', css_id='measurebox', css_class="collapse col-12", ),
            ),
            HTML('</div>'),  # end of card
            Submit('Save', 'Save', css_class='btn-primary mr-2'),
            HTML('''<a href="{% url 'scxrd:all_experiments' %}" class="btn btn-outline-danger" 
                        formnovalidate="formnovalidate">Cancel</a>
                        '''),

        )

    class Meta:
        model = Experiment
        fields = '__all__'