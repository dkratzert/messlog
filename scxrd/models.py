import datetime

from django_tables2 import tables

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
from django.db import models, utils

# Create your models here.
from django.utils import timezone


class UploadManager(models.Manager):

    def upload_file(self, uploaded_file, category=''):
        sha256 = hashlib.sha256()
        for c in uploaded_file.chunks():
            sha256.update(c)
        checksum = sha256.hexdigest()
        inst = self.get_queryset().filter(checksum=checksum).first()

        if inst:
            return inst

        inst = self.model(
            checksum=checksum,
            category=category,
            name=uploaded_file.name,
            size=uploaded_file.size,
            content_type=uploaded_file.content_type,
        )

        filename = '{}.{}'.format(checksum, uploaded_file.content_type.split('/')[1])
        inst.upload.save(filename, File(uploaded_file))

        return inst


class AbstractUpload(models.Model):
    checksum = models.CharField(max_length=64, primary_key=True)
    category = models.CharField(max_length=255, db_index=True, default='')
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, default='applicaiton/binary')
    size = models.BigIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_url(self):
        return self.upload.url

    def to_dict(self):
        return {
            'checksum': self.checksum,
            'url': self.get_url(),
            'content_type': self.content_type,
            'size': self.size,
            'name': self.name,
            'created_on': self.created_on.isoformat(),
        }


class Upload(AbstractUpload):
    upload = models.FileField(upload_to='scxrd/cifs', null=True, blank=True)
    objects = UploadManager()


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
    machine = models.ForeignKey(to=Machine, verbose_name='diffractometer', parent_link=True, on_delete=models.CASCADE, null=True, blank=True)
    sum_formula = models.CharField(max_length=300, blank=True)
    solvents_used = models.ManyToManyField(Solvent, verbose_name='solvents used', blank=True)
    measure_date = models.DateTimeField(verbose_name='measurement date', default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name='sample submission date', blank=True, null=True)
    result_date = models.DateField(verbose_name='structure results date', blank=True, null=True)
    operator = models.ForeignKey(User, verbose_name='operator', related_name='experiment', on_delete=models.CASCADE, default=1)
    cif = Upload()

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

