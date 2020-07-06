from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from scxrd.models import Profile
from tests.tests import Plain_user_Mixin, Operator_user_Mixin, DeleteFilesMixin, MEDIA_ROOT


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestUser(Plain_user_Mixin, DeleteFilesMixin, TestCase):

    def test_string_class(self):
        """"""
        u = User.objects.get(pk=1)
        self.assertEqual(str(u), 'testuser')

    def test_string_username(self):
        u = User.objects.get(pk=1)
        u.first_name = 'Bob'
        u.last_name = 'Barker'
        u.save(update_fields=('first_name', 'last_name'))
        self.assertEqual(str(u), 'testuser')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestProfile(Operator_user_Mixin, DeleteFilesMixin, TestCase):

    def test_string_class(self):
        """"""
        u = User.objects.get(pk=1)
        self.assertEqual(str(u), 'testuser')

    def test_string_username(self):
        u = User.objects.get(pk=1)
        self.assertEqual(str(u), 'testuser')
        pro = Profile.objects.get(pk=1)
        self.assertNotEqual(str(pro), 'Bob Barker')
        self.assertEqual(str(pro), 'Sandra Sorglos')
        pro.user = u
        u.first_name = 'Bob'
        u.last_name = 'Barker'
        print(u.profile.house_number, ':housenumber')
        # Has to be after "pro.user = u":
        u.profile.house_number = '45'
        self.assertEqual(str(User.objects.get(pk=1)), 'testuser')
        self.assertEqual(str(Profile.objects.get(pk=1)), 'Sandra Sorglos')
        u.save(update_fields=('first_name', 'last_name'))
        # pro.save(update_fields=('house_number',))
        self.assertEqual(str(User.objects.get(pk=1)), 'testuser')
        # Profile is saved during u.save()
        self.assertEqual(str(Profile.objects.get(pk=1)), 'Bob Barker')
        self.assertEqual(str(pro), 'Bob Barker')
        self.assertEqual(Profile.objects.get(pk=1).house_number, '45')

    def test_rights(self):
        u = User.objects.get(pk=1)
        self.assertEqual(u.profile.is_operator, False)