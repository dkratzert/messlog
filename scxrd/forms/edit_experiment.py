from crispy_forms.layout import Layout, Row, Column, HTML, Field
from django import forms
from django.utils.translation import gettext_lazy as _

from scxrd.form_utils import card, backbutton, save_button2
from scxrd.forms.forms import ExperimentFormMixin
from scxrd.models import Experiment


class ExperimentEditForm(ExperimentFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.exp_title = _('Experiment')
        super().__init__(*args, **kwargs)

        self.experiment_layout = Layout(

            card(self.exp_title, backbutton),
            Row(
                Column('experiment'),
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

        self.crystal_layout = Layout(
            card(_('Crystal and Results'), backbutton),
            # AppendedText('prelim_unit_cell', 'presumed empirical formula', active=True),
            Row(
                Column('sum_formula', css_class='col-8'),
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
            card(_('File upload')),
            Row(
                Column(
                    # Field('cif'), css_class='col-12'
                    Field('cif_file_on_disk'), css_class='col-8'
                ),
            ),
            HTML('</div>'),  # end of card
        )

        self.misc_layout = Layout(
            card(_('Miscellaneous'), backbutton),
            Row(
                Column('exptl_special_details'),
            ),
            Row(
                Column('publishable'),
            ),
            HTML('</div>'),  # end of card
        )

        self.helper.layout = Layout(
            # Experiment ###
            self.experiment_layout,
            HTML('</div>'),  # end of card
            save_button2,
            # Crystal ######
            self.crystal_layout,
            # HTML('</div>'),  # end of card
            # Files ########
            self.files_layout,
            # HTML('</div>'),  # end of card
            save_button2,
            # HTML('</div>'),  # end of card
            self.misc_layout,
        )

    class Meta:
        model = Experiment
        fields = '__all__'