import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, EmailValidator, RegexValidator
from django.db import models
# Create your models here.
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pip._vendor.colorama import initialise

from scxrd.cif_model import CifFile
from scxrd.utils import COLOUR_CHOICES, COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES

"""
TODO:

- addd delete experiment
- improve details page
- add upload results dropdown
- A really simple file upload handler: https://github.com/ipartola/django-upman
- https://github.com/sibtc/form-rendering-examples
- upload all needed files from work dir (foo.abs, foo.raw, foo_0m._ls, foo.prp, foo.lst, foo.res, foo.cif) and 
  have a button "generate report and final cif files"
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


class Person(models.Model):
    """
    Persons where samples belong to.
    A Person is a Human that has no authentication.
    A Person does not need to have a User account.
    """
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
    A work group is a group of Person() with a leading group_head (which is also a Person).
    """
    group_head = models.OneToOneField(Person, related_name='group', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "AK {}".format(self.group_head.last_name)


class Machine(models.Model):
    fixtures = ['machines']
    name = models.CharField(verbose_name="machines name", max_length=200)

    def __str__(self):
        return self.name


class Solvent(models.Model):
    fixtures = ['solvents.json']
    name = models.CharField(verbose_name="solvents name", max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CrystalSupport(models.Model):
    """
    How was it mounted?
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
    number = models.IntegerField(verbose_name='number', unique=True, validators=[MinValueValidator(1)])
    publishable = models.BooleanField(verbose_name="structure is publishable", default=False)
    customer = models.ForeignKey(to=Person, on_delete=models.CASCADE, null=True, blank=True, related_name='experiment')
    # Operator has to be an authenticated User:
    operator = models.ForeignKey(User, verbose_name='operator', related_name='experiments', on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, verbose_name='diffractometer', on_delete=models.SET_NULL,
                                related_name='experiments', null=True, blank=True)
    sum_formula = models.CharField(max_length=300, blank=True)
    solvent1 = models.ForeignKey(Solvent, verbose_name='solvent 1', null=True, blank=True,
                                 related_name='experiment1', on_delete=models.CASCADE, default='')
    solvent2 = models.ForeignKey(Solvent, verbose_name='solvent 2', null=True, blank=True,
                                 related_name='experiment2', on_delete=models.CASCADE, default='')
    solvent3 = models.ForeignKey(Solvent, verbose_name='solvents 3', null=True, blank=True,
                                 related_name='experiment3', on_delete=models.CASCADE, default='')
    measure_date = models.DateTimeField(verbose_name='measurement date', default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name='sample submission date', blank=True, null=True)
    result_date = models.DateField(verbose_name='results sent date', blank=True, null=True)
    base = models.ForeignKey(CrystalSupport, verbose_name='sample base', related_name='+', blank=True, null=True,
                             on_delete=models.DO_NOTHING)
    glue = models.ForeignKey(CrystalGlue, verbose_name='sample glue', related_name='+', blank=True, null=True,
                             on_delete=models.DO_NOTHING)
    cif = models.OneToOneField(CifFile, null=True, blank=True, related_name="experiments",
                               verbose_name='cif file', on_delete=models.CASCADE)
    crystal_colour = models.IntegerField(choices=COLOUR_CHOICES, default=COLOUR_CHOICES[0][0])
    crystal_colour_mod = models.IntegerField(choices=COLOUR_MOD_CHOICES, verbose_name='crystal colour modifier',
                                             default=COLOUR_MOD_CHOICES[0][0])
    crystal_colour_lustre = models.IntegerField(choices=COLOUR_LUSTRE_COICES,
                                                default=COLOUR_LUSTRE_COICES[0][0])  # no blank=True here!
    # _exptl_special_details:
    special_details = models.TextField(verbose_name='experimental special details', blank=True, null=True, default='')

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
