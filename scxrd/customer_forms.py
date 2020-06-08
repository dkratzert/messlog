from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django.utils.translation import gettext_lazy as _

from scxrd.customer_models import SCXRDSample
from scxrd.form_utils import save_button, card


class SubmitFormfieldsMixin(forms.ModelForm):
    submit_date_samp = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'), required=False,
                                       label=_("Sample submission date"))
    # TODO: do this during view save()
    # customer_samp = forms.ModelChoiceField(queryset=Person.objects.all(), required=True, label=_('customer'))
    # customer_samp = CurrentUserField(default=get_current_authenticated_user())
    sum_formula_samp = forms.CharField(label=_("Assumed sum formula"), required=True)
    crystal_cond_samp = forms.CharField(label=_('Crystallized from and method'), required=True)
    desired_struct_samp = forms.CharField(label=_('Desired structure'), required=True)
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
        self.backbutton = """
            <a role="button" class="btn btn-sm btn-outline-secondary float-right my-0 py-0" 
                href="{% url "scxrd:index"%}">Back to start</a>
            """


class SubmitNewForm(SubmitNewFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.exp_title = _('New Sample')
        super().__init__(*args, **kwargs)
        self.helper.render_unmentioned_fields = False
        self.helper.layout = Layout(
            card(self.exp_title, self.backbutton),
            Row(
                Column('sample_name_samp', css_class='col-6'),
                Column('sum_formula_samp', css_class='col-6'),
                # Column('customer_samp'),  # not needed, because inherited by the login
                # Column('measurement_temp'),
            ),
            Row(
                Column('stable_samp'),
                Column('solve_refine_selv_samp'),
            ),
            # Row(

            # Column('solve_refine_selv_samp'),
            # ),
            Row(
                Column('reaction_path_samp')
            ),
            Row(
                Column('crystal_cond_samp')
            ),
            Row(
                # Column('desired_struct_samp'),
                Column(HTML('<iframe id="ifKetcher" src="ketcher.html" width="400" height="300"></iframe>'),
                       css_class='p-3 m-2')
            ),
            Row(
                Column('special_remarks_samp')
            ),
            HTML('</div>'),  # end of card
            save_button,
            HTML('</br>'),
            HTML('</br>'),
            HTML('</br>'),
        )

    class Meta:
        model = SCXRDSample
        fields = '__all__'
