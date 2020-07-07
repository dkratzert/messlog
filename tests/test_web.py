import unittest

from django.contrib.auth.models import User
from django.test import override_settings, TestCase
from django.urls import reverse

from scxrd.customer_models import Sample
from scxrd.models import Experiment
from tests.tests import MEDIA_ROOT, DeleteFilesMixin, PlainUserMixin, AnonUserMixin


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestNotAuthenticated(DeleteFilesMixin, AnonUserMixin, TestCase):

    def test_anonymous_cannot_see_page(self):
        response = self.client.get(reverse("scxrd:submit_sample"))
        self.assertRedirects(response, "/accounts/login/?next=%2Fscxrd%2Fsubmit%2F")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestNewSampleSubmit(DeleteFilesMixin, PlainUserMixin, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data = {
            "sample_name"               : "DK_ml_766",
            "sum_formula"               : "C6H12O2",
            "stable"                    : "True",
            "solve_refine_selve"        : "False",
            "crystallization_conditions": "From CH2Cl2 at RT",
            "reaction_path"             : "File",
            "desired_struct_draw"       : "SVG",
            "special_remarks"           : "Would love to talk about Philip K. Dick",
        }

    def test_user(self):
        self.assertEqual(str(User.objects.first()), 'testuser')

    def test_register(self):
        self.assertEqual((self.user is not None and self.user.is_authenticated), True)

    def test_get_request(self):
        response = self.client.get(reverse("scxrd:submit_sample"), follow=True, data=self.data)
        self.assertTemplateUsed(response, 'scxrd/new_sample_by_customer.html')

    def test_post_request(self):
        response = self.client.post(reverse("scxrd:submit_sample"), follow=False, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'index.html')
        self.assertEqual(Sample.objects.count(), 1)

    def test_post_request_folow(self):
        response = self.client.post(reverse("scxrd:submit_sample"), follow=True, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(Sample.objects.first().sample_name, 'DK_ml_766')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestNewExpFromSample(DeleteFilesMixin, PlainUserMixin, AnonUserMixin, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data1 = {
            "sample_name"               : "DK_ml_766",
            "sum_formula"               : "C6H12O2",
            "stable"                    : "True",
            "solve_refine_selve"        : "False",
            "crystallization_conditions": "From CH2Cl2 at RT",
            "reaction_path"             : "File",
            "desired_struct_draw"       : "SVG",
            "special_remarks"           : "Would love to talk about Philip K. Dick",
        }
        self.data2 = {
            "machine"                   : 1,
            'experiment_name'           : "DK_ml_766",
            'number'                    : 1,
            'base'                      : 1,
            'crystal_size_x'            : 0.1,
            'crystal_size_y'            : 0.1,
            'crystal_size_z'            : 0.1,
            'measurement_temp'          : 100,
            'crystal_colour'            : 3,
            'crystal_habit'             : 'block',
            'customer'                  : 1,
            "crystallization_conditions": "From CH2Cl2 at RT",
            "conditions": "From CH2Cl2 at RT",
            "sample_name"               : "DK_ml_766",
            "sum_formula"               : "C6H12O2",
            "stable"                    : "True",
            "solve_refine_selve"        : "False",
            "reaction_path"             : "File",
            "desired_struct_draw"       : "SVG",
            "special_remarks"           : "Would love to talk about Philip K. Dick",
        }

    def test_user(self):
        self.assertEqual(str(User.objects.first()), 'testuser')

    def test_register(self):
        self.assertEqual((self.user is not None and self.user.is_authenticated), True)

    def test_get_request(self):
        url = reverse("scxrd:new_exp_from_sample", args=(1,))
        response1 = self.client.get(reverse("scxrd:submit_sample"), follow=True)
        self.assertTemplateUsed(response1, 'scxrd/new_sample_by_customer.html')
        self.assertEqual(url, '/scxrd/newexp/1/')
        self.assertEqual(response1.status_code, 200)
        response1 = self.client.post(reverse("scxrd:submit_sample"), follow=True, data=self.data1)
        self.assertEqual(Sample.objects.count(), 1)

    @unittest.skip('')
    def test_post_data(self):
        url = reverse("scxrd:new_exp_from_sample", args=(1,))
        # TODO: I might use a different template here:
        # self.assertTemplateUsed(response2, 'scxrd/experiment_new.html')
        self.assertEqual(Experiment.objects.count(), 0)
        response1 = self.client.post(reverse("scxrd:submit_sample"), follow=True, data=self.data1)
        self.assertEqual(Sample.objects.count(), 1)
        response2 = self.client.get(url, follow=False, data=self.data2, pk=1)
        response2 = self.client.post(url, follow=False, data=self.data2, pk=1)
        #response2 = self.client.post(url, follow=False, data=self.data2)
        self.assertEqual(Experiment.objects.count(), 1)
        self.assertEqual(response2.status_code, 200)

