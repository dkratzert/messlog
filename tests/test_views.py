from pprint import pprint

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase, override_settings, Client, RequestFactory
from django.urls import reverse, reverse_lazy

from scxrd.forms.edit_experiment import ExperimentEditForm
from scxrd.views import NewSampleByCustomer
from tests.tests import MEDIA_ROOT, DeleteFilesMixin, OperatorUserMixin, SetupUserMixin, PlainUserMixin


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
class TestNewSampleByCustomerView(DeleteFilesMixin, OperatorUserMixin, SetupUserMixin, TestCase):

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
class TestAuthenticatedLogin(DeleteFilesMixin, PlainUserMixin, SetupUserMixin, TestCase):

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
