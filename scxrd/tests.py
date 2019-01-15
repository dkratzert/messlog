# Create your tests here.
import tempfile
from datetime import datetime
from pathlib import Path

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from scxrd.cif.cifparser import Cif
from scxrd.cif_model import CifFile
from scxrd.models import Experiment, Machine, Person, WorkGroup, Solvent, CrystalSupport, CrystalGlue, CrystalShape

"""
TODO: 
The position of 
migrations.CreateModel(
    name='Machine',
    [...]
is critical. By default, its position in the migration is faulty.      

- Test atoms   
"""


def create_experiment(number, cif=None, save_related=False):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    head = Person(first_name='Susi', last_name='Sorglos')
    head.save()
    group = WorkGroup(group_head=head)
    group.save()
    pers = Person(first_name='Hans', last_name='Meyerhof', work_group=group)
    mach = Machine(name='FobarMachine')
    op = User(username='foouser')
    glue = CrystalGlue(glue='grease')
    if save_related:
        group.save()
        glue.save()
        pers.save()
        mach.save()
        op.save()
    exp = Experiment(
        experiment='test1',
        machine=mach,
        number=number,
        customer=pers,
        glue=glue,
        sum_formula='C5H10O2',
        measure_date=datetime(2013, 11, 20, 20, 8, 7, 127325, tzinfo=pytz.UTC),
        operator=op,
        cif=cif
    )
    return exp


class ExperimentIndexViewTests(TestCase):

    def test_no_experiements(self):
        response = self.client.get(reverse('scxrd:index'))
        # print('response:', response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['request']), "<WSGIRequest: GET '/scxrd/'>")


class ExperimentCreateTest(TestCase):

    def test_makeexp(self):
        file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        c = CifFile(cif_file_on_disk=file)
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
        self.assertEqual(str(ex.customer.first_name), 'Hans')
        self.assertEqual(str(ex.customer.last_name), 'Meyerhof')
        ex.cif.delete()


class ExperimentCreateCif(TestCase):

    def test_parsecif(self):
        self.cif = Cif()
        self.cif.parsefile(Path('scxrd/testfiles/p21c.cif').read_text(encoding='ascii').splitlines(keepends=True))
        self.assertEqual(self.cif.cif_data['_diffrn_reflns_number'], '42245')
        self.assertEqual(self.cif.cif_data['_shelx_res_file'][:20], 'TITL p21c in P2(1)/c')


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
        c = CifFile(cif_file_on_disk=file)
        ex = create_experiment(99, cif=c, save_related=True)
        self.assertEqual(ex.customer.first_name, 'Hans')
        self.assertEqual(ex.customer.last_name, 'Meyerhof')
        self.assertEqual(ex.operator.username, 'foouser')
        self.assertEqual(ex.cif.data, None)
        ex.cif.save()
        self.assertEqual(str(c.experiments.glue), 'grease')
        self.assertEqual(str(c.experiments), 'test1')
        self.assertEqual(str(c.experiments.customer.work_group), 'AK Sorglos')
        # Cif dictionary is populated during save():
        self.assertEqual(ex.cif.data, 'p21c')
        # ex.save() would delete the cif handle:
        ex.save_base()
        self.assertEqual(ex.cif.shelx_res_file[:20], 'TITL p21c in P2(1)/c')
        response = self.client.get(reverse('scxrd:details_table', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        # delete file afterwards:
        ex.cif.delete()


class WorkGroupTest(TestCase):

    def test_group_head(self):
        """
        Create the Person of a group first. Then the group itselv and finally
        define the group as work_group of the heads Person instance.
        """
        head = Person(first_name='Susi', last_name='Sorglos', email_adress='foo@bar.de')
        head.save()  # important
        group1 = WorkGroup(group_head=head)
        group1.save()  # important
        head.work_group = group1
        head.save()
        self.assertEqual(str(group1.group_head), 'Susi Sorglos*')
        dokt1 = Person(first_name='Sandra', last_name='Superschlau', email_adress='foo@bar.de', work_group=group1)
        dokt2 = Person(first_name='Heiner', last_name='Hirni', email_adress='foo@bar.de', work_group=group1)
        dokt1.save()
        dokt2.save()
        group1.save()
        self.assertEqual([str(x) for x in group1.person.all()], ["Susi Sorglos*", "Sandra Superschlau", "Heiner Hirni"])

    def test_validate_email(self):
        # TODO: why is it not evaluating?
        pers = Person(first_name='DAniel', last_name='Kratzert', email_adress='-!ß\/()')
        pers.save()
        #print(pers.email_adress)


class OtherTablesTest(TestCase):

    def other_test(self):
        solv = Solvent(name='Toluene')
        solv.save()
        self.assertEqual(str(solv), 'Toluene')

        mach = Machine(name='APEX')
        mach.save()
        self.assertEqual(str(mach), 'APEX')

        sup = CrystalSupport(support='Glass Fiber')
        sup.save()
        self.assertEqual(str(sup), 'Glass Fiber')

        glue = CrystalGlue(glue='perfluor ether oil')
        glue.save()
        self.assertEqual(str(glue), 'perfluor ether oil')

        shape = CrystalShape(habitus='block')
        shape = save()
        self.assertEqual(str(shape), 'block')

if __name__ == '__main':
    pass
    # create_experiment(12)
