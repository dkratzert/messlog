from django.db import models
from django.utils.translation import gettext_lazy as _

from scxrd.models import Person


class SCXRDSample(models.Model):
    sample_name_samp = models.CharField(verbose_name=_('sample name'), max_length=200, blank=False, default='',
                                        unique=True)
    submit_date_samp = models.DateField(verbose_name=_('sample submission date'), blank=True, null=True)
    customer_samp = models.ForeignKey(verbose_name=_('Submitter'), to=Person, on_delete=models.DO_NOTHING, null=True,
                                      blank=True,
                                      related_name='SCXRDSample')
    stable_samp = models.BooleanField(verbose_name=_('Sample is Stable'),
                                      help_text=_('Indicate whether the sample needs special '
                                                'care in order to keep it stable'))
    solve_refine_selv_samp = models.BooleanField(verbose_name=_('I want to solve/refine myself'),
                                                 help_text=_('Indicate whether you want to solve and '
                                                           'refine the structure yourselves'))
    sum_formula_samp = models.CharField(max_length=300, verbose_name=_("assumed sum formula"), blank=True)
    reaction_path_samp = models.TextField(verbose_name=_('reaction pathway'), blank=True, null=True, default='')
    crystal_cond_samp = models.TextField(verbose_name=_('crystallized from and method'), blank=True, null=True, default='')
    # TODO: make this with Ketcher:
    desired_struct_samp = models.CharField(verbose_name=_('desired structure'), blank=True, default='', max_length=500)
    special_remarks_samp = models.TextField(verbose_name=_('special remarks'), blank=True, null=True, default='')
