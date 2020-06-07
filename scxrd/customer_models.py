from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SCXRDSample(models.Model):
    sample_name_samp = models.CharField(verbose_name=_('sample name'), max_length=200, blank=False, default='',
                                        unique=True)
    # The date when the sample is submitted to the facility:
    submit_date_samp = models.DateField(verbose_name=_('sample submission date'), blank=True, null=True,
                                        default=timezone.now)
    customer_samp = models.ForeignKey(verbose_name=_('Submitter'), to=User, on_delete=models.SET_NULL, null=True,
                                      blank=True,
                                      related_name='SCXRDSample')
    stable_samp = models.BooleanField(verbose_name=_('sample is unstable'),
                                      help_text=_("Indicate whether the sample needs special "
                                                  "care in order to keep it stable. Tell us more in the "
                                                  "'special remarks' field."))
    solve_refine_selv_samp = models.BooleanField(verbose_name=_('I want to solve/refine'),
                                                 help_text=_('Indicate whether you want to solve and '
                                                             'refine the structure yourselves'))
    sum_formula_samp = models.CharField(max_length=300, verbose_name=_("assumed sum formula"), blank=True)
    reaction_path_samp = models.TextField(verbose_name=_('reaction pathway'), blank=True, null=True, default='')
    crystal_cond_samp = models.CharField(verbose_name=_('crystallized from and method'), blank=True, null=True,
                                         default='', max_length=500)
    # TODO: make this with Ketcher:
    desired_struct_samp = models.CharField(verbose_name=_('desired structure'), blank=True, default='', max_length=500)
    special_remarks_samp = models.TextField(verbose_name=_('special remarks'), blank=True, null=True, default='')
