from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from scxrd.customer_models import SCXRDSample
from scxrd.form_utils import card, save_button2, backbutton


class SubmitFormfieldsMixin(forms.ModelForm):
    submit_date_samp = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'), required=False,
                                       label=_("Sample submission date"))
    # TODO: do this during view save()
    # customer_samp = forms.ModelChoiceField(queryset=Person.objects.all(), required=True, label=_('customer'))
    # customer_samp = CurrentUserField(default=get_current_authenticated_user())
    sum_formula_samp = forms.CharField(label=_("Presumed sum formula"), required=True)
    crystal_cond_samp = forms.CharField(label=_('Crystallized from, method and conditions'), required=True)
    reaction_path_samp = forms.FileField(label=_('Document with reaction pathway, desired molecule and conditions'),
                                         required=False,
                                         help_text=_("Please upload a document (.docx, .cdx or .pdf) showing the "
                                                     "reaction path with the "
                                                     "desired product including all used solvents and other reagents. "
                                                     "<br>The solvents are important information for us if they crystallize "
                                                     "along with the main molecule.")
                                         )
    desired_struct_samp = forms.CharField(label=_('Desired structure'), required=False)
    special_remarks_samp = forms.TextInput()


class SubmitNewFormMixin(SubmitFormfieldsMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # self.helper.form_action = reverse_lazy('scxrd:index', )
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


class SubmitNewForm(SubmitNewFormMixin, forms.ModelForm):
    """
    For to submit a new sample to be measured by an expert.
    """

    def __init__(self, *args, **kwargs):
        self.exp_title = _('New Sample')
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            card(self.exp_title, backbutton),
            Row(
                Column('sample_name_samp', css_class='col-6'),
                Column('sum_formula_samp', css_class='col-6'),
                # Column('customer_samp'),  # not needed, because inherited by the login
            ),
            Row(
                Column('stable_samp'),
                # Column('solve_refine_selv_samp'),
            ),
            Row(
                Column('solve_refine_selv_samp'),
            ),
            Row(
                Column('crystal_cond_samp')
            ),
            Row(
                Column('reaction_path_samp')
            ),
            Row(
                # jsme_frame,
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
                    """)),
            ),
            Row(
                Column('special_remarks_samp')
            ),
            Row(
                save_button2,
            ),
            HTML('</div>'),  # end of card
            # HTML('<div onLoad="self.scrollTo(0,0)"></div>'),
        )

    def clean(self):
        """
        This runs after submitting the form. It makes sure at least one of the form reaction_path_samp or
        desired_struct_samp has content.
        """
        # TODO: make a custom form where the model is coupled to the form field and the html template
        cleaned_data = super().clean()
        figure_document = cleaned_data.get('reaction_path_samp')
        svg_sample = cleaned_data.get('desired_struct_samp')
        if not any([figure_document, svg_sample]):
            raise ValidationError(_('You need to either upload a document with the desired structure '
                                    'or draw it in the field below.'))

    class Meta:
        model = SCXRDSample
        fields = '__all__'
