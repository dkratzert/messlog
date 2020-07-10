from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.models import sample_name_validator


def validate_reaction_file_extension(value):
    ext = value.name.split('.')[-1]
    if ext and ext.lower() not in ['docx', 'pdf', 'cdx']:
        raise ValidationError(_('Files with this extension are not allowed to upload here.'))


class Sample(models.Model):
    # TODO: make sure that no samples can be created in the future and not too far in the past. 
    sample_name = models.CharField(verbose_name=_('sample name'), max_length=200, blank=False, unique=True,
                                   help_text=_('A unique name of your sample'), validators=[sample_name_validator])
    # The date when the sample is submitted to the facility:
    submit_date = models.DateField(verbose_name=_('sample submission date'), blank=True, null=True,
                                   default=timezone.now)
    customer_samp = models.ForeignKey(to=User, verbose_name=_('Submitter'), on_delete=models.SET_NULL, null=True,
                                      blank=True,
                                      related_name='Sample')
    stable = models.BooleanField(verbose_name=_('sample is sensitive (temperature, oxygen, moisture)'),
                                 help_text=_("The sample requires special precautions to remain stable "
                                             "until measurement."))
    solve_refine_selve = models.BooleanField(verbose_name=_('I want to solve/refine by myself'),
                                             help_text=_('Indicate whether you want to solve and '
                                                         'refine the structure by yourselves.'))
    sum_formula = models.CharField(max_length=300, verbose_name=_("assumed sum formula"), blank=True)
    reaction_path = models.FileField(
        verbose_name=_('Document with reaction equation and conditions'),
        validators=[validate_reaction_file_extension],
        upload_to='reactions',
        blank=True,
        null=True
    )
    crystallization_conditions = models.CharField(blank=True, max_length=500, 
                                                  verbose_name=_('Solvents used for crystallization, '
                                                                 'method, conditions'))
    desired_struct_draw = models.TextField(verbose_name=_('desired structure'), blank=True, default='')
    mol_file = models.TextField(verbose_name=_('MOL file of the structure'), blank=True, default='')
    special_remarks = models.TextField(verbose_name=_('special remarks'), blank=True,
                                       help_text=_('Any additional information we should know.'))

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.sample_name

    def was_measured(self):
        return any([x.was_measured for x in self.experiments])