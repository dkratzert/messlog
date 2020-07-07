# Create your tests here.
import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import Client

from mysite.settings import MEDIA_ROOT
from scxrd.models import Experiment, Machine, WorkGroup, CrystalGlue, model_fixtures

MEDIA_ROOT = tempfile.mkdtemp(dir=MEDIA_ROOT)


class AnonUserMixin():
    def setUp(self):
        self.client = Client()


class PlainUserMixin():

    def setUp(self) -> None:
        user = User.objects.create_user(username='testuser', email='test@test.com', is_active=True, is_superuser=False,
                                        password='Test1234!')
        self.user = user
        self.client = Client()
        self.client.login(username='testuser', password='Test1234!')


class OperatorUserMixin():
    def setUp(self) -> None:
        u = make_operator_user()
        self.user = u
        self.client = Client()
        self.client.login(username='testuser', password='Test1234!')


class SuperUserMixin():
    def setUp(self) -> None:
        u = make_superuser_user()
        self.user = u
        self.client = Client()
        self.client.login(username='elefant', password='Test1234!')


def make_operator_user():
    group = WorkGroup.objects.create(group_head='Krabäppel')
    u = User.objects.create_user(username='testuser', email='test@test.com', is_active=True, first_name='Sandra',
                                 last_name='Sorglos', is_superuser=False, password='Test1234!')
    # This works, because of the update_user_profile slot in Profile
    u.profile.work_group = group
    u.profile.is_operator = True
    u.profile.phone_number = '123456'
    u.profile.street = 'Foostreet'
    u.profile.house_number = '31'
    u.profile.town = 'Bartown'
    u.profile.country = 'Germany'
    u.profile.postal_code = '3500'
    u.profile.building = 'AC'
    u.profile.comment = "A Dog's live in Databases"
    u.profile.work_group = group
    u.save()
    return u


def make_superuser_user():
    group = WorkGroup.objects.create(group_head='Blümchen')
    u = User.objects.create_user(username='elefant', email='test@test.com', is_active=True, first_name='Benjamin',
                                 last_name='Blümchen', is_superuser=True, password='Test1234!')
    # This works, because of the update_user_profile slot in Profile
    u.profile.work_group = group
    # Setting operator to True should be not necessary for a superuser:
    # u.profile.is_operator = True
    u.profile.phone_number = '654321'
    u.profile.street = 'Zoostraße'
    u.profile.house_number = '3'
    u.profile.town = 'Freudenstadt'
    u.profile.country = 'Germany'
    u.profile.postal_code = '3000'
    u.profile.building = 'Elefantenhaus'
    u.profile.comment = "Auf der schönen grünen Wiese"
    u.profile.work_group = group
    u.save()
    return u


class DeleteFilesMixin():
    fixtures = model_fixtures

    @classmethod
    def tearDownClass(cls):
        # print(MEDIA_ROOT)
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        # noinspection PyUnresolvedReferences
        super().tearDownClass()


def create_experiment(user: User = None):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    fixtures = model_fixtures
    if not user:
        user = User(first_name='Susi',
                    last_name='Sorglos',
                    username='susi',
                    email='susi@foo.de',
                    )
        user.save()
    user2 = User(first_name='Hansi',
                 last_name='Hinterseer',
                 username='hans',
                 email='hans@foo.de',
                 )
    user2.save()
    user.profile.work_group = WorkGroup.objects.get(group_head__contains='krossing')
    user2.profile.work_group = WorkGroup.objects.get(group_head__contains='Hillebrecht')
    # user.save()
    # user2.save()
    mach = Machine(diffrn_measurement_device_type='FoobarMachine')
    mach.save()
    exp = Experiment.objects.create(experiment_name='IK_MSJg20_100K',
                                    number='1',
                                    sum_formula='C5H10O2',
                                    was_measured=True,
                                    machine=Machine.objects.filter(
                                        diffrn_measurement_device_type__contains='APEX').first(),
                                    operator=user,
                                    customer=user2,
                                    glue=CrystalGlue.objects.create(glue='Polyether'),
                                    crystal_colour='1',
                                    measure_date='2013-11-20 20:08:07.127325+00:00',
                                    prelim_unit_cell='10 01 10 90 90 90'
                                    )
    return exp


if __name__ == '__main':
    pass
