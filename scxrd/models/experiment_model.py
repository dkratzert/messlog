import datetime

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ProtectedError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.models.models import sample_name_validator, Machine, resolution_validator, CrystalSupport, CrystalGlue
from scxrd.utils import COLOUR_CHOICES, COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES


class Experiment(models.Model):
    # The name of the current experiment
    experiment_name = models.CharField(verbose_name=_('experiment name'), max_length=200, blank=False, unique=True,
                                       validators=[sample_name_validator])
    # Makes the sample measurement status visible through the experiment status:
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='experiments')
    number = models.PositiveIntegerField(verbose_name=_('number'), unique=True, validators=[MinValueValidator(1)])
    publishable = models.BooleanField(verbose_name=_("structure is publishable"), default=False)
    # The user who submitted a respective sample
    customer = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=_("customer (for service)"), related_name='customer_experiments')
    # Operator has to be an authenticated User:
    operator = models.ForeignKey(to=User, verbose_name=_('operator'), null=True, related_name='operator_experiments',
                                 on_delete=models.SET_NULL)
    machine = models.ForeignKey(Machine, verbose_name=_('diffractometer'), on_delete=models.SET_NULL,
                                related_name='experiments', null=True, blank=True)
    sum_formula = models.CharField(max_length=300, verbose_name=_("empirical formula"), blank=True)
    prelim_unit_cell = models.CharField(max_length=250, blank=True, verbose_name=_('first unit cell'))
    resolution = models.FloatField(verbose_name=_('Resolution [&#x212b;]'), null=True, blank=True,
                                   validators=(resolution_validator,))
    conditions = models.TextField(verbose_name=_('reaction conditions'), blank=True)
    measure_date = models.DateTimeField(verbose_name=_('measurement date'), default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name=_('sample submission date'), blank=True, null=True)
    result_date = models.DateField(verbose_name=_('results sent date'), blank=True, null=True)
    end_time = models.DateTimeField(verbose_name=_('expected end date and time of the experiment'), blank=False)
    base = models.ForeignKey(CrystalSupport, verbose_name=_('sample base'), blank=True, null=True,
                             on_delete=models.DO_NOTHING, related_name='experiments')
    glue = models.ForeignKey(CrystalGlue, verbose_name=_('sample glue'), related_name='experiments', blank=True,
                             null=True,
                             on_delete=models.DO_NOTHING)
    # equivalent to _exptl_crystal_size_max
    crystal_size_x = models.FloatField(verbose_name=_('crystal size max'), null=True, blank=True)
    # equivalent to _exptl_crystal_size_mid
    crystal_size_y = models.FloatField(verbose_name=_('crystal size mid'), null=True, blank=True)
    # equivalent to _exptl_crystal_size_min
    crystal_size_z = models.FloatField(verbose_name=_('crystal size min'), null=True, blank=True)
    measurement_temp = models.FloatField(verbose_name=_('measurement temperature [K]'), null=True, blank=True)
    # equivalent to _exptl_crystal_colour
    crystal_colour = models.IntegerField(choices=COLOUR_CHOICES, default=COLOUR_CHOICES[0][0])
    # equivalent to _exptl_crystal_colour_modifier
    crystal_colour_mod = models.IntegerField(choices=COLOUR_MOD_CHOICES, verbose_name=_('crystal colour modifier'),
                                             default=COLOUR_MOD_CHOICES[0][0])
    # equivalent to _exptl_crystal_colour_lustre
    crystal_colour_lustre = models.IntegerField(choices=COLOUR_LUSTRE_COICES,
                                                default=COLOUR_LUSTRE_COICES[0][0])  # no blank=True here!
    # equivalent to _exptl_crystal_description
    crystal_habit = models.CharField(max_length=300, blank=True, verbose_name=_("crystal habit"))
    # _exptl_special_details:
    exptl_special_details = models.TextField(verbose_name=_('special remarks'), blank=True, default='')
    was_measured = models.BooleanField(verbose_name=_('The sample was measured successfully'), default=False, null=True,
                                       blank=True)
    not_measured_cause = models.TextField(verbose_name=_('Not measured, because:'), blank=True,
                                          help_text=_('The cause why the sample could not be measured'))
    # After setting final to True, the experiment is write protected:
    final = models.BooleanField(default=False)

    class Meta:
        ordering = ["-number"]

    def was_measured_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=2) <= self.measure_date <= now

    def measured_last_year(self):
        now = timezone.now()
        return now - datetime.timedelta(days=365) <= self.measure_date <= now

    was_measured_recently.admin_order_field = 'measure_date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def __str__(self):
        return self.experiment_name


@receiver(pre_delete, sender=Experiment)
def delete_protect_handler(sender, instance: Experiment, **kwargs):
    """
    Delete protection for finished projects.
    """
    if hasattr(instance, 'final') and instance.final:
        raise ProtectedError('This Experiment can not be changed anymore.', instance)