import datetime

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
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


# Editable lists of solvents and machines for the experiment:
#SOLVENT_NAMES = [(x.pk, x.__str__()) for x in Solvent.objects.all()]
MACHINE_NAMES = [(x.pk, x.__str__()) for x in Machine.objects.all()]

cif_fs = FileSystemStorage(location='/cif_files')


class Experiment(models.Model):
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default=None)
    number = models.IntegerField(verbose_name='number', unique=True, validators=[MinValueValidator(1)])
    machine = models.IntegerField(verbose_name='diffractometer', choices=MACHINE_NAMES)
    sum_formula = models.CharField(max_length=300, blank=True)
    solvents_used = models.ManyToManyField(Solvent, verbose_name='solvents used', blank=True)
    measure_date = models.DateTimeField(verbose_name='measurement date', default=timezone.now)
    submit_date = models.DateTimeField(verbose_name='sample submission date', default=timezone.now)
    result_date = models.DateTimeField(verbose_name='structure results date', default=timezone.now)
    owner = models.ForeignKey(User, verbose_name='owner', related_name='experiment', on_delete=models.CASCADE)

    class Meta:
        ordering = ["number"]

    def was_measured_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.measure_date <= now

    was_measured_recently.admin_order_field = 'date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def __str__(self):
        return self.experiment
