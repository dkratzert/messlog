from django.test import TestCase, override_settings

from tests.tests import DeleteFilesMixin, MEDIA_ROOT, Operator_user_Mixin


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestNewSampleByCustomerView(DeleteFilesMixin, Operator_user_Mixin, TestCase):

    def test_status_code(self):
        print('#####foo')
