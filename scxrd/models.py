import datetime
import hashlib


"""
TODO:

- addd delete experiment
- improve details page
- add upload results dropdown
- A good file upload handler: https://github.com/divio/django-filer
- A really simple file upload handler: https://github.com/ipartola/django-upman
- https://github.com/sibtc/form-rendering-examples
- upload all needed files from work dir (foo.abs, foo.raw, foo_0m._ls, foo.prp, foo.lst, foo.res, foo.cif) and 
  have a button "generate report and final cif files"
- for charts: https://www.chartjs.org/docs/latest/
- http://ccbv.co.uk/projects/Django/2.0
"""

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

# Create your models here.
from django.utils import timezone


def generate_sha1(file):
    f = file.open('rb')
    hash = hashlib.sha1()
    if f.multiple_chunks():
        for chunk in f.chunks(chunk_size=64 * 2 ** 10):
            hash.update(chunk)
    else:
        hash.update(f.read())
    f.close()
    sha1 = hash.hexdigest()
    return sha1


class CifFile(models.Model):
    cif = models.FileField(upload_to='cifs', null=True, blank=True)
    sha1 = models.CharField(max_length=256, blank=True, null=True)
    filesize = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(CifFile, self).save(*args, **kwargs)
        # f = self.cif.open('rb')
        checksum = generate_sha1(self.cif.file)
        self.filesize = self.cif.size
        #inst = self.objects.get().filter(sha1=checksum).first()
        #if inst:
        #    return inst
        self.sha1 = checksum
        super(CifFile, self).save(*args, **kwargs)

    def __str__(self):
        return self.cif.url

    def delete(self, *args, **kwargs):
        self.cif.delete()
        super().delete(*args, **kwargs)


class Machine(models.Model):
    fixtures = ['machines']
    name = models.CharField(verbose_name="machines name", max_length=200)

    def __str__(self):
        return self.name


class Solvent(models.Model):
    name = models.CharField(verbose_name="solvents name", max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


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
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default=None)
    number = models.IntegerField(verbose_name='number', unique=True, validators=[MinValueValidator(1)])
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE, null=True, blank=True)
    machine = models.ForeignKey(to=Machine, verbose_name='diffractometer', parent_link=True,
                                on_delete=models.CASCADE, null=True, blank=True)
    sum_formula = models.CharField(max_length=300, blank=True)
    solvents_used = models.ManyToManyField(Solvent, verbose_name='solvents used', blank=True)
    measure_date = models.DateTimeField(verbose_name='measurement date', default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name='sample submission date', blank=True, null=True)
    result_date = models.DateField(verbose_name='structure results date', blank=True, null=True)
    operator = models.ForeignKey(User, verbose_name='operator', related_name='experiment',
                                 on_delete=models.CASCADE, null=True, blank=True)
    cif = models.ForeignKey(CifFile, null=True, blank=True, related_name="cif_file",
                            verbose_name='cif file', on_delete=models.CASCADE)

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




#class Structure(models.Model):
#    x = models.FloatField()
#    y = models.FloatField()
#    z = models.FloatField()
#    element = models.CharField(max_length=2)

