import datetime

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import User

from utils import COLOUR_CHOICES, COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES
from .cif_model import CifFile, Atom

# from django.contrib.auth.models import AbstractUser, UserManager


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


class CrystalGlue(models.Model):
    """
    What kind of addhesive was used?
    """
    glue = models.CharField(verbose_name='crystal glue', max_length=200, unique=True)


class CrystalShape(models.Model):
    """
    A description of the quality and habit of the crystal.
    """
    habitus = models.CharField(verbose_name='crystal shape', max_length=200, unique=True)


class Customer(models.Model):
    """
    Persons where samples belong to.
    """
    name = models.CharField(verbose_name='first name', max_length=250, blank=True, null=True)
    last_name = models.CharField(verbose_name='last name', max_length=250, blank=False, null=False)
    workgroup = models.CharField(verbose_name='work group', max_length=250, blank=True, null=True)
    company = models.CharField(verbose_name='company', max_length=250, blank=True, null=True)
    mail_adress = models.EmailField(null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: "
                                         "'+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list

    def __str__(self):
        return '{} {}'.format(self.name, self.last_name)


class Experiment(models.Model):
    fixtures = ['experiment']
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default='')
    number = models.IntegerField(verbose_name='number', unique=True, validators=[MinValueValidator(1)])
    customer = models.ForeignKey(to=Customer, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO: Change to MyUser for case insensitive usernames:
    operator = models.ForeignKey(User, verbose_name='operator', related_name='experiments',
                                 on_delete=models.SET_NULL, null=True, blank=True)
    machine = models.OneToOneField(Machine, verbose_name='diffractometer', on_delete=models.SET_NULL,
                                   related_name='experiments', null=True, blank=True)
    sum_formula = models.CharField(max_length=300, blank=True)
    solvents_used = models.ManyToManyField(Solvent, verbose_name='solvents used', blank=True)
    measure_date = models.DateTimeField(verbose_name='measurement date', default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name='sample submission date', blank=True, null=True)
    result_date = models.DateField(verbose_name='structure results date', blank=True, null=True)
    base = models.ForeignKey(CrystalSupport, verbose_name='sample base', related_name='+', blank=True, null=True,
                             on_delete=models.DO_NOTHING)
    glue = models.ForeignKey(CrystalGlue, verbose_name='sample glue', related_name='+', blank=True, null=True,
                             on_delete=models.DO_NOTHING)
    cif = models.OneToOneField(CifFile, null=True, blank=True, related_name="experiments",
                               verbose_name='cif file', on_delete=models.CASCADE)
    crystal_colour = models.IntegerField(choices=COLOUR_CHOICES, default=0)
    crystal_colour_mod = models.IntegerField(choices=COLOUR_MOD_CHOICES, default=0)
    crystal_colour_lustre = models.IntegerField(choices=COLOUR_LUSTRE_COICES, default=0)
    #_exptl_special_details:
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

