from django.db import models

# Create your models here.


'''
settings.AUTH_USER_MODEL = 'scxrd.CustomUser'


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        """
        Replaces USERNAME_FIELD = 'username' with 'username__iexact'.
        """
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class CustomUser(AbstractUser):
    """
    Extend user model here:
    """
    objects = CustomUserManager()


class Person():
    first_name =
    last_name =
    street =
    house_number =
    building =
    town =
    country =
    postal_code =
    email_adress =
    phone_number =
    comment =


class WorkGroup():
    group_leader = ForeignKey(Person, related_name='group')



'''