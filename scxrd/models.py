import datetime

from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, EmailValidator, RegexValidator
from django.db import models
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.cif_model import CifFileModel
from scxrd.utils import COLOUR_CHOICES, COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES

"""
TODO:
- "New Experiment page" from "measure a sample" is missing the sum formula and crystal habit 
    and special remarks and "not measure cause"
- measure sample seems to use the wrong pk?
- Save current user during save of "new experiment
- "new experiment does not need the customer field
- edit experiment: "Solvents used" and "Reaction conditions" must be adapted
    - svg of molecule is not displayed
- check checksum for correctness during file upload and download
- addd delete experiment -> No, this is only for admins
- Check for existing unit cell during cif upload.
- for charts: https://www.chartjs.org/docs/latest/
- http://ccbv.co.uk/projects/Django/2.0

"""


def validate_email(value):
    """
    Validate that a username is email like.
    """
    _validate_email = EmailValidator()
    try:
        _validate_email(value)
    except ValidationError:
        raise ValidationError(_('Enter a valid email address.'))
    return value


phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: "
                                         "'+999999999'. Up to 15 digits allowed.")


class Profile(models.Model):
    """
    Persons where samples belong to.
    A Person is a Human that has no authentication.
    A Person does not need to have a User account.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=200, verbose_name=_('company'), blank=True)
    work_group = models.ForeignKey('WorkGroup', blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name='profiles')
    street = models.CharField(max_length=250, blank=True, null=True)
    house_number = models.CharField(max_length=200, blank=True, null=True)
    building = models.CharField(max_length=200, blank=True, null=True)
    town = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    postal_code = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=17, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        name = '{} {}'.format(self.user.first_name, self.user.last_name)
        try:
            self.work_group.group_head
        except AttributeError:
            return name
        else:
            if self.work_group.group_head == self:
                return name + '*'
            else:
                return name


class WorkGroup(models.Model):
    """
    A work group is a group of Person()s with a leading group_head (which is also a Person).
    """
    fixtures = ['work_groups']
    group_head = models.CharField(verbose_name=_('work group head'), max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return "AK {}".format(self.group_head)


class Machine(models.Model):
    """
    A diffractometer name and type.
    """
    fixtures = ['machines']
    # The make, model or name of the measurement device (goniometer) used:
    diffrn_measurement_device_type = models.CharField(verbose_name="machine model name", max_length=200)
    # The general class of goniometer or device used to support and orient the specimen:
    # e.g. 'three-circle diffractometer'
    diffrn_measurement_device = models.CharField(verbose_name=_("machine type"), max_length=200, null=True, blank=True)
    # A description of special aspects of the device used to measure the diffraction intensities:
    diffrn_measurement_device_details = models.CharField(verbose_name="machine special aspects",
                                                         max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.diffrn_measurement_device_type


class CrystalSupport(models.Model):
    """
    The support where the crystal was mounted on the diffraktometer.
    _diffrn_measurement_specimen_support e.g. 'glass capillary'
    """
    support = models.CharField(verbose_name='crystal support', max_length=200, unique=True)

    def __str__(self):
        return self.support


class CrystalGlue(models.Model):
    """
    What kind of addhesive was used?
    """
    glue = models.CharField(verbose_name='crystal glue', max_length=200, unique=True)

    def __str__(self):
        return self.glue


class Experiment(models.Model):
    fixtures = ['experiment']
    experiment = models.CharField(verbose_name=_('experiment name'), max_length=200, blank=False, default='',
                                  unique=True)
    number = models.PositiveIntegerField(verbose_name=_('number'), unique=True, validators=[MinValueValidator(1)])
    publishable = models.BooleanField(verbose_name=_("structure is publishable"), default=False)
    customer = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='customer_experiments')
    # Operator has to be an authenticated User:
    operator = models.ForeignKey(to=User, verbose_name=_('operator'), null=True, related_name='operator_experiments',
                                 on_delete=models.SET_NULL)
    machine = models.ForeignKey(Machine, verbose_name=_('diffractometer'), on_delete=models.SET_NULL,
                                related_name='experiments', null=True, blank=True)
    sum_formula = models.CharField(max_length=300, verbose_name=_("presumed empirical formula"), blank=True)
    prelim_unit_cell = models.CharField(max_length=250, blank=True, verbose_name=_('first unit cell'))
    solvents = models.CharField(verbose_name=_('solvents used'), null=True, blank=True, max_length=256)
    conditions = models.CharField(verbose_name=_('reaction conditions'), null=True, blank=True, max_length=1024)
    measure_date = models.DateTimeField(verbose_name=_('measurement date'), default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name=_('sample submission date'), blank=True, null=True)
    result_date = models.DateField(verbose_name=_('results sent date'), blank=True, null=True)
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
    crystal_habit = models.CharField(max_length=300, blank=True, null=True, verbose_name=_("crystal habit"))
    # _exptl_special_details:
    exptl_special_details = models.TextField(verbose_name=_('special remarks'), blank=True, null=True,
                                             default='')

    class Meta:
        ordering = ["-number"]

    def was_measured_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=2) <= self.measure_date <= now

    was_measured_recently.admin_order_field = 'measure_date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def __str__(self):
        return self.experiment


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
