import datetime

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

    def __str__(self):
        return self.name


# Editable lists of solvents and machines for the experiment:
#SOLVENT_NAMES = [(x.pk, x.__str__()) for x in Solvent.objects.all()]
MACHINE_NAMES = [(x.pk, x.__str__()) for x in Machine.objects.all()]

cif_fs = FileSystemStorage(location='/cif_files')

class Experiment(models.Model):
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default=None)
    number = models.IntegerField(verbose_name='number', unique=True, validators=[MinValueValidator(1)])
    date = models.DateTimeField(verbose_name='time of measurement', default=timezone.now)
    sum_formula = models.CharField(max_length=300, blank=True)
    solvents_used = models.ManyToManyField(Solvent, verbose_name='solvents used', blank=True)
    machine = models.IntegerField(verbose_name='machine used', choices=MACHINE_NAMES)

    class Meta:
        ordering = ["number"]

    def was_measured_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date <= now

    was_measured_recently.admin_order_field = 'date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def __str__(self):
        return self.experiment
