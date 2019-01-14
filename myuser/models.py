from django.contrib.auth.models import AbstractUser

'''
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
'''
