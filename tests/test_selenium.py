import time

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
from selenium.webdriver.support.select import Select

from scxrd.models.experiment_model import Measurement
from scxrd.models.models import WorkGroup
from tests.tests import MEDIA_ROOT, DeleteFilesMixin, PlainUserMixin


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AccountChromeTestCase(DeleteFilesMixin, StaticLiveServerTestCase):
    port = 8001

    @classmethod
    def tearDownClass(cls):
        # noinspection PyUnresolvedReferences
        super().tearDownClass()

    def setUp(self):
        self.selenium = webdriver.Chrome()
        super().setUp()

    def tearDown(self):
        self.selenium.close()
        super().tearDown()

    # @unittest.skip('skipping, because it creates a persisting user. why?')
    def test_register(self):
        selenium = self.selenium
        # Opening the link we want to test
        selenium.get('http://127.0.0.1:8001/signup/')
        # find the form element
        first_name = selenium.find_element_by_id('id_first_name')
        last_name = selenium.find_element_by_id('id_last_name')
        username = selenium.find_element_by_id('id_username')
        email = selenium.find_element_by_id('id_email')
        group = selenium.find_element_by_id('id_work_group')
        phone = selenium.find_element_by_id('id_phone_number')
        password1 = selenium.find_element_by_id('id_password1')
        password2 = selenium.find_element_by_id('id_password2')

        submit = selenium.find_element_by_id('register')

        # Fill the form with data
        first_name.send_keys('Yusuf')
        last_name.send_keys('Unary')
        username.send_keys('unary')
        group.send_keys('AK Krossing')
        phone.send_keys('016512345')
        email.send_keys('yusuf@qawba.com')
        password1.send_keys('ms.kerh47i5z')
        password2.send_keys('ms.kerh47i5z')

        # submitting the form
        submit.send_keys(Keys.RETURN)
        print(selenium.page_source)
        assert '/scxrd/sample/submit/' in selenium.page_source
        assert '/scxrd/submit/mysamples/' in selenium.page_source


def submit_sample(selenium):
    # Opening the link we want to test
    login_user(selenium, username='testuser', password='Test1234!')
    selenium.get('http://127.0.0.1:8001/scxrd/sample/submit/')
    # time.sleep(0.5)
    sample_name = selenium.find_element_by_id('id_sample_name')
    formula = selenium.find_element_by_id('id_sum_formula')
    cryst_cond = selenium.find_element_by_id('id_crystallization_conditions')
    ketcherbutton = selenium.find_element_by_id('id_reaction_path_button')
    ketcherbutton.click()
    # time.sleep(0.5)
    selenium.switch_to.frame('ketcher-frame')
    benzenesymbol = selenium.find_element_by_id('template-0')
    draw_canvas = selenium.find_element_by_id('canvas')
    benzenesymbol.click()
    draw_canvas.click()
    selenium.switch_to.parent_frame()
    # time.sleep(0.5)
    remarks = selenium.find_element_by_id('id_special_remarks')
    submit = selenium.find_element_by_id('submit-id-save')
    sample_name.send_keys('testsample_123')
    formula.send_keys('C2H5OH')
    cryst_cond.send_keys('From CH2CL2 by cooling to 6°C')
    remarks.send_keys('this is a comment')
    submit.send_keys(Keys.RETURN)
    # time.sleep(0.5)
    # print(selenium.page_source)


def login_user(selenium, username='', password=''):
    selenium.get('http://127.0.0.1:8001/scxrd/sample/submit/')
    # time.sleep(0.5)
    userfield = selenium.find_element_by_id('id_username')
    passwordfield = selenium.find_element_by_id('id_password')
    userfield.send_keys(username)
    passwordfield.send_keys(password)
    submit = selenium.find_element_by_id('id_submit')
    submit.send_keys(Keys.RETURN)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NewSampleChromeTestCase(DeleteFilesMixin, PlainUserMixin, StaticLiveServerTestCase):
    port = 8001

    def setUp(self):
        self.selenium = webdriver.Chrome()
        super().setUp()

    def tearDown(self):
        self.selenium.close()
        self.selenium.quit()
        super().tearDown()

    # @unittest.skip('')
    def test_new_sample(self):
        selenium = self.selenium
        submit_sample(selenium)
        assert 'Probe erfolgreich abgeben' in selenium.page_source


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ExperimentFromSampleChromeTestCase(DeleteFilesMixin, PlainUserMixin, StaticLiveServerTestCase):
    port = 8001

    def setUp(self):
        self.selenium = webdriver.Chrome()
        super().setUp()

    def tearDown(self):
        self.selenium.close()
        self.selenium.quit()
        super().tearDown()

    # @unittest.skip('')
    def test_exp_from_sample(self):
        selenium = self.selenium
        submit_sample(selenium)
        selenium.find_element_by_id('id_ok_button').send_keys(Keys.RETURN)
        selenium.find_element_by_id('logout_button').send_keys(Keys.RETURN)
        group = WorkGroup.objects.create(group_head='Krabäppel')
        user = User.objects.create_user(username='testuser_operator', email='test@test.com', is_active=True, is_superuser=True,
                                        password='Test1234!')
        user.profile.is_operator = True
        user.profile.work_group = group
        user.save()
        login_user(selenium, username='testuser_operator', password='Test1234!')
        selenium.get('http://127.0.0.1:8001/scxrd/newexp/1/')
        #TODO: test what happens if I change the sample name
        selenium.find_element_by_id('id_measurement_temp').send_keys('101.5')
        self.select_choicefield(selenium, field_id='id_machine', choice='VENTURE')
        selenium.find_element_by_id('id_end_time').send_keys('2020-07-19 09:01')
        self.select_choicefield(selenium, field_id='id_base', choice='glass fiber')
        self.select_choicefield(selenium, field_id='id_glue', choice='grease')
        self.assertEqual(selenium.find_element_by_id('id_sum_formula').get_attribute('value'), 'C2H5OH')
        self.assertEqual(selenium.find_element_by_id('id_experiment_name').get_attribute('value'), 'testsample_123')
        selenium.find_element_by_id('id_crystal_habit').send_keys('block')
        selenium.find_element_by_id('id_crystal_size_z').send_keys('0.067')
        selenium.find_element_by_id('id_crystal_size_y').send_keys('0.079')
        selenium.find_element_by_id('id_crystal_size_x').send_keys('0.099')
        self.assertEqual(selenium.find_element_by_id('id_exptl_special_details').get_attribute('value'), 'this is a comment')
        selenium.find_element_by_id('id_exptl_special_details').send_keys('\nsome more comments')
        selenium.find_element_by_id('id_prelim_unit_cell').send_keys('12.12 13.654 29.374 90 108.5 90')
        # send
        selenium.find_element_by_id('submit-id-save').send_keys(Keys.RETURN)
        assert 'Erfolgreich gespeichert' in selenium.page_source
        self.assertEqual(str(Measurement.objects.last()), 'testsample_123')

    def select_choicefield(self, selenium, field_id, choice):
        mach = selenium.find_element_by_id(field_id)
        Select(mach).select_by_visible_text(choice)