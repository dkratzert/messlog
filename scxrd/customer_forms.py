from crispy_forms.layout import Layout, HTML
from django import forms

from scxrd.customer_models import SCXRDSample
from scxrd.forms import ExperimentFormMixin


class ExperimentNewForm(ExperimentFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.exp_title = 'New Sample'
        super().__init__(*args, **kwargs)
        self.helper.render_unmentioned_fields = True

        self.helper.layout = Layout(
            # Experiment ###
            #self.experiment_layout,
            #self.crystal_colour_layout,
            #self.sumform_row,
            #HTML('</div>'),  # end of card
            #self.save_button,
            # HTML('</div>'),  # end of card
        )

    class Meta:
        model = SCXRDSample
        fields = '__all__'
