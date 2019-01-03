# Create your tests here.
import tempfile
from datetime import datetime
from pathlib import Path

import pytz
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from scxrd.cif.cifparser import Cif
from scxrd.cif_model import CifFile
from scxrd.models import Experiment, Customer, Machine

"""
TODO: 
The position of 
migrations.CreateModel(
    name='Machine',
    [...]
is critical. By default, its position in the migration is faulty.         
"""


def create_experiment(number, cif=None, save_related=False):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    cust = Customer(name='Horst', last_name='Meyerhof')
    mach = Machine(name='FobarMachine')
    op = User(username='foouser')
    if save_related:
        cust.save()
        mach.save()
        op.save()
    exp = Experiment(
        experiment='test1',
        machine=mach,
        number=number,
        customer=cust,
        sum_formula='C5H10O2',
        measure_date=datetime(2013, 11, 20, 20, 8, 7, 127325, tzinfo=pytz.UTC),
        operator=op,
        cif=cif
    )
    return exp


class ExperimentIndexViewTests(TestCase):

    def setUp(self):
        settings.MEDIA_ROOT = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_no_experiements(self):
        response = self.client.get(reverse('scxrd:index'))
        # print('response:', response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['request']), "<WSGIRequest: GET '/scxrd/'>")


class ExperimentCreateTest(TestCase):
    def test_makeexp(self):
        file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        c = CifFile(cif=file)
        c.save()
        ex = create_experiment(100, cif=c, save_related=True)
        ex.save()
        self.assertEqual(str(ex), 'test1')
        self.assertEqual(ex.sum_formula, 'C5H10O2')
        self.assertEqual(ex.pk, 1)
        self.assertEqual(str(ex.operator), 'foouser')
        self.assertEqual(str(ex.measure_date), '2013-11-20 20:08:07.127325+00:00')
        self.assertEqual(str(ex.machine), 'FobarMachine')
        self.assertEqual(str(ex.operator), 'foouser')
        self.assertEqual(str(ex.customer.name), 'Horst')
        self.assertEqual(str(ex.customer.last_name), 'Meyerhof')


class ExperimentCreateCif(TestCase):

    def test_parsecif(self):
        self.cif = Cif()
        self.cif.parsefile(Path('scxrd/testfiles/p21c.cif').read_text(encoding='ascii').splitlines(keepends=True))
        self.assertEqual(self.cif.cif_data['_diffrn_reflns_number'], '42245')


class UploadTest(TestCase):

    def setUp(self):
        # setting MEDIA_ROOT to a temporary directory
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        self.tmp = settings.MEDIA_ROOT

    def tearDown(self):
        # removing temporary directory after tests
        import shutil
        shutil.rmtree(settings.MEDIA_ROOT)
        self.assertEqual(settings.MEDIA_ROOT, self.tmp)

    def test_uploadCif(self):
        with open('scxrd/testfiles/p21c.cif') as fp:
            response = self.client.post('/scxrd/upload/1/', {'name': 'p21c.cif', 'attachment': fp})
            self.assertEqual(response.status_code, 200)


class CifFileTest(TestCase):

    def test_saveCif(self):
        file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        c = CifFile(cif=file)
        ex = create_experiment(99, cif=c)
        # ex.customer.save()
        # ex.machine.save()
        # ex.operator.save()
        self.assertEqual(ex.customer.name, 'Horst')
        self.assertEqual(ex.customer.last_name, 'Meyerhof')
        self.assertEqual(ex.operator.username, 'foouser')
        self.assertEqual(ex.cif.data, None)
        ex.cif.save()
        # Cif dictionary is populated during save():
        self.assertEqual(ex.cif.data, 'p21c')
        print(ex.cif.data)
        # delete file afterwards:
        ex.cif.delete()


if __name__ == '__main':
    pass
    # create_experiment(12)
