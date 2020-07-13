from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.test import TestCase, override_settings, Client
from django.urls import reverse_lazy

from scxrd.forms.new_experiment import ExperimentNewForm
from scxrd.forms.new_sample import SubmitNewSampleForm
from scxrd.models.sample_model import Sample
from tests.tests import MEDIA_ROOT, DeleteFilesMixin, OperatorUserMixin


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestNewSampleForm(DeleteFilesMixin, TestCase):
    def setUp(self) -> None:
        self.data = {
            "sample_name"               : "Juliana",
            "sum_formula"               : "C5H5",
            "crystallization_conditions": "Would love to talk about John K. Dick",
            "desired_struct_draw"       : "Would love to talk about Philip K. Dick",
            "reaction_path"             : "uploaded file",
            "special_remarks"           : 'foobar!',
            "stable"                    : 'true',
            "solve_refine_selve"        : 'false',
        }
        user = User.objects.create(username='testuser', email='test@test.com', is_active=True, is_superuser=False)
        user.set_password('Test1234!')
        user.save()
        self.client = Client()
        self.client.login(username='testuser', password='Test1234!')

    def test_submit_new_sample(self):
        form = SubmitNewSampleForm(self.data)
        self.assertEqual(True, form.is_valid())
        sample: Sample = form.save()
        self.assertEqual('Juliana', str(sample))
        self.assertEqual(1, sample.pk)
        self.assertEqual(False, sample.solve_refine_selve)
        self.assertEqual(True, sample.stable)
        self.assertEqual('Would love to talk about Philip K. Dick', sample.desired_struct_draw)
        self.assertEqual('Juliana', sample.sample_name)
        self.assertEqual('foobar!', sample.special_remarks)
        self.assertEqual('C5H5', sample.sum_formula)
        self.assertNotEqual('C5H5', sample.crystallization_conditions)
        self.assertEqual('Would love to talk about John K. Dick', sample.crystallization_conditions)
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

    def getform(self):
        response: HttpResponse = self.app.get(path=reverse_lazy("scxrd:submit_sample"), data=self.data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual('OK', response.reason_phrase)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestNewExperimentForm(DeleteFilesMixin, OperatorUserMixin, TestCase):
    def setUp(self) -> None:
        self.data = {
            # The minimum requirements:
            "experiment_name" : "A_test_123",
            "number"          : 100,
            "machine"         : 1,
            "measurement_temp": 100.15,
            'end_time'        : '2020-07-03 09:37:19',
            "base"            : '1',
            "crystal_colour"  : 3,
            "crystal_habit"   : 2,
            "crystal_size_x"  : '0.12',
            "crystal_size_y"  : '0.132',
            "crystal_size_z"  : '0.21',
            'user'            : 1,
        }

    def test_create_new_experiment(self):
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(True, form.is_valid())
        sample: Sample = form.save()
        self.assertNotEqual('Juliana', str(sample))
        self.assertEqual('A_test_123', str(sample))

    def test_name_missing(self):
        self.data['experiment_name'] = ''
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_number_missing(self):
        self.data.pop('number')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(True, form.is_valid())
        with self.assertRaises(IntegrityError):
            form.save()

    def test_machine_missing(self):
        self.data.pop('machine')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_measurement_temp_missing(self):
        self.data.pop('measurement_temp')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_end_time_missing(self):
        self.data.pop('end_time')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_base_missing(self):
        self.data.pop('base')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_crystal_colour(self):
        self.data.pop('crystal_colour')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_crystal_habit(self):
        self.data.pop('crystal_habit')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_crystal_size_x(self):
        self.data.pop('crystal_size_x')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_crystal_size_y(self):
        self.data.pop('crystal_size_y')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_crystal_size_z(self):
        self.data.pop('crystal_size_z')
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(False, form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_add_glue(self):
        self.data['glue'] = 1
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(True, form.is_valid())
        form.save()

    def test_add_sum_formula(self):
        self.data['sum_formula'] = 'C2H5OH'
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(True, form.is_valid())
        form.save()

    def test_add_prelim_unit_cell(self):
        self.data['prelim_unit_cell'] = '10 10 10 90 90 90'
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(True, form.is_valid())
        form.save()

    def test_add_exptl_special_details(self):
        self.data['exptl_special_details'] = 'This is a test'
        form = ExperimentNewForm(self.data, user=1)
        self.assertEqual(True, form.is_valid())
        form.save()