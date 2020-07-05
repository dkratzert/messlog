# Create your tests here.
import shutil
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from pprint import pprint
from wsgiref.handlers import SimpleHandler

import gemmi
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import TestCase, override_settings, Client
from django.urls import reverse, reverse_lazy
from model_bakery import baker

from mysite.settings import MEDIA_ROOT
from scxrd.cif_model import CifFileModel
from scxrd.customer_models import Sample
from scxrd.forms.edit_experiment import ExperimentEditForm
from scxrd.forms.new_cust_sample import SubmitNewSampleForm
from scxrd.models import Experiment, Machine, Profile, WorkGroup, CrystalSupport, CrystalGlue, model_fixtures

"""
TODO:      
 
"""

MEDIA_ROOT = tempfile.mkdtemp(dir=MEDIA_ROOT)


class DeleteFilesMixin():
    fixtures = model_fixtures

    @classmethod
    def tearDownClass(cls):
        # print(MEDIA_ROOT)
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class HomeTests(DeleteFilesMixin, TestCase):
    def test_home_view_status_code(self):
        url = reverse('scxrd:index')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)


def create_experiment():
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    fixtures = model_fixtures
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
    pro = Profile(user=user,
                  phone_number='1234',
                  street='Foostreet',
                  work_group=WorkGroup(group_head='Krossing'),
                  )
    # pro.save()  # not needed?
    user.profile = pro
    mach = Machine(diffrn_measurement_device_type='FoobarMachine')
    mach.save()
    exp = Experiment(experiment_name='IK_MSJg20_100K',
                     number='1',
                     sum_formula='C5H10O2',
                     machine=Machine.objects.filter(diffrn_measurement_device_type__contains='APEX').first(),
                     operator=user,
                     customer=user2,
                     glue=CrystalGlue.objects.create(glue='Polyether'),
                     crystal_colour='1',
                     measure_date='2013-11-20 20:08:07.127325+00:00'
                     )
    exp.save()
    return exp


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ExperimentIndexViewTests(DeleteFilesMixin, TestCase):
    fixtures = model_fixtures

    """def test_no_experiements(self):
        response = self.client.get(reverse('scxrd:index'), follow=True)
        # print('response:', response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("<WSGIRequest: GET '/accounts/login/?next=%2Fscxrd%2F'>", str(response.context['request']))
"""


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ExperimentCreateTest(DeleteFilesMixin, TestCase):
    fixtures = model_fixtures

    def test_make_exp(self):
        file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        c = CifFileModel(cif_file_on_disk=file)
        exp = create_experiment()
        c.experiment = exp
        c.save()
        self.cif = c
        self.assertEqual('IK_MSJg20_100K', str(exp))
        self.assertEqual('susi', str(exp.operator))
        self.assertEqual('C5H10O2', exp.sum_formula)
        self.assertEqual('2013-11-20 20:08:07.127325+00:00', str(exp.measure_date))
        self.assertEqual(1, exp.pk)
        self.assertEqual('APEXII', str(exp.machine))
        self.assertEqual('Hansi', str(exp.customer.first_name))
        self.assertEqual('Hinterseer', str(exp.customer.last_name))

    def test_string_representation(self):
        entry = Experiment(experiment_name="My entry title")
        self.assertEqual(str(entry), entry.experiment_name)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ExperimentCreateCif(DeleteFilesMixin, TestCase):

    def test_parsecif(self):
        struct = gemmi.cif.read_file('scxrd/testfiles/p21c.cif')
        struct.sole_block()
        b = struct.sole_block()
        self.assertEqual(b.find_value('_diffrn_reflns_number'), '42245')
        self.assertEqual(b.find_value('_shelx_res_file').replace('\r\n', '')
                         .replace('\n', '')[:20], ';TITL p21c in P2(1)/')
        lo = b.find_loop('_atom_site_label')
        self.assertEqual(lo[1], 'C1_6')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CifFileTest(DeleteFilesMixin, TestCase):

    def test_saveCif(self):
        file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        c = CifFileModel(cif_file_on_disk=file, experiment=create_experiment())
        c.save()
        ex = c.experiment
        self.assertEqual(ex.customer.first_name, 'Hansi')
        self.assertEqual(ex.customer.last_name, 'Hinterseer')
        self.assertEqual(ex.operator.username, 'susi')
        ex.save()
        c.experiment = ex
        # ex.save_base()
        self.assertEqual(ex.ciffilemodel.wr2_in_percent(), 10.1)
        self.assertEqual(ex.ciffilemodel.refine_ls_wR_factor_ref, 0.1014)
        self.assertEqual(ex.ciffilemodel.shelx_res_file.replace('\r\n', '').replace('\n', '').replace('\r', '')[:30],
                         'TITL p21c in P2(1)/c    p21c.r')
        # self.assertEqual(ex.cif.atoms.x, '')
        self.assertEqual(ex.ciffilemodel.space_group_name_H_M_alt, 'P 21/c')
        response = self.client.get(reverse('scxrd:details_table', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        # delete file afterwards:
        ex.ciffilemodel.delete()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class WorkGroupTest(DeleteFilesMixin, TestCase):

    def test_group_head(self):
        """
        Create the Person of a group first. Then the group itselv and finally
        define the group as work_group of the heads Person instance.
        """
        user = User(first_name='Susie', last_name='Sorglos', email='foo@bar.de', username='susi')
        user.profile = Profile(company='A Company')
        user.save()  # important
        self.assertEqual('Susie Sorglos', str(user.profile))
        user1 = User(username='sandra', first_name='Sandra', last_name='Superschlau', email='foo@bar.de')
        user2 = User(username='hein', first_name='Heiner', last_name='Hirni', email='foo@bar.de')
        group = WorkGroup(group_head='group1')
        group.save()
        user1.save_base()
        user2.save_base()
        user1.profile.town = 'Freiburg'
        user1.profile.work_group = group
        user2.profile.town = 'Freiburg'
        user2.profile.work_group = group
        user1.save()
        user2.save()
        print(user1.profile.town)
        print(User.objects.get(username__icontains='san'))
        print(User.objects.get(username__icontains='san').profile.town)
        print(User.objects.get(username__icontains='san').profile.work_group)
        print(User.objects.filter(profile__work_group__group_head__contains='grou'), '###')

    def test_validate_email(self):
        # TODO: why is it not evaluating?
        pers = User(first_name='DAniel', last_name='Kratzert', email='-!ß\/()')
        pers.save()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class OtherTablesTest(DeleteFilesMixin, TestCase):

    def test_other(self):
        mach = Machine(diffrn_measurement_device_type='APEXII', diffrn_measurement_device='3-circle diffractometer')
        mach.save()
        self.assertEqual('APEXII', str(mach))
        self.assertEqual('3-circle diffractometer', mach.diffrn_measurement_device)
        self.assertEqual('APEXII', mach.diffrn_measurement_device_type)

        sup = CrystalSupport(support='Glass Fiber')
        sup.save()
        self.assertEqual(str(sup), 'Glass Fiber')

        glue = CrystalGlue(glue='perfluor ether oil')
        glue.save()
        self.assertEqual(str(glue), 'perfluor ether oil')


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
class TestNewSample(DeleteFilesMixin, TestCase):
    def setUp(self) -> None:
        self.data = {
            "sample_name"               : "Juliana",
            "sum_formula"               : "C5H5",
            "crystallization_conditions": "Would love to talk about Philip K. Dick",
            "desired_struct_draw"       : "Would love to talk about Philip K. Dick",
        }
        user = User.objects.create(username='testuser', email='test@test.com', is_active=True, is_superuser=False)
        user.set_password('Test1234!')
        user.save()
        self.client = Client()
        self.client.login(username='testuser', password='Test1234!')

    def test_submit_new_sample(self):
        #response = self.client.get(reverse_lazy('scxrd:new_exp'), follow=True)
        #self.assertEqual(200, response.status_code)
        response: HttpResponse = self.client.get(path=reverse_lazy("scxrd:submit_sample"), data=self.data, follow=True)
        self.assertEqual('OK', response.reason_phrase)
        response: HttpResponse = self.client.post(path=reverse_lazy("scxrd:submit_sample"), data=self.data, follow=True)
        form = SubmitNewSampleForm(response)
        self.assertEqual(True, form.is_valid())
        self.assertEqual('Juliana', str(form.save()))
        self.assertEqual(Sample.objects.count(), 1)

    def test_submit_invalid_sample_name(self):
        self.data["sample_name"] = ''
        form = SubmitNewSampleForm(self.data)
        self.assertEqual(False, form.is_valid())
        self.assertDictEqual({'sample_name': ['This field is required.']}, form.errors)

    def test_submit_invalid_formula(self):
        self.data["sum_formula"] = ''
        form = SubmitNewSampleForm(self.data)
        self.assertEqual(False, form.is_valid())
        self.assertDictEqual({'sum_formula': ['This field is required.']}, form.errors)

    def test_submit_invalid_crystallizations(self):
        self.data["crystallization_conditions"] = ''
        form = SubmitNewSampleForm(self.data)
        self.assertEqual(False, form.is_valid())
        self.assertDictEqual({'crystallization_conditions': ['This field is required.']}, form.errors)

    def test_submit_invalid_struct(self):
        self.data["desired_struct_draw"] = ''
        form = SubmitNewSampleForm(self.data)
        self.assertEqual(False, form.is_valid())
        self.assertDictEqual({'__all__': ['You need to either upload a document with the desired '
                                          'structure or draw it in the field below.']}, form.errors)


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
