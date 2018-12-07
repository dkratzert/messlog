import datetime

from django_tables2 import tables

"""
TODO:

- addd delete experiment
- improve details page
- add upload results dropdown

"""

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator
from django.db import models, utils

# Create your models here.
from django.forms import widgets
from django.utils import timezone


class Machine(models.Model):
    name = models.CharField(verbose_name="machines name", max_length=200)

    def __str__(self):
        return self.name


class Solvent(models.Model):
    name = models.CharField(verbose_name="solvents name", max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


cif_fs = FileSystemStorage(location='/cif_files')


class Experiment(models.Model):
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default=None)
    number = models.IntegerField(verbose_name='number', unique=True, validators=[MinValueValidator(1)])
    machine = models.ForeignKey(to=Machine, verbose_name='diffractometer', parent_link=True, on_delete=models.CASCADE)
    sum_formula = models.CharField(max_length=300, blank=True)
    solvents_used = models.ManyToManyField(Solvent, verbose_name='solvents used', blank=True)
    measure_date = models.DateTimeField(verbose_name='measurement date', default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name='sample submission date', blank=True, null=True)
    result_date = models.DateField(verbose_name='structure results date', blank=True, null=True)
    operator = models.ForeignKey(User, verbose_name='operator', related_name='experiment', on_delete=models.CASCADE, default=1)

    class Meta:
        ordering = ["number"]

    def was_measured_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=2) <= self.measure_date <= now

    was_measured_recently.admin_order_field = 'measure_date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def __str__(self):
        return self.experiment


