from django.test import TestCase, override_settings

from scxrd.models import model_fixtures
from tests.tests import MEDIA_ROOT, DeleteFilesMixin, OperatorUserMixin


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestNewSampleByCustomerView(DeleteFilesMixin, OperatorUserMixin, TestCase):

    def test_status_code(self):
        print('#####foo')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ExperimentIndexViewTests(DeleteFilesMixin, TestCase):
    fixtures = model_fixtures

    """def test_no_experiements(self):
        response = self.client.get(reverse('scxrd:index'), follow=True)
        # print('response:', response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("<WSGIRequest: GET '/accounts/login/?next=%2Fscxrd%2F'>", str(response.context['request']))
"""