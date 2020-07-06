from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase, override_settings, Client
from django.urls import reverse_lazy

from scxrd.customer_models import Sample
from scxrd.forms.new_cust_sample import SubmitNewSampleForm
from tests.tests import MEDIA_ROOT, DeleteFilesMixin


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestNewSampleForm(DeleteFilesMixin, TestCase):
    def setUp(self) -> None:
        self.data = {
            "sample_name"               : "Juliana",
            "sum_formula"               : "C5H5",
            "crystallization_conditions": "Would love to talk about John K. Dick",
            "desired_struct_draw"       : "Would love to talk about Philip K. Dick",
            "special_remarks"           : 'foobar!',
        }
        user = User.objects.create(username='testuser', email='test@test.com', is_active=True, is_superuser=False)
        user.set_password('Test1234!')
        user.save()
        self.client = Client()
        self.client.login(username='testuser', password='Test1234!')

    def test_submit_new_sample(self):
        form = SubmitNewSampleForm(self.data)
        self.assertEqual(True, form.is_valid())
        forminst: Sample = form.save()
        self.assertEqual('Juliana', str(forminst))
        self.assertEqual(1, forminst.pk)
        self.assertEqual(False, forminst.solve_refine_selve)
        self.assertEqual(False, forminst.stable)
        self.assertEqual('Would love to talk about Philip K. Dick', forminst.desired_struct_draw)
        self.assertEqual('Juliana', forminst.sample_name)
        self.assertEqual('foobar!', forminst.special_remarks)
        self.assertEqual('C5H5', forminst.sum_formula)
        self.assertNotEqual('C5H5', forminst.crystallization_conditions)
        self.assertEqual('Would love to talk about John K. Dick', forminst.crystallization_conditions)
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