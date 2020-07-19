import datetime
from pathlib import Path

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings, Client, RequestFactory
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from scxrd.cif.cif_file_io import CifContainer
from scxrd.models.cif_model import CifFileModel
from scxrd.forms.edit_measurement import MeasurementEditForm
from scxrd.models.models import CrystalSupport, Machine, WorkGroup
from scxrd.models.measurement_model import Measurement
from scxrd.models.sample_model import Sample
from scxrd.utils import generate_sha256
from scxrd.views.sample_views import NewSampleByCustomer
from tests.tests import MEDIA_ROOT, DeleteFilesMixin, OperatorUserMixin, PlainUserMixin, create_measurement


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
class TestNewSampleByCustomerView(DeleteFilesMixin, OperatorUserMixin, TestCase):

    def test_authenticated(self):
        self.assertEqual(self.user.is_authenticated, True)

    def test_request(self):
        self.maxDiff = None
        self.longMessage = True
        request_factory = RequestFactory()
        request = request_factory.get(reverse('scxrd:submit_sample'))
        request.user = self.user
        view = NewSampleByCustomer.as_view(template_name='scxrd/new_sample_by_customer.html',
                                           extra_context={'sample_name': 'Waldo'})
        response = view(request, sample_name='laskjdfh')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['scxrd/new_sample_by_customer.html'])


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class HomeTests(DeleteFilesMixin, TestCase):
    def test_home_view_status_code(self):
        url = reverse('scxrd:index')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)


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
                              'measurement_name'      : 'TB_VR40_v1b',
                              'exptl_special_details': 'blub',
                              'glue'                 : '2',
                              'machine'              : '1',
                              'measure_date'         : '2020-07-03 12:53',
                              'end_time    '         : '2020-07-03 19:33',
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

    def test_post_measurement(self):
        c = Client()
        c.login(username='testuser', password='Test1234!')
        response = c.get(reverse_lazy('scxrd:new_exp'), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual('testuser', str(response.context.get('user')))
        self.assertEqual(True, response.context.get('render_required_fields'))
        self.assertEqual(False, response.context.get('render_unmentioned_fields'))

    def test_form(self):
        form = MeasurementEditForm(self.formdata)
        self.assertDictEqual({'customer': ['Select a valid choice. That choice is not one of the available choices.'],
                              'end_time': ['This field is required.']},
                             form.errors)
        self.assertEqual(False, form.is_valid())
        # print(form.cleaned_data)

    def test_invalid_form(self):
        self.maxDiff = 999
        self.formdata['measurement_name'] = ''
        form = MeasurementEditForm(self.formdata)
        self.assertDictEqual({'measurement_name': ['This field is required.'],
                              'end_time'       : ['This field is required.'],
                              'customer'       : [
                                  'Select a valid choice. That choice is not one of the available choices.']},
                             form.errors)
        self.assertEqual(False, form.is_valid())


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestMeasurementEditView(DeleteFilesMixin, OperatorUserMixin, TestCase):

    def test_edit_exp(self):
        response = self.client.get(reverse("scxrd:new_exp"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scxrd/measurement_new.html')

    def test_new_exp_create_not_exist(self):
        self.assertEqual(Measurement.objects.count(), 0)
        # Do not Follow the post request, because it goes to index page afterwards:
        response = self.client.post(reverse("scxrd:edit-measurement", args=(1,)), follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content,
                         b'\n<!doctype html>\n<html lang="en">\n<head>\n  <title>Not Found</title>\n</head>\n<body>\n  '
                         b'<h1>Not Found</h1><p>The requested resource was not found on this server.</p>\n</body>\n</html>\n')

    def test_new_exp_create(self):
        data = {
            'conditions'      : '',
            'crystal_habit'   : 'block',
            'measurement_name' : 'PK_TMP355_b',  # PK-TMP355
            'base'            : CrystalSupport.objects.get(pk=1),
            'machine'         : Machine.objects.get(pk=1),
            'measure_date'    : datetime.datetime(2020, 7, 2, 14, 37, 9, tzinfo=timezone.get_current_timezone()),
            # 'end_time'        : datetime.datetime(2020, 7, 3, 9, 37, 9, tzinfo=timezone.get_current_timezone()),
            'end_time'        : '2020-07-03 09:37:19',
            'measurement_temp': 101.0,  # 123.0
            'number'          : 3,
            'operator_id'     : 1,
            'prelim_unit_cell': '',
            'publishable'     : True,  # False
            'resolution'      : 0.80,
            'was_measured'    : True}
        data2 = {
            'conditions'           : 'blubb',
            'crystal_colour'       : 1,
            'crystal_colour_lustre': 0,
            'crystal_colour_mod'   : 0,
            'crystal_habit'        : 'block',
            'crystal_size_x'       : 0.12,
            'crystal_size_y'       : 0.13,
            'crystal_size_z'       : 0.14,
            'base'                 : 1,
            'measurement_name'      : 'PK_TMP355',  # PK-TMP355
            'exptl_special_details': 'some details',
            'machine'              : 1,
            'measurement_temp'     : 124.0,  # 123.0
            'not_measured_cause'   : '',
            'number'               : 3,
            'operator_id'          : 1,
            'prelim_unit_cell'     : '',
            'publishable'          : False,  # False
            'resolution'           : 0.79,
            'result_date'          : '2020-7-7',
            'end_time'             : '2020-07-03 09:37:19',
            'submit_date'          : '',
            'sum_formula'          : 'C5H5',
            'was_measured'         : True}
        self.assertEqual(Measurement.objects.count(), 0)
        Measurement.objects.create(**data)
        self.assertEqual(Measurement.objects.count(), 1)
        # Do not Follow the post request, because it goes to index page afterwards:
        # remember: we use number instead of pk:
        response = self.client.post(reverse("scxrd:edit-measurement", kwargs={'number': 3}), follow=True, data=data2)
        self.assertEqual(Measurement.objects.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scxrd/scxrd_index.html')
        self.assertEqual(Measurement.objects.last().measurement_temp, 124.0)
        self.assertEqual(Measurement.objects.last().measurement_name, 'PK_TMP355')
        self.assertEqual(Measurement.objects.last().sum_formula, 'C5H5')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestMeasurementEditViewPlain(DeleteFilesMixin, PlainUserMixin, TestCase):
    data = {
        'measurement_name': 'PK_TMP355_b',  # PK-TMP355
        'end_time': '2020-07-03 09:37:19',
        'number'         : 3, }

    def test_exp_edit_by_other_user(self):
        """TODO: A plain user should not be allowed to edit this measurement"""
        Measurement.objects.create(**self.data)
        self.assertEqual(Measurement.objects.count(), 1)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class MySamplesList(DeleteFilesMixin, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data = {
            'sample_name'               : 'PK_TMP355_b',  # PK-TMP355
            'exptl_special_details'     : 'dfg',
            'crystallization_conditions': 'From hot H2SO4',
            'sum_formula'               : 'UO2',
            'desired_struct_draw'       : 'SVG',
        }
        user = User.objects.create_user(username='plainuser', email='test@test.com', is_active=True, is_superuser=False,
                                        password='Test1234!')
        self.user_plain = user
        self.client_plain = Client()
        self.client_plain.login(username='plainuser', password='Test1234!')
        ##
        group = WorkGroup.objects.create(group_head='Krabäppel')
        u = User.objects.create_user(username='opuser', email='test@test.com', is_active=True, first_name='Sandra',
                                     last_name='Sorglos', is_superuser=False, password='Test1234!')
        # This works, because of the update_user_profile slot in Profile
        u.profile.work_group = group
        u.profile.is_operator = True
        u.profile.phone_number = '123456'
        u.profile.street = 'Foostreet'
        self.user_op = u
        self.client_op = Client()
        self.client_op.login(username='opuser', password='Test1234!')

    def test_user_view_op_samples(self):
        # Operator makes a sample:
        request = self.client_op.post(reverse('scxrd:submit_sample'), data=self.data, follow=True)
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(request.status_code, 200)
        # The user:
        request = self.client_plain.get(reverse('scxrd:my_samples_page'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.context_data['sample_list']), 0)
        # The operator
        request = self.client_op.get(reverse('scxrd:my_samples_page'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.context_data['sample_list']), 1)

    def test_op_view_user_samples(self):
        # Operator makes a sample:
        request = self.client_plain.post(reverse('scxrd:submit_sample'), data=self.data, follow=True)
        self.data['sample_name'] = 'sdf'
        request = self.client_op.post(reverse('scxrd:submit_sample'), data=self.data, follow=True)
        self.assertEqual(Sample.objects.count(), 2)
        self.assertEqual(request.status_code, 200)
        # The user:
        request = self.client_plain.get(reverse('scxrd:my_samples_page'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.context_data['sample_list']), 1)
        # The operator
        request = self.client_op.get(reverse('scxrd:my_samples_page'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.context_data['sample_list']), 1)
        # Operator all samples:
        request = self.client_op.get(reverse('scxrd:op_samples_page'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.context_data['sample_list']), 2)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestMoleculeView(DeleteFilesMixin, OperatorUserMixin, TestCase):

    def setUp(self) -> None:
        super().setUp()
        cif_model = CifFileModel()
        cif_file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        cif = CifContainer(chunks='\n'.join([x.decode(encoding='cp1250', errors='ignore') for x in cif_file.chunks()]))
        cif_model.fill_residuals_table(cif)
        cif_model.sha256 = generate_sha256(cif_file)
        cif_model.filesize = cif_file.size
        cif_model.cif_file_on_disk = cif_file
        self.exp = create_measurement()
        cif_model.measurement = self.exp
        cif_model.save()
        self.cif_model = cif_model

    def test_molecule(self):
        # TODO: measurement_id is useless here: Use id instead of cif file path!
        request = self.client.post(reverse('scxrd:molecule'), follow=False,
                                   data={'measurement_id': 2, 'cif_file': self.cif_model.cif_file_path})
        self.assertEqual(Measurement.objects.count(), 1)
        self.assertEqual(CifFileModel.objects.count(), 1)
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.content[:100],
                         b'\n\n\n  128  126\n    0.2501    4.9458    8.1795 O \n   -0.1835    4.8977'
                         b'    6.8930 C \n   -1.5751    4.22')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestMeasurementListJsonView(DeleteFilesMixin, OperatorUserMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.exp = create_measurement()

    def test_exp_list_json(self):
        request = self.client.post(reverse('scxrd:measurements_list'), follow=True)
        self.assertEqual(Measurement.objects.count(), 1)
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.content,
                         (b'{"draw": 0, "recordsTotal": 1, "recordsFiltered": 1, '
                          b'"data": [["1", "1", "IK'
                          b'_MSJg20_100K", "20.11.2013 21:08", "APEXII", "susi", "<span class=\\"badg'
                          b'e badge-warning ml-1\\">no</span>", '
                          b'"", '
                          b'"<a class=\\"btn-outline-danger m-0 p-1\\" href=\\"/scxrd/measurements/edit/1/\\">Edit</a>"]], '
                          b'"result": "ok"}'))
