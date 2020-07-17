from crispy_forms.layout import Layout, Row, Column, HTML, Field, Submit, ButtonHolder
from django import forms
from django.utils.translation import gettext_lazy as _

from scxrd.form_utils import card, backbutton
from scxrd.forms.forms import ExperimentFormMixin
from scxrd.models.experiment_model import Measurement


class ExperimentEditForm(ExperimentFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.exp_title = _('Measurement')
        self.number = "<span class='btn btn-secondary ml-3 pt-0 pb-0 pl-1 pr-1'>Nr. {{ object.number }}</span>"
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            # Measurement ###

            # card(self.exp_title+self.number, backbutton),
            HTML('<div class="card w-100 mb-3">  <div class="card-header">{} {}'
                 '{}</div>'.format(self.exp_title, self.number, backbutton)),

            Row(
                Column('experiment_name', css_class='col-4'),
                Column('measure_date'),
                Column('end_time', css_class='col-4'),
            ),
            Row(
                Column('machine', css_class='col-4'),
                # Column('operator'), # done automatically in the view
                Column('measurement_temp', css_class='col-4'),
                Column('customer', css_class='col-4')
            ),
            Row(
                Column('base', css_class='col-4'),
                Column('glue', css_class='col-4'),
                Column(
                    HTML(""" 
                            {% if object.sample %}
                            {% load i18n %}
                            {% trans "Respective Sample" as myvar %}
                                <div class='pt-3 mt-3 ml-3 mr-3 ml-0 mb-3'>
                                    <a class='btn btn-outline-success w-100 mt-1 p-2' href="{% url "scxrd:op_samples_detail" object.sample.pk %}">
                                        {{ myvar }}           
                                    </a>
                                </div>
                            {% endif %}
                        """), css_class='col-4'
                ),
            ),
            HTML('</div>'),  # end of card

            Row(
                ButtonHolder(
                    Submit('Save', _('Save'), css_class='btn-primary mr-2'),
                    HTML('''
                        {% load i18n %}
                        {% trans "Cancel" as myvar %}
                        <a href="{% url 'scxrd:index' %}" class="btn btn-outline-danger" 
                                                    formnovalidate="formnovalidate">
                                                    {{ myvar }}</a>'''), css_class='ml-2 mb-3'
                ),
            ),

            # Crystal ######
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

            HTML('</div>'),  # end of card
            # HTML('</div>'),  # end of card
            # Files ########
            card(_('File upload')),
            Row(
                Column(
                    Field('cif_file_on_disk'), css_class='col-8'
                ),
            ),
            Row(
                Column(
                    Field('checkcif_on_disk'), css_class='col-8'
                ),
            ),
            Row(
                Column(
                    Field('reportdoc_on_disk'), css_class='col-8'
                ),
            ),
            HTML('</div>'),  # end of card
            # HTML('</div>'),  # end of card
            # save_button2,
            # HTML('</div>'),  # end of card
            card(_('Miscellaneous'), backbutton),
            Row(
                Column('publishable', css_class='col-6 mt-3'),
                Column('final', css_class='col-6 mt-3'),
            ),
            Row(
                Column('exptl_special_details'),
            ),
            HTML('</div>'),  # end of card
            Row(
                ButtonHolder(
                    Submit('Save', _('Save'), css_class='btn-primary mr-2'),
                    HTML('''
                        {% load i18n %}
                        {% trans "Cancel" as myvar %}
                        <a href="{% url 'scxrd:index' %}" class="btn btn-outline-danger" 
                                                    formnovalidate="formnovalidate">
                                                    {{ myvar }}</a>'''), css_class='ml-2'
                ), css_class='mb-5'
            ),

        )

    class Meta:
        model = Measurement
        fields = '__all__'
