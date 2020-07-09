from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from scxrd.form_utils import card, backbutton, submit_button
from scxrd.sample_model import Sample


class SubmitFormfieldsMixin(forms.ModelForm):
    """
    Definition of the fields for the customer Sample form.
    """
    submit_date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'), required=False,
                                  label=_("Sample submission date"))
    sum_formula = forms.CharField(label=_("Presumed sum formula"), required=True)
    crystallization_conditions = forms.CharField(label=_('Solvents used for crystallization, method, conditions'),
                                                 required=True,
                                                 help_text=_(
                                                     "Knowing the solvents used for synthesis and crystallization "
                                                     "can be crucial for the success of the structure solution and "
                                                     "refinement."))
    reaction_path = forms.FileField(label=_('Document with reaction equation'),
                                    required=False,
                                    help_text=_("Please upload a PDF document showing the reaction equation "
                                                "with the desired product <br> including all conditions, "
                                                "solvents and reagents used."))
    desired_struct_draw = forms.CharField(label=_('Desired structure'), required=False)
    special_remarks = forms.TextInput()


class SubmitNewFormMixin(SubmitFormfieldsMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
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


class SubmitNewSampleForm(SubmitNewFormMixin, forms.ModelForm):
    """
    For to submit a new sample to be measured by an expert.
    """

    def __init__(self, *args, **kwargs):
        self.exp_title = _('New Sample')
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            card(self.exp_title, backbutton),
            Row(
                Column('sample_name', css_class='col-6'),
                Column('sum_formula', css_class='col-6'),
                # Column('customer_samp'),  # not needed, because inherited by the login
            ),
            Row(
                Column('stable'),
            ),
            Row(
                Column('solve_refine_selve'),
            ),
            Row(
                Column('crystallization_conditions')
            ),
            Row(
                Column('reaction_path')
            ),
            Row(
                Column(
                    HTML("""
                    <div id="div_id_reaction_path" class="form-group">\n
                        <button class="btn btn-outline-secondary ml-3 mt-2 mr-1" type="button" data-toggle="collapse" 
                                data-target="#collapseKetcher" aria-expanded="false" aria-controls="collapseKetcher">
                                Alternatively, draw the Molecule
                        </button>
                        <!--<label for="id_svg_struct_samp" class="pr-3 pt-2 pb-0 mt-3 mb-0 ml-3">\n
                            Draw the desired structure<span class="asteriskField">*</span>\n
                        </label>\n-->
                        <small id="hint_id_reaction_path" class="form-text text-muted ml-3">
                            This is an alternative to the file upload above.
                        </small>\n
                        <input type="hidden" id="id_svg_struct_samp" value="" name="desired_struct_draw">\n
                        <div class="p-3 collapse" id="collapseKetcher">
                            <iframe id="ketcher-frame" src="ketcher.html">\n
                            </iframe>\n
                        </div>
                    </div>\n
                    """)),
            ),
            Row(
                Column('special_remarks')
            ),
            Row(
                submit_button,
            ),
            HTML('</div>'),  # end of card
        )

    def clean(self):
        """
        This runs after submitting the form. It makes sure at least one of the form reaction_path or
        desired_struct_draw has content.
        """
        cleaned_data = super().clean()
        figure_document = cleaned_data.get('reaction_path')
        svg_sample = cleaned_data.get('desired_struct_draw')
        if not any([figure_document, svg_sample]):
            raise ValidationError(_('You need to either upload a document with the desired structure '
                                    'or draw it in the field below.'))

    class Meta:
        model = Sample
        fields = '__all__'
