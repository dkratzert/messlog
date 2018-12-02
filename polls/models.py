import datetime

from django import forms
from django.db import models

# Create your models here.
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(verbose_name='date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Machine(models.Model):
    name = models.CharField(verbose_name="Machines name", max_length=200, blank=False)

    def __str__(self):
        return self.name


class Measurement(models.Model):
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False)
    date = models.DateTimeField(verbose_name='time of measurement', default=timezone.now)
    MACHINE_NAMES = [(x.pk, x) for x in Machine.objects.all() if Machine]
    #MACHINE_NAMES = [(1, 'Foo'),(2, 'Bar'),(3, 'APEX')]
    used_machine = models.IntegerField(choices=MACHINE_NAMES)

    def __str__(self):
        return self.experiment

