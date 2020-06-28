# Create your tests here.
import sys
import tempfile
import unittest
from datetime import datetime
from io import BytesIO
from pathlib import Path
from wsgiref.handlers import SimpleHandler

import gemmi
import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from scxrd.cif_model import CifFileModel
from scxrd.models import Experiment, Machine, Profile, WorkGroup, CrystalSupport, CrystalGlue

"""
TODO:      

- Test atoms   
"""


class HomeTests(TestCase):
    def test_home_view_status_code(self):
        url = reverse('scxrd:index')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)


def create_experiment(number, cif=None, save_related=False):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    head = Profile(first_name='Susi', last_name='Sorglos')
    head.save()
    group = WorkGroup(group_head=head)
    group.save()
    pers = Profile(first_name='Hans', last_name='Meyerhof', work_group=group)
    mach = Machine(diffrn_measurement_device_type='FobarMachine')
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
        response = self.client.get(reverse('scxrd:index'), follow=True)
        # print('response:', response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("<WSGIRequest: GET '/accounts/login/?next=%2Fscxrd%2F'>", str(response.context['request']))


class ExperimentCreateTest(TestCase):

    def test_makeexp(self):
        file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        c = CifFileModel(cif_file_on_disk=file)
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

    def test_string_representation(self):
        entry = Experiment(experiment="My entry title")
        self.assertEqual(str(entry), entry.experiment)


class ExperimentCreateCif(TestCase):

    def test_parsecif(self):
        struct = gemmi.cif.read_file('scxrd/testfiles/p21c.cif')
        struct.sole_block()
        b = struct.sole_block()
        self.assertEqual(b.find_value('_diffrn_reflns_number'), '42245')
        self.assertEqual(b.find_value('_shelx_res_file').replace('\r\n', '')
                         .replace('\n', '')[:20], ';TITL p21c in P2(1)/')
        lo = b.find_loop('_atom_site_label')
        self.assertEqual(lo[1], 'Al1')


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
            response = self.client.post('/scxrd/upload/1/', {'name': 'p21c.cif', 'attachment': fp}, follow=True)
            self.assertEqual(response.status_code, 200)


class CifFileTest(TestCase):

    def test_saveCif(self):
        file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        c = CifFileModel(cif_file_on_disk=file)
        ex = create_experiment(99, cif=c, save_related=True)
        self.assertEqual(ex.customer.first_name, 'Hans')
        self.assertEqual(ex.customer.last_name, 'Meyerhof')
        self.assertEqual(ex.operator.username, 'foouser')
        self.assertEqual(ex.cif.data, None)
        ex.cif.save()
        first_atom = CifFileModel.objects.first().atom_set.first()
        self.assertEqual(0.63951, first_atom.x)
        self.assertEqual(str(c.experiments.glue), 'grease')
        self.assertEqual(str(c.experiments), 'test1')
        self.assertEqual(str(c.experiments.customer.work_group), 'AK Sorglos')
        # Cif dictionary is populated during save():
        self.assertEqual(ex.cif.data, 'p21c')
        # ex.save() would delete the cif handle:
        ex.save_base()
        self.assertEqual(ex.cif.wr2_in_percent(), 10.1)
        self.assertEqual(ex.cif.refine_ls_wR_factor_ref, 0.1014)
        self.assertEqual(ex.cif.shelx_res_file.replace('\r\n', '').replace('\n', '').replace('\r', '')[:30],
                         'TITL p21c in P2(1)/c    p21c.r')
        # self.assertEqual(ex.cif.atoms.x, '')
        self.assertEqual(ex.cif.space_group_name_H_M_alt, 'P 21/c')
        response = self.client.get(reverse('scxrd:details_table', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        # delete file afterwards:
        ex.cif.delete()

    def test_read_cif_content_by_gemmi(self):
        self.assertEqual(['_diffrn_reflns_number', '42245'], CifFileModel.get_cif_item('scxrd/testfiles/p21c.cif',
                                                                                       '_diffrn_reflns_number'))
        # check
        self.assertEqual(['_diffrn_reflns_number', '22246'], CifFileModel.get_cif_item('scxrd/testfiles/p21c.cif',
                                                                                       '_diffrn_reflns_number'))


class WorkGroupTest(TestCase):

    def test_group_head(self):
        """
        Create the Person of a group first. Then the group itselv and finally
        define the group as work_group of the heads Person instance.
        """
        head = Profile(first_name='Susi', last_name='Sorglos', email_adress='foo@bar.de')
        head.save()  # important
        group1 = WorkGroup(group_head=head)
        group1.save()  # important
        head.work_group = group1
        head.save()
        self.assertEqual(str(group1.group_head), 'Susi Sorglos*')
        dokt1 = Profile(first_name='Sandra', last_name='Superschlau', email_adress='foo@bar.de', work_group=group1)
        dokt2 = Profile(first_name='Heiner', last_name='Hirni', email_adress='foo@bar.de', work_group=group1)
        dokt1.save()
        dokt2.save()
        group1.save()
        self.assertEqual([str(x) for x in group1.person.all()], ["Susi Sorglos*", "Sandra Superschlau", "Heiner Hirni"])

    def test_validate_email(self):
        # TODO: why is it not evaluating?
        pers = Profile(first_name='DAniel', last_name='Kratzert', email_adress='-!ß\/()')
        pers.save()
        # print(pers.email_adress)


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


def hello_app(environ, start_response):
    start_response("200 OK", [
        ('Content-Type', 'text/plain'),
        ('Date', 'Mon, 05 Jun 2006 18:49:54 GMT')
    ])
    return [b"Hello, world!"]


class TestWSGIRef(TestCase):

    @unittest.skip
    def testConnectionAbortedError(self):
        class AbortingWriter:
            def write(self, b):
                raise ConnectionAbortedError()

            def flush(self):
                pass

        environ = {"SERVER_PROTOCOL": "HTTP/1.0"}
        h = SimpleHandler(BytesIO(), AbortingWriter(), sys.stderr, environ)
        msg = "Client connection aborted"
        with self.assertWarnsRegex(RuntimeWarning, msg):
            h.run(hello_app)


class TestViews(TestCase):

    def test_report(self):
        response = self.client.get(reverse_lazy('scxrd:report', kwargs={'pk': 3}))
        self.assertEqual("/accounts/login/?next=/scxrd/report/3/", response.url)
        self.assertEqual(302, response.status_code)
        self.assertEqual("utf-8", response.charset)
        self.assertEqual("ResolverMatch(func=scxrd.views.ReportView, args=(), kwargs={'pk': 3}, url_name=report, "
                         "app_names=['scxrd'], namespaces=['scxrd'])", str(response.resolver_match))

    def test_post_data(self):
        response = self.client.post(reverse_lazy('scxrd:report', kwargs={'pk': 3}), data={'foo': 'bar'})


if __name__ == '__main':
    pass
    # create_experiment(12)
