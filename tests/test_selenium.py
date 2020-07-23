import time

import chromedriver_binary
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from scxrd.models.measurement_model import Measurement
from scxrd.models.models import WorkGroup
from tests.tests import MEDIA_ROOT, DeleteFilesMixin, PlainUserMixin, OperatorUserMixin, make_operator_user

chromedriver_binary.add_chromedriver_to_path()

SELENIUM_WEBDRIVERS = {
    'default': {
        'callable': webdriver.Chrome,
        'args'    : (),
        'kwargs'  : {},
    },
    'firefox': {
        'callable': webdriver.Firefox,
        'args'    : (),
        'kwargs'  : {},
    }
}


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
        time.sleep(0.6)
        print(selenium.page_source)
        #time.sleep(5)
        assert '/scxrd/sample/submit/' in selenium.page_source
        assert '/scxrd/submit/mysamples/' in selenium.page_source


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AccountFireFoxTestCase(AccountChromeTestCase, DeleteFilesMixin, StaticLiveServerTestCase):
    port = 8001

    def setUp(self):
        self.selenium = webdriver.Firefox()


def submit_sample(selenium, sample_name: str = 'testsample_123'):
    # Opening the link we want to test
    selenium.get('http://127.0.0.1:8001/scxrd/sample/submit/')
    time.sleep(0.4)
    selenium.find_element_by_id('id_sample_name').send_keys(sample_name)
    selenium.find_element_by_id('id_sum_formula').send_keys('C2H5OH')
    selenium.find_element_by_id('id_reaction_path_button').click()
    # open ketcher canvas:
    # Have to scroll down, otherwise firefox doesn't catch the canvas click:  
    selenium.execute_script('window.scrollTo(0,9999)')
    selenium.switch_to.frame('ketcher-frame')
    benzene_button = selenium.find_element_by_id('template-0')
    benzene_button.click()
    el = selenium.find_element_by_id('canvas')
    el.click()
    selenium.switch_to.parent_frame()
    # switch back and submit
    selenium.find_element_by_id('id_special_remarks').send_keys('this is a comment')
    selenium.find_element_by_id('id_crystallization_conditions').send_keys(u'From CH2CL2 by cooling to 6 °C')
    selenium.find_element_by_id('submit-id-save').send_keys(Keys.RETURN)
    time.sleep(0.2)
    # print(selenium.page_source)


def login_user(selenium, username='', password=''):
    selenium.get('http://127.0.0.1:8001/accounts/login/')
    time.sleep(0.1)
    selenium.find_element_by_id('id_username').send_keys(username)
    selenium.find_element_by_id('id_password').send_keys(password)
    selenium.find_element_by_id('id_submit').send_keys(Keys.RETURN)


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
        login_user(selenium, username='testuser', password='Test1234!')
        time.sleep(0.1)
        submit_sample(selenium, sample_name='testsample_1234')
        assert 'Probe erfolgreich abgeben' in selenium.page_source


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NewSampleFirefoxTestCase(NewSampleChromeTestCase, DeleteFilesMixin, PlainUserMixin, StaticLiveServerTestCase):
    port = 8001

    def setUp(self):
        user = User.objects.create_user(username='testuser', email='test@test.com', is_active=True, is_superuser=False,
                                        password='Test1234!')
        self.selenium = webdriver.Firefox()


def select_choicefield(selenium, field_id, choice):
    mach = selenium.find_element_by_id(field_id)
    Select(mach).select_by_visible_text(choice)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class MeasurementFromSampleChromeTestCase(DeleteFilesMixin, PlainUserMixin, StaticLiveServerTestCase):
    port = 8001

    def setUp(self):
        self.selenium = webdriver.Chrome()
        # self.selenium = webdriver.Firefox()
        super().setUp()

    def tearDown(self):
        self.selenium.close()
        self.selenium.quit()
        super().tearDown()

    # @unittest.skip('')
    def test_exp_from_sample(self):
        selenium = self.selenium
        login_user(selenium, username='testuser', password='Test1234!')
        time.sleep(0.2)
        submit_sample(selenium, sample_name='testsample_123')
        time.sleep(0.4)
        # The next lines fail if Firefox for example is unable to get the svg from ketcher:
        selenium.find_element_by_id('id_ok_button').send_keys(Keys.RETURN)
        time.sleep(0.2)
        selenium.find_element_by_id('logout_button').send_keys(Keys.RETURN)
        group = WorkGroup.objects.create(group_head='Krabäppel')
        user = User.objects.create_user(username='testuser_operator', email='test@test.com', is_active=True,
                                        is_superuser=True,
                                        password='Test1234!')
        user.profile.is_operator = True
        user.profile.work_group = group
        user.save()
        time.sleep(0.5)
        login_user(selenium, username='testuser_operator', password='Test1234!')
        time.sleep(0.8)
        selenium.get('http://127.0.0.1:8001/scxrd/new_measurement/1/')
        time.sleep(0.8)
        # TODO: test what happens if I change the sample name
        selenium.find_element_by_id('id_measurement_temp').send_keys('101.5')
        select_choicefield(selenium, field_id='id_machine', choice='VENTURE')
        selenium.find_element_by_id('id_end_time').send_keys('2020-07-19 09:01')
        select_choicefield(selenium, field_id='id_base', choice='glass fiber')
        select_choicefield(selenium, field_id='id_glue', choice='grease')
        select_choicefield(selenium, field_id='id_crystal_colour', choice='red')
        self.assertEqual(selenium.find_element_by_id('id_sum_formula').get_attribute('value'), 'C2H5OH')
        self.assertEqual(selenium.find_element_by_id('id_measurement_name').get_attribute('value'), 'testsample_123')
        selenium.find_element_by_id('id_crystal_habit').send_keys('block')
        # selenium.find_element_by_id('id_resolution').send_keys(0.781)
        selenium.find_element_by_id('id_crystal_size_z').send_keys('0.067')
        selenium.find_element_by_id('id_crystal_size_y').send_keys('0.079')
        selenium.find_element_by_id('id_crystal_size_x').send_keys('0.099')
        self.assertEqual(selenium.find_element_by_id('id_exptl_special_details').get_attribute('value'),
                         'this is a comment')
        selenium.find_element_by_id('id_exptl_special_details').send_keys('\nsome more comments')
        selenium.find_element_by_id('id_prelim_unit_cell').send_keys('12.12 13.654 29.374 90 108.5 90')
        # import time
        # time.sleep(0.2)
        # send
        selenium.find_element_by_id('submit-id-save').send_keys(Keys.RETURN)
        # assert 'Erfolgreich gespeichert' in selenium.page_source
        time.sleep(0.4)
        # Is Measurement there?
        self.assertEqual(str(Measurement.objects.last()), 'testsample_123')
        # Are all fields in db?
        self.assertEqual(Measurement.objects.last().measurement_name, 'testsample_123')
        self.assertEqual(Measurement.objects.last().sample.sample_name, 'testsample_123')
        self.assertEqual(Measurement.objects.last().sample.special_remarks, 'this is a comment')
        self.assertEqual(Measurement.objects.last().number, 1)
        self.assertEqual(Measurement.objects.last().publishable, False)
        self.assertEqual(str(Measurement.objects.last().customer), 'testuser')
        self.assertEqual(str(Measurement.objects.last().operator), 'testuser_operator')
        self.assertEqual(str(Measurement.objects.last().machine), 'VENTURE')
        self.assertEqual(Measurement.objects.last().sum_formula, 'C2H5OH')
        self.assertEqual(Measurement.objects.last().prelim_unit_cell, '12.12 13.654 29.374 90 108.5 90')
        self.assertEqual(Measurement.objects.last().resolution, None)
        # TODO: degree sign is not working in windows!
        # self.assertEqual(Measurement.objects.last().conditions, 'From CH2CL2 by cooling to 6 °C')
        # self.assertEqual(str(Measurement.objects.last().measure_date), '2020-07-19 16:49:51.952574+00:00')
        # self.assertEqual(str(Measurement.objects.last().submit_date), '2020-07-22')
        # self.assertEqual(str(Measurement.objects.last().result_date), '2020-07-19 16:53:00+00:00')
        # self.assertEqual(str(Measurement.objects.last().end_time), '2020-07-19 16:54:00+00:00')
        self.assertEqual(str(Measurement.objects.last().base), 'glass fiber')
        self.assertEqual(str(Measurement.objects.last().glue), 'grease')
        self.assertEqual(str(Measurement.objects.last().base), 'glass fiber')
        self.assertEqual(Measurement.objects.last().crystal_size_x, 0.099)
        self.assertEqual(Measurement.objects.last().crystal_size_y, 0.079)
        self.assertEqual(Measurement.objects.last().crystal_size_z, 0.067)
        self.assertEqual(Measurement.objects.last().measurement_temp, 101.5)
        self.assertEqual(Measurement.objects.last().crystal_colour, 6)
        self.assertEqual(Measurement.objects.last().crystal_colour_mod, 0)
        self.assertEqual(Measurement.objects.last().crystal_colour_lustre, 0)
        self.assertEqual(Measurement.objects.last().crystal_habit, 'block')
        self.assertEqual(Measurement.objects.last().exptl_special_details, 'this is a comment\r\nsome more comments')
        self.assertEqual(Measurement.objects.last().was_measured, True)
        self.assertEqual(Measurement.objects.last().not_measured_cause, '')
        self.assertEqual(Measurement.objects.last().final, False)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class MeasurementFromSampleFirefoxTestCase(MeasurementFromSampleChromeTestCase, DeleteFilesMixin, PlainUserMixin,
                                           StaticLiveServerTestCase):
    port = 8001

    def setUp(self):
        user = User.objects.create_user(username='testuser', email='test@test.com', is_active=True, is_superuser=False,
                                        password='Test1234!')
        self.user = user
        self.selenium = webdriver.Firefox()


# TODO: Add test that finalized experiment is write protected


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NewMeasuremenChromeTestCase(DeleteFilesMixin, OperatorUserMixin, StaticLiveServerTestCase):
    port = 8001

    def setUp(self):
        self.selenium = webdriver.Chrome()
        super().setUp()

    def tearDown(self):
        self.selenium.close()
        self.selenium.quit()
        super().tearDown()

    def test_new_experiment(self):
        selenium = self.selenium
        login_user(selenium, username='testuser', password='Test1234!')
        time.sleep(0.5)
        selenium.get('http://127.0.0.1:8001/scxrd/new_measurement/')
        time.sleep(0.5)
        selenium.find_element_by_id('id_measurement_name').send_keys('new_sample1')
        selenium.find_element_by_id('id_sum_formula').send_keys('C2H5OH')
        selenium.find_element_by_id('id_measurement_temp').send_keys('101.5')

        select_choicefield(selenium, field_id='id_machine', choice='VENTURE')
        selenium.find_element_by_id('id_end_time').send_keys('2020-07-19 09:01')
        select_choicefield(selenium, field_id='id_base', choice='glass fiber')
        select_choicefield(selenium, field_id='id_glue', choice='grease')
        select_choicefield(selenium, field_id='id_crystal_colour', choice='red')
        selenium.find_element_by_id('id_crystal_habit').send_keys('block')
        # selenium.find_element_by_id('id_resolution').send_keys(0.781)
        selenium.find_element_by_id('id_crystal_size_z').send_keys('0.067')
        selenium.find_element_by_id('id_crystal_size_y').send_keys('0.079')
        selenium.find_element_by_id('id_crystal_size_x').send_keys('0.099')
        selenium.find_element_by_id('id_exptl_special_details').send_keys('a comment')

        self.assertEqual(Measurement.objects.last(), None)
        selenium.find_element_by_id('submit-id-save').send_keys(Keys.RETURN)
        time.sleep(0.8)
        self.assertEqual(Measurement.objects.last().measurement_name, 'new_sample1')
        self.assertEqual(str(Measurement.objects.last().base), 'glass fiber')
        self.assertEqual(str(Measurement.objects.last().glue), 'grease')
        self.assertEqual(str(Measurement.objects.last().base), 'glass fiber')
        self.assertEqual(Measurement.objects.last().crystal_size_x, 0.099)
        self.assertEqual(Measurement.objects.last().crystal_size_y, 0.079)
        self.assertEqual(Measurement.objects.last().crystal_size_z, 0.067)
        self.assertEqual(Measurement.objects.last().measurement_temp, 101.5)
        self.assertEqual(Measurement.objects.last().crystal_colour, 6)
        self.assertEqual(Measurement.objects.last().crystal_habit, 'block')
        self.assertEqual(Measurement.objects.last().exptl_special_details, 'a comment')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NewMeasuremenFirefoxTestCase(NewMeasuremenChromeTestCase, DeleteFilesMixin, OperatorUserMixin,
                                   StaticLiveServerTestCase):
    port = 8001

    def setUp(self):
        u = make_operator_user()
        self.selenium = webdriver.Firefox()
