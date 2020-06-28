from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_reaction_file_extension(value):
    ext = value.name.split('.')[-1]
    if ext and ext.lower() not in ['docx', 'pdf', 'cdx']:
        raise ValidationError(_('Files with this extension are not allowed to upload here.'))


class SCXRDSample(models.Model):
    sample_name_samp = models.CharField(verbose_name=_('sample name'), max_length=200, blank=False, null=False,
                                        unique=True, help_text=_('A unique nae of your sample'))
    # The date when the sample is submitted to the facility:
    submit_date_samp = models.DateField(verbose_name=_('sample submission date'), blank=True, null=True,
                                        default=timezone.now)
    customer_samp = models.ForeignKey(to=User, verbose_name=_('Submitter'), on_delete=models.SET_NULL, null=True,
                                      blank=True,
                                      related_name='SCXRDSample')
    stable_samp = models.BooleanField(verbose_name=_('sample is unstable'),
                                      help_text=_("Indicate if the sample requires special care "
                                                  "to keep it stable until the measurement. "
                                                  "Tell us more in the "
                                                  "'special remarks' field."))
    solve_refine_selv_samp = models.BooleanField(verbose_name=_('I want to solve/refine'),
                                                 help_text=_('Indicate whether you want to solve and '
                                                             'refine the structure yourselves.'))
    sum_formula_samp = models.CharField(max_length=300, verbose_name=_("assumed sum formula"), blank=True)
    reaction_path_samp = models.FileField(
        verbose_name=_('Document with reaction pathway, desired molecule and conditions'),
        validators=[validate_reaction_file_extension],
        upload_to='reactions',
        blank=True,
        null=True
    )
    crystal_cond_samp = models.CharField(verbose_name=_('crystallized from, method and conditions'), blank=True,
                                         null=True,
                                         default='', max_length=500)
    desired_struct_samp = models.TextField(verbose_name=_('desired structure'), blank=True, default='')
    special_remarks_samp = models.TextField(verbose_name=_('special remarks'), blank=True, null=True, default='',
                                            help_text=_('Any additional information we should know.'))
    was_measured = models.BooleanField(verbose_name=_('The sample was measured successfully'), default=False)
    not_measured_cause = models.TextField(verbose_name=_('Not measured, because:'), blank=True, default='',
                                          help_text=_('The cause why the sample could not be measured'))

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.sample_name_samp
