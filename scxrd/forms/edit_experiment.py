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
            # HTML('</div>'),  # end of card, done later
        )

        self.crystal_layout = Layout(
            card(_('Crystal and Conditions'), backbutton),
            # AppendedText('prelim_unit_cell', 'presumed empirical formula', active=True),
            Row(
                Column('crystal_size_z'),
                Column('crystal_size_y'),
                Column('crystal_size_x'),
            ),
            Row(
                Column('crystal_colour'),
                Column('crystal_colour_mod'),
                Column('crystal_colour_lustre'),
            ),
            Row(
                Column('prelim_unit_cell', css_class='col-8'),
                Column('result_date', css_class='col-4'),
            ),
            Row(
                Column('sum_formula', css_class='col-8'),
                Column('crystal_habit'),
            ),

            Row(
                # Column('solvents'),
                Column(
                    HTML("""
                        <div id="div_id_reaction_path" class="form-group">\n
                            <label for="id_svg_struct_samp" class="pr-3 pt-2 pb-0 mt-3 mb-0 ml-3">\n
                                Draw the desired structure<span class="asteriskField">*</span>\n
                            </label>\n
                            <small id="hint_id_reaction_path" class="form-text text-muted ml-3">
                                This field is an alternative to the file upload above:
                            </small>\n
                            <input type="hidden" id="id_svg_struct_samp" value="" name="desired_struct_samp">\n
                            <div class="p-3">
                                <iframe id="ketcher-frame" src="ketcher.html">\n
                                </iframe>\n
                            </div>
                        </div>\n
                        """)
                ),

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
