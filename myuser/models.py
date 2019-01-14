from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator, EmailValidator
from django.db import models


validate_email = EmailValidator()

phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: "
                                         "'+999999999'. Up to 15 digits allowed.")


class MyUserManager(UserManager):
    def get_by_natural_key(self, username):
        """
        Replaces USERNAME_FIELD = 'username' with 'username__iexact'.
        """
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class MyUser(AbstractUser):
    """
    username = models.CharField
    first_name = models.CharField
    last_name = models.CharField
    email = models.EmailField
    is_staff = models.BooleanField
    is_active = models.BooleanField
    date_joined = models.DateTimeField
    Extend user model here:
    """
    objects = MyUserManager()


class Person(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, verbose_name='company', blank=True)
    work_group = models.ForeignKey('WorkGroup', related_name='person', max_length=200, blank=True, null=True,
                                   on_delete=models.DO_NOTHING)
    street = models.CharField(max_length=250, blank=True)
    house_number = models.CharField(max_length=200, blank=True)
    building = models.CharField(max_length=200, blank=True)
    town = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=200, blank=True)
    email_adress = models.EmailField(max_length=250, validators=[validate_email], blank=True)
    phone_number = models.CharField(# validators=[phone_validator],
                                    max_length=17, blank=True)
    comment = models.TextField(blank=True)


class WorkGroup(models.Model):
    work_group = models.ForeignKey(Person, related_name='group', on_delete=models.CASCADE)

