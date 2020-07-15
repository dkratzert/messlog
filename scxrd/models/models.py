import re
from pathlib import Path

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

"""
TODO: 
- add email notifications and password reset etc...

- Add a "currently running experiment" page with status for everyone visible
   - there should be also the end time visible and who is responsible
   - the owner of the experiment could do modifications to this experiment by an "edit experiment" button
     owners can do changes only until the cif file is uploaded 
   - page should have a link to the google calendar (or even embedded into an iframe?)

- check checksum for correctness during file upload and download
- show wrong cif crc in "Details" of experiments list page
- Check for existing unit cell during cif upload and measure experiment.
- reminder message to take back vials?
- for charts:
    https://simpleisbetterthancomplex.com/tutorial/2020/01/19/how-to-use-chart-js-with-django.html 
    https://www.chartjs.org/docs/latest/
    - chart with measurements per time
    - chart with R-value per time
    - chart with  
- show success rate per person
- http://ccbv.co.uk/projects/Django/3.0/


<a href="{{ object.get_absolute_url }}">{{ object.name }}</a>

def get_absolute_url(self):
    return reverse('company_details', kwargs={'pk': self.id})

"""

model_fixtures = ['scxrd/fixtures/glue.json',
                  'scxrd/fixtures/support.json',
                  'scxrd/fixtures/machines.json',
                  'scxrd/fixtures/work_group.json']


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


def resolution_validator(value):
    if not value:
        return value
    if value < 0.001 or value > 99:
        raise ValidationError(_('Enter a valid resolution in angstrom.'))
    return value


def sample_name_validator(value):
    if re.fullmatch(r'[A-Za-z0-9_]+', value):
        return value
    else:
        raise ValidationError(_('Enter a name with characters A-Z a-z 0-9 or _'))


phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: "
                                         "'+999999999'. Up to 15 digits allowed.")


class Profile(models.Model):
    """
    Persons where samples belong to.
    A Person is a Human that has no authentication.
    A Person does not need to have a User account.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.CharField(max_length=200, verbose_name=_('company'), blank=True)
    work_group = models.ForeignKey('WorkGroup', blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name='profiles')
    street = models.CharField(max_length=250, blank=True)
    house_number = models.CharField(max_length=200, blank=True)
    building = models.CharField(max_length=200, blank=True)
    town = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=17, blank=True)
    comment = models.TextField(blank=True, default='')
    is_operator = models.BooleanField(verbose_name=_('The user has operator rights'), default=False)

    def __str__(self):
        name = '{} {}'.format(self.user.first_name, self.user.last_name)
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
    A work group is a group of Person()s with a leading group_head (which is also a Person).
    """
    fixtures = ['scxrd/fixtures/work_group.json']
    group_head = models.CharField(verbose_name=_('work group head'), max_length=50, blank=True, unique=True)

    def __str__(self):
        return "AK {}".format(self.group_head)


class Machine(models.Model):
    """
    A diffractometer name and type.
    """
    fixtures = ['scxrd/fixtures/machines.json']
    # The make, model or name of the measurement device (goniometer) used:
    diffrn_measurement_device_type = models.CharField(verbose_name="machine model name", max_length=200)
    # The general class of goniometer or device used to support and orient the specimen:
    # e.g. 'three-circle diffractometer'
    diffrn_measurement_device = models.CharField(verbose_name=_("machine type"), max_length=200, blank=True)

    def __str__(self):
        return self.diffrn_measurement_device_type


class CrystalSupport(models.Model):
    """
    The support where the crystal was mounted on the diffraktometer.
    _diffrn_measurement_specimen_support e.g. 'glass capillary'
    """
    fixtures = ['scxrd/fixtures/support.json']
    support = models.CharField(verbose_name='crystal support', max_length=200, unique=True)

    def __str__(self):
        return self.support


class CrystalGlue(models.Model):
    """
    What kind of addhesive was used?
    """
    fixtures = ['scxrd/fixtures/glue.json']
    glue = models.CharField(verbose_name='crystal glue', max_length=200, unique=True)

    def __str__(self):
        return self.glue


def validate_checkcif_file_extension(value):
    error = ValidationError(_('Only .html or .pdf files are allowed to upload here.'))
    if not isinstance(value.name, str):
        raise error
    if not value.name.lower().endswith(('.pdf', '.htm', '.html')):
        raise error


def validate_reportdoc_file_extension(value):
    error = ValidationError(_('Only .docx, .doc or .pdf files are allowed to upload here.'))
    if not isinstance(value.name, str):
        raise error
    if not value.name.lower().endswith(('.docx', '.doc', '.pdf')):
        raise error


class CheckCifModel(models.Model):
    """
    A pdf or html file with the IUCr checkcif result: https://checkcif.iucr.org/
    """
    experiment = models.OneToOneField(to='Experiment', on_delete=models.CASCADE, verbose_name='checkCIF report',
                                      related_name='checkcifmodel')
    checkcif_on_disk = models.FileField(upload_to='checkcif_reports', null=True, blank=True, max_length=255,
                                        validators=[validate_checkcif_file_extension],
                                        verbose_name='cif file')

    @property
    def chkcif_file_path(self) -> Path:
        """The complete absolute path of the CIF file with file name and ending"""
        return Path(str(self.checkcif_on_disk.file))

    @property
    def chkcif_name_only(self) -> str:
        """The CIF file name without path"""
        return self.chkcif_file_path.name

    def chkcif_exists(self):
        """Check if the CIF exists"""
        if self.chkcif_file_path.exists():
            return True
        return False


class ReportModel(models.Model):
    """
    A pdf or html file with the IUCr checkcif result: https://checkcif.iucr.org/
    """
    experiment = models.OneToOneField(to='Experiment', on_delete=models.CASCADE, max_length=255,
                                      verbose_name='structure report document',
                                      related_name='reportmodel')
    reportdoc_on_disk = models.FileField(upload_to='struct_reports', null=True, blank=True,
                                         validators=[validate_reportdoc_file_extension],
                                         verbose_name='cif file')

    @property
    def report_file_path(self) -> Path:
        """The complete absolute path of the report file with file name and ending"""
        return Path(str(self.reportdoc_on_disk.file))

    @property
    def report_name_only(self) -> str:
        """The CIF file name without path"""
        return self.report_file_path.name

    def report_exists(self):
        """Check if the report document exists"""
        if self.report_file_path.exists():
            return True
        return False


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    """Creating a Profile model instance while saving a user"""
    if created:
        Profile.objects.create(user=instance)
        # print('Created a profile instance!')
    instance.profile.save()
