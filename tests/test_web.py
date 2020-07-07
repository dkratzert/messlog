from pprint import pprint

from django.contrib.auth.models import User
from django.test import override_settings, TestCase
from django.urls import reverse

from scxrd.customer_models import Sample
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