from django.db import models

# Create your models here.
from django.utils import timezone


class Machine(models.Model):
    name = models.CharField(verbose_name="sachines name", max_length=200)

    def __str__(self):
        return self.name

class Solvent(models.Model):
    name = models.CharField(verbose_name="solvents name", max_length=200)

    def __str__(self):
        return self.name

class Experiment(models.Model):
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default=None)
    date = models.DateTimeField(verbose_name='time of measurement', default=timezone.now)
    number = models.IntegerField(verbose_name='number', unique=True)
    sum_formula = models.CharField(max_length=300)
    solvents_used =
    MACHINE_NAMES = [(x.pk, x) for x in Machine.objects.all() if Machine]
    #MACHINE_NAMES = [(1, 'Foo'),(2, 'Bar'),(3, 'APEX')]
    machine = models.IntegerField(verbose_name='machine used', choices=MACHINE_NAMES, blank=False, default='Select '
                                                                                                           'Machine')

    def __str__(self):
        return self.experiment




