from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings

settings.AUTH_USER_MODEL = 'core.CustomUser'


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

