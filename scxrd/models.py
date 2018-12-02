import datetime

from django.db import models

# Create your models here.
from django.utils import timezone


class Machine(models.Model):
    name = models.CharField(verbose_name="machines name", max_length=200)

    def __str__(self):
        return self.name


class Solvent(models.Model):
    name = models.CharField(verbose_name="solvents name", max_length=200)

    def __str__(self):
        return self.name


# Editable lists of solvents and machines for the experiment:
SOLVENT_NAMES = [(x.pk, x.__str__()) for x in Solvent.objects.all()]
MACHINE_NAMES = [(x.pk, x.__str__()) for x in Machine.objects.all()]


class Experiment(models.Model):
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default=None)
    date = models.DateTimeField(verbose_name='time of measurement', default=timezone.now)
    number = models.IntegerField(verbose_name='number', unique=True)
    sum_formula = models.CharField(max_length=300)
    solvents_used = models.IntegerField(verbose_name='solvents used', choices=SOLVENT_NAMES)
    machine = models.IntegerField(verbose_name='machine used', choices=MACHINE_NAMES)

    def was_measured_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date <= now

    was_measured_recently.admin_order_field = 'date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def __str__(self):
        return self.experiment
