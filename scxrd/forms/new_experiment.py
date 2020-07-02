from crispy_forms.layout import Layout, Row, Column, HTML, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from scxrd.form_utils import card, backbutton
from scxrd.forms.forms import ExperimentFormMixin
from scxrd.models import Experiment


class ExperimentNewForm(ExperimentFormMixin, forms.ModelForm):
    number = forms.IntegerField(min_value=1)
    #customer = forms.CharField(max_length=150, required=False, label=_('Customer (for service)'))

    def __init__(self, *args, **kwargs):
        self.exp_title = _('New Experiment')
        # pop the current user in orde to save him as operator in Experiment model:
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
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
                Column('machine'),
                # Column('operator'), # done automatically in the view
                Column('measure_date'),
                Column('customer'),
            ),
            Row(
                Column('base'),
                Column('glue'),
                Column('crystal_habit'),
            ),
            Row(
                Column('crystal_size_z'),
                Column('crystal_size_y'),
                Column('crystal_size_x'),
            ),
            Row(
                Column('sum_formula', css_class='col-8'),
                Column('crystal_colour'),
                #Column('crystal_colour_mod'),
                #Column('crystal_colour_lustre'),
            ),
            Row(
                Column('prelim_unit_cell', css_class='col-8'),
            ),
            Row(
                Column('exptl_special_details'),
            ),
            HTML('</div>'),  # end of card

            Submit('Save', 'Save', css_class='btn-primary mr-2'),
            HTML('''<a href="{% url 'scxrd:all_experiments' %}" class="btn btn-outline-danger" 
                    formnovalidate="formnovalidate">Cancel</a> '''),
            HTML("<div class='mb-5'></div>"),
        )

    class Meta:
        model = Experiment
        fields = '__all__'


