# Create your tests here.
import shutil
import sys
import tempfile
import unittest
from io import BytesIO
from pprint import pprint
from wsgiref.handlers import SimpleHandler

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase, override_settings, Client
from django.urls import reverse, reverse_lazy
from model_bakery import baker

from mysite.settings import MEDIA_ROOT
from scxrd.forms.edit_experiment import ExperimentEditForm
from scxrd.models import Experiment, Machine, WorkGroup, CrystalSupport, CrystalGlue, model_fixtures

"""
TODO:      
 
"""

MEDIA_ROOT = tempfile.mkdtemp(dir=MEDIA_ROOT)


def make_operator_user():
    group = WorkGroup.objects.create(group_head='Krabäppel')
    u = User.objects.create(username='testuser', email='test@test.com', is_active=True, first_name='Sandra',
                            last_name='Sorglos', is_superuser=False)
    u.set_password('Test1234!')
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
    u = User.objects.create(username='elefant', email='test@test.com', is_active=True, first_name='Benjamin',
                            last_name='Blümchen', is_superuser=True)
    u.set_password('Test1234!')
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


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class HomeTests(DeleteFilesMixin, TestCase):
    def test_home_view_status_code(self):
        url = reverse('scxrd:index')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)


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






def hello_app(environ, start_response):
    start_response("200 OK", [
        ('Content-Type', 'text/plain'),
        ('Date', 'Mon, 05 Jun 2006 18:49:54 GMT')
    ])
    return [b"Hello, world!"]


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestWSGIRef(DeleteFilesMixin, TestCase):

    @unittest.skip
    def testConnectionAbortedError(self):
        class AbortingWriter:
            def write(self, b):
                raise ConnectionAbortedError()

            def flush(self):
                pass

        environ = {"SERVER_PROTOCOL": "HTTP/1.0"}
        h = SimpleHandler(BytesIO(), AbortingWriter(), sys.stderr, environ)
        msg = "Client connection aborted"
        with self.assertWarnsRegex(RuntimeWarning, msg):
            h.run(hello_app)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestCustomerModel(DeleteFilesMixin, TestCase):

    def setUp(self):
        self.sample = baker.prepare('Sample', _quantity=3)
        self.exp = baker.prepare('Experiment', experiment_name='foo')
        self.user = baker.prepare('User')
        self.profile = baker.prepare('Profile')

    def test_foo(self):
        [pprint(x.__dict__) for x in self.sample]
        pprint(self.exp.__dict__)
        pprint(self.user.__dict__)
        pprint(self.profile.__dict__)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestViews(DeleteFilesMixin, TestCase):

    def test_report(self):
        pass


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NewExpTest(DeleteFilesMixin, TestCase):
    def setUp(self):
        self.formdata = dict({'Save'                 : 'Save',
                              'base'                 : '2',
                              'crystal_colour'       : '6',
                              'crystal_habit'        : 'needle',
                              'crystal_size_x'       : '0.13',
                              'crystal_size_y'       : '0.12',
                              'crystal_size_z'       : '0.1',
                              'csrfmiddlewaretoken'  : '4J3vmTSFVd9QxLy7tnu7dCwa5cealpcsvkH1w7kYG3h1cEtKkGqgZxnLwXOinwpb',
                              'customer'             : '1',
                              'experiment_name'      : 'TB_VR40_v1b',
                              'exptl_special_details': 'blub',
                              'glue'                 : '2',
                              'machine'              : '1',
                              'measure_date'         : '2020-07-03 12:53',
                              'measurement_temp'     : '102',
                              'number'               : '88',
                              'prelim_unit_cell'     : '10 10 10 90 90 90',
                              'resolution'           : '0.77',
                              'sum_formula'          : 'C3H4O2',
                              'cif_file_on_disk'     : 'scxrd/testfiles/p21c.cif',
                              })
        # self.selenium = webdriver.Chrome()
        super().setUp()
        user = User.objects.create(username='testuser', email='test@test.com', is_active=True, is_superuser=True)
        user.set_password('Test1234!')
        user.save()
        self.user = authenticate(username='testuser', password='Test1234!')

    def test_post_experiment(self):
        c = Client()
        c.login(username='testuser', password='Test1234!')
        response = c.get(reverse_lazy('scxrd:new_exp'), follow=True)
        self.assertEqual(200, response.status_code)
        for c1 in response.context:
            for c in c1:
                pprint(c)
        self.assertEqual('testuser', str(response.context.get('user')))
        self.assertEqual(True, response.context.get('render_required_fields'))
        self.assertEqual(False, response.context.get('render_unmentioned_fields'))
        print('######')
        print(response.context[0]['form'].fields['experiment_name'])
        # response = c.get(reverse_lazy('scxrd:new_exp'), follow=True)
        # print(response.redirect_chain)
        # response = self.client.post(reverse_lazy('scxrd:new_exp'), follow=True, data=self.formdata)
        # print('#', response.content)
        # response = self.client.post(reverse_lazy('scxrd:new_exp'), data=self.formdata, follow=True)
        # self.assertEqual(response.status_code, 200)

    def test_form(self):
        form = ExperimentEditForm(self.formdata)
        self.assertDictEqual({'customer': ['Select a valid choice. That choice is not one of the available choices.']},
                             form.errors)
        self.assertEqual(False, form.is_valid())
        # print(form.cleaned_data)

    def test_invalid_form(self):
        self.maxDiff = 999
        self.formdata['experiment_name'] = ''
        form = ExperimentEditForm(self.formdata)
        self.assertDictEqual({'experiment_name': ['This field is required.'],
                              'customer'       : [
                                  'Select a valid choice. That choice is not one of the available choices.']},
                             form.errors)
        self.assertEqual(False, form.is_valid())


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestHostHeader(DeleteFilesMixin, TestCase):
    def test_empty_host(self):
        response = self.client.get(reverse("scxrd:index"))
        self.assertEqual(response.status_code, 200)

    def test_wrong_host(self):
        response = self.client.get(reverse("scxrd:index"), HTTP_HOST="128.0.0.2")
        self.assertEqual(response.status_code, 400)

    def test_wrong_host_construct(self):
        client = Client(HTTP_HOST="127.0.0.1")
        response = client.get(reverse("scxrd:index"))
        self.assertContains(response, "")

    def test_correct_host(self):
        response = self.client.get(reverse("scxrd:index"), HTTP_HOST="127.0.0.1:8000")
        self.assertContains(response, "")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestAuthenticated(DeleteFilesMixin, TestCase):
    def setUp(self):
        # self.selenium = webdriver.Chrome()
        super().setUp()
        user = User.objects.create(username='testuser', email='test@test.com', is_active=True)
        user.set_password('Test1234!')
        user.save()
        self.user = authenticate(username='testuser', password='Test1234!')

    def test_user(self):
        self.assertEqual(str(User.objects.first()), 'testuser')

    def test_register(self):
        user = authenticate(username='testuser', password='Test1234!')
        if user is not None:  # prints Backend login failed
            print("Backend login successful")
        else:
            print("Backend login failed")

    def test_can_send_message(self):
        data = {
            "name"   : "Juliana",
            "foo"    : " Crain",
            "message": "Would love to talk about Philip K. Dick",
        }
        response = self.client.post(reverse("scxrd:submit_sample"), data=data, user=self.user, follow=True)
        self.assertEqual(response.status_code, 200)
        # TODO: test to full sample creation
        # self.assertEqual(Sample.objects.count(), 1)


if __name__ == '__main':
    pass


class PlainUserMixin():
    def setUp(self) -> None:
        user = User.objects.create(username='testuser', email='test@test.com', is_active=True, is_superuser=False)
        user.set_password('Test1234!')
        self.user_instance = user
        self.client = Client()
        self.client.login(username='testuser', password='Test1234!')


class OperatorUserMixin():
    def setUp(self) -> None:
        u = make_operator_user()
        self.user_instance = u
        self.client = Client()
        self.client.login(username='testuser', password='Test1234!')


class SuperUserMixin():
    def setUp(self) -> None:
        u = make_superuser_user()
        self.user_instance = u
        self.client = Client()
        self.client.login(username='elefant', password='Test1234!')
