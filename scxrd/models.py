import datetime
import textwrap

import gemmi
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, EmailValidator, RegexValidator
from django.db import models
# Create your models here.
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.cif_model import CifFileModel
from scxrd.utils import COLOUR_CHOICES, COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES

"""
TODO:
- decide which cif resuduals do I really need? 
  wR2, R1, Space group, symmcards, atoms, cell, sumformula, completeness, Goof, temperature, Z, Rint, Peak/hole
- Add pdf/word upload for reaction conditions
- check checksum for correctness
- Measurement temperatue to experiment start page
- Upload save two files?
- Make upload work
- addd delete experiment
- improve details page
- for charts: https://www.chartjs.org/docs/latest/
- http://ccbv.co.uk/projects/Django/2.0
- cif is deleted from experiment when saving again!!
- Check for existing unit cell during cif upload.
- upload cif without input throws exception.
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


class Person(models.Model):
    """
    Persons where samples belong to.
    A Person is a Human that has no authentication.
    A Person does not need to have a User account.
    """
    # TODO: Check if this is a good idea:
    # user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, verbose_name='company', blank=True)
    work_group = models.ForeignKey('WorkGroup', related_name='person', max_length=200, blank=True, null=True,
                                   on_delete=models.DO_NOTHING)
    street = models.CharField(max_length=250, blank=True)
    house_number = models.CharField(max_length=200, blank=True)
    building = models.CharField(max_length=200, blank=True)
    town = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=200, blank=True)
    email_adress = models.EmailField(max_length=250, blank=True, validators=[validate_email])
    phone_number = models.CharField(max_length=17, blank=True
                                    # validators=[phone_validator],
                                    )
    comment = models.TextField(blank=True)

    def __str__(self):
        name = '{} {}'.format(self.first_name, self.last_name)
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
    group_head = models.OneToOneField(Person, related_name='group', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "AK {}".format(self.group_head.last_name)


class Machine(models.Model):
    """
    A diffractometer name and type.
    """
    fixtures = ['machines']
    # The make, model or name of the measurement device (goniometer) used:
    diffrn_measurement_device_type = models.CharField(verbose_name="machine model name", max_length=200)
    # The general class of goniometer or device used to support and orient the specimen:
    # e.g. 'three-circle diffractometer'
    diffrn_measurement_device = models.CharField(verbose_name="machine type", max_length=200, null=True, blank=True)
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


class CrystalShape(models.Model):
    """
    A description of the quality and habit of the crystal.
    """
    habitus = models.CharField(verbose_name='crystal shape', max_length=200, unique=True)

    def __str__(self):
        return self.habitus


class Experiment(models.Model):
    fixtures = ['experiment']
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default='', unique=True)
    number = models.PositiveIntegerField(verbose_name='number', unique=True, validators=[MinValueValidator(1)])
    publishable = models.BooleanField(verbose_name="structure is publishable", default=False)
    customer = models.ForeignKey(to=Person, on_delete=models.CASCADE, null=True, blank=True, related_name='experiment')
    # Operator has to be an authenticated User:
    operator = models.ForeignKey(User, verbose_name='operator', related_name='experiments', on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, verbose_name='diffractometer', on_delete=models.SET_NULL,
                                related_name='experiments', null=True, blank=True)
    sum_formula = models.CharField(max_length=300, verbose_name="assumed sum formula", blank=True)
    prelim_unit_cell = models.CharField(max_length=250, blank=True, verbose_name='first unit cell')
    solvents = models.CharField(verbose_name='solvents used', null=True, blank=True, max_length=256)
    conditions = models.CharField(verbose_name='reaction conditions', null=True, blank=True, max_length=1024)
    measure_date = models.DateTimeField(verbose_name='measurement date', default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name='sample submission date', blank=True, null=True)
    result_date = models.DateField(verbose_name='results sent date', blank=True, null=True)
    base = models.ForeignKey(CrystalSupport, verbose_name='sample base', related_name='+', blank=True, null=True,
                             on_delete=models.DO_NOTHING)
    glue = models.ForeignKey(CrystalGlue, verbose_name='sample glue', related_name='+', blank=True, null=True,
                             on_delete=models.DO_NOTHING)
    cif = models.OneToOneField(CifFileModel, null=True, blank=True, related_name="experiments",
                               verbose_name='cif file', on_delete=models.CASCADE)
    # equivalent to _exptl_crystal_size_max
    crystal_size_x = models.FloatField(verbose_name='crystal size max', null=True, blank=True)
    # equivalent to _exptl_crystal_size_mid
    crystal_size_y = models.FloatField(verbose_name='crystal size mid', null=True, blank=True)
    # equivalent to _exptl_crystal_size_min
    crystal_size_z = models.FloatField(verbose_name='crystal size min', null=True, blank=True)
    measurement_temp = models.FloatField(verbose_name='measurement temperature [K]', null=True, blank=True)
    # equivalent to _exptl_crystal_colour
    crystal_colour = models.IntegerField(choices=COLOUR_CHOICES, default=COLOUR_CHOICES[0][0])
    # equivalent to _exptl_crystal_colour_modifier
    crystal_colour_mod = models.IntegerField(choices=COLOUR_MOD_CHOICES, verbose_name='crystal colour modifier',
                                             default=COLOUR_MOD_CHOICES[0][0])
    # equivalent to _exptl_crystal_colour_lustre
    crystal_colour_lustre = models.IntegerField(choices=COLOUR_LUSTRE_COICES,
                                                default=COLOUR_LUSTRE_COICES[0][0])  # no blank=True here!
    # equivalent to _exptl_crystal_description
    crystal_habit = models.CharField(max_length=300, blank=True, null=True, verbose_name="crystal habit")
    # _exptl_special_details:
    exptl_special_details = models.TextField(verbose_name='experimental special details', blank=True, null=True,
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

    def get_choice(self, choices, attibute, na_0=True):
        """
        Get the choice value from a choices field.
        :param choices: The choice dictionary
        :param attibute: the attribute to retrieve from the choice
        :param na_0: Decide wether 0 should be translated to '?' or not.
        :return: Choice value
        """
        value = getattr(self, attibute)
        if na_0:
            if value == 0:
                return '?'
            else:
                return choices[value][1]
        else:
            return choices[value][1]

    @staticmethod
    def quote_string(string):
        """
        Quotes the string value in a way that the line maximum of cif 1.1 with 2048 characters is fulfilled and longer
        strings are embedded into ; quotes.
        :param string: The string to save
        :return: a quoted string
        """
        if not string:
            return '?'
        if isinstance(string, (int, float)):
            return str(string)
        if not isinstance(string, (str)):
            # To get the string representation of model instances first:
            string = str(string)
        if len(string) < 2047 and (not '\n' in string or not '\r' in string):
            return "'{}'".format(string)
        else:
            return ";{}\n;".format('\n'.join(textwrap.wrap(string, width=2047)))


