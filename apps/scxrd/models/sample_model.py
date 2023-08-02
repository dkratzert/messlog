from pathlib import Path

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.scxrd.models.models import sample_name_validator


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
                                 help_text=_("Please indicate in the notes which conditions are necessary to keep the sample stable."))
    solve_refine_selve = models.BooleanField(verbose_name=_('I want to solve/refine by myself'))
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
    history = HistoricalRecords()

    class Meta:
        ordering = ["id"]
        verbose_name = _('Sample')
        verbose_name_plural = _('Samples')

    def __str__(self):
        return self.sample_name

    @property
    def reaction_path_file_path(self) -> Path:
        """The complete absolute path of the CIF file with file name and ending"""
        try:
            return Path(str(self.reaction_path.file))
        except FileNotFoundError:
            return Path()

    @property
    def reaction_path_file_name_only(self) -> str:
        """The CIF file name without path"""
        return self.reaction_path_file_path.name

    def was_measured(self):
        if not self.measurements:
            return False
        return any([x.was_measured for x in self.measurements.all()])

    was_measured.boolean = True