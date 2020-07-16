from pathlib import Path

import gemmi
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from scxrd.cif.cif_file_io import CifContainer
from scxrd.models.cif_model import CifFileModel
from scxrd.models.experiment_model import Measurement
from scxrd.models.models import model_fixtures, Machine, CrystalSupport, CrystalGlue, WorkGroup
from scxrd.models.sample_model import Sample
from scxrd.utils import generate_sha256
from tests.tests import MEDIA_ROOT, create_experiment, DeleteFilesMixin, PlainUserMixin, OperatorUserMixin, \
    SuperUserMixin


# TODO: tests for write protection of experiment, file uploads

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestUser(PlainUserMixin, DeleteFilesMixin, TestCase):

    def test_string_class(self):
        """"""
        u = User.objects.get(pk=1)
        self.assertEqual(str(u), 'testuser')

    def test_string_username(self):
        u = User.objects.get(pk=1)
        u.first_name = 'Bob'
        u.last_name = 'Barker'
        u.save(update_fields=('first_name', 'last_name'))
        self.assertEqual(str(u), 'testuser')

    def test_if_plain_user(self):
        u, created = User.objects.get_or_create(pk=1)
        self.assertEqual(created, False)
        self.assertEqual(u.profile.is_operator, False)
        self.assertEqual(u.is_staff, False)
        self.assertEqual(u.is_superuser, False)
        u.profile.is_operator = True
        u.save()
        self.assertEqual(User.objects.get(pk=1).profile.is_operator, True)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestOperatorProfile(OperatorUserMixin, DeleteFilesMixin, TestCase):

    def test_string_class(self):
        """Testing the string representation of a user with empty profile"""
        u = User.objects.get(pk=1)
        self.assertEqual(str(u), 'testuser')

    def test_string_username(self):
        u = User.objects.get(pk=1)
        self.assertEqual(str(u), 'testuser')
        self.assertNotEqual(str(u.profile), 'Bob Barker')
        self.assertEqual(str(u.profile), 'Sandra Sorglos')
        self.assertEqual(u.profile.house_number, '31')
        self.assertEqual(u.profile.town, 'Bartown')
        self.assertEqual(str(u.profile.work_group), 'AK Krabäppel')

    def test_rights(self):
        """Test if he has operator rights"""
        u = User.objects.get(pk=1)
        self.assertEqual(u.profile.is_operator, True)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestSuperuserProfile(SuperUserMixin, DeleteFilesMixin, TestCase):

    def test_string_class(self):
        """Testing the string representation of a user with empty profile"""
        u = User.objects.get(pk=1)
        self.assertEqual(str(u), 'elefant')

    def test_string_username(self):
        u = User.objects.get(pk=1)
        self.assertEqual(str(u), 'elefant')
        self.assertNotEqual(str(u.profile), 'Bob Barker')
        self.assertEqual(str(u.profile), 'Benjamin Blümchen')
        self.assertEqual(u.profile.house_number, '3')
        self.assertEqual(u.profile.town, 'Freudenstadt')
        self.assertEqual(str(u.profile.work_group), 'AK Blümchen')

    def test_rights(self):
        """Test if he has superuser rights"""
        u = User.objects.get(pk=1)
        self.assertEqual(u.profile.is_operator, False)
        self.assertEqual(u.is_superuser, True)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestExperimentCreateTest(DeleteFilesMixin, TestCase):
    fixtures = model_fixtures

    def setUp(self) -> None:
        cif_model = CifFileModel()
        cif_file = SimpleUploadedFile('p21c.cif', Path('scxrd/testfiles/p21c.cif').read_bytes())
        cif = CifContainer(chunks='\n'.join([x.decode(encoding='cp1250', errors='ignore') for x in cif_file.chunks()]))
        cif_model.fill_residuals_table(cif)
        cif_model.sha256 = generate_sha256(cif_file)
        cif_model.filesize = cif_file.size
        cif_model.cif_file_on_disk = cif_file
        self.exp = create_experiment()
        cif_model.experiment = self.exp
        cif_model.save()
        self.cif_model = cif_model

    def test_make_exp(self):
        self.assertEqual('IK_MSJg20_100K', str(self.exp))
        self.assertEqual('susi', str(self.exp.operator))
        self.assertEqual('C5H10O2', self.exp.sum_formula)
        self.assertEqual('2013-11-20 20:08:07.127325+00:00', str(self.exp.measure_date))
        self.assertEqual(1, self.exp.pk)
        self.assertEqual('APEXII', str(self.exp.machine))
        self.assertEqual('Hansi', str(self.exp.customer.first_name))
        self.assertEqual('Hinterseer', str(self.exp.customer.last_name))

    def test_string_representation(self):
        entry = Measurement(experiment_name="My entry title")
        self.assertEqual(str(entry), entry.experiment_name)

    def test_cif_model(self):
        self.assertEqual(self.cif_model.sha256, 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a')
        self.assertEqual(self.cif_model.data, 'p21c')
        self.assertEqual(self.cif_model.wr2_in_percent(), 4.0)
        self.assertEqual(self.cif_model.r1_in_percent(), 10.1)
        self.assertEqual(self.cif_model.experiment.was_measured, True)

    def test_cif_workgroup(self):
        self.assertEqual(str(self.cif_model.experiment.operator.profile.work_group), 'AK Krossing')
        self.assertEqual(str(self.cif_model.experiment.customer.profile.work_group), 'AK Hillebrecht')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestSampleCreate(DeleteFilesMixin, TestCase):

    def test_sample(self):
        user = User.objects.create(username='foo', last_name='Bar', first_name='Foo')
        user.profile.work_group = WorkGroup.objects.get(group_head__contains='Krossing')
        user.save()
        s: Sample = Sample.objects.create(
            sample_name='DK_123_b',
            sum_formula='C6H12O6',
            submit_date='2020-03-02',
            crystallization_conditions='From methanol at room temperature by evaporation',
            solve_refine_selve=False,
            customer_samp=user,
            stable=True,
        )
        s.save()
        self.assertEqual(str(Sample.objects.first().customer_samp.profile.work_group), 'AK Krossing')
        self.assertEqual(Sample.objects.first().sum_formula, 'C6H12O6')
        self.assertEqual(str(Sample.objects.first()), 'DK_123_b')
        self.assertEqual(str(Sample.objects.last()), 'DK_123_b')
        self.assertEqual(Sample.objects.last().stable, True)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestExperimentCreateCif(DeleteFilesMixin, TestCase):

    def test_parsecif(self):
        struct = gemmi.cif.read_file('scxrd/testfiles/p21c.cif')
        struct.sole_block()
        b = struct.sole_block()
        self.assertEqual(b.find_value('_diffrn_reflns_number'), '42245')
        self.assertEqual(b.find_value('_shelx_res_file').replace('\r\n', '')
                         .replace('\n', '')[:20], ';TITL p21c in P2(1)/')
        lo = b.find_loop('_atom_site_label')
        self.assertEqual(lo[1], 'C1_6')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestWorkGroup(DeleteFilesMixin, TestCase):

    def test_user_company(self):
        user = User(first_name='Susie', last_name='Sorglos', email='foo@bar.de', username='susi')
        user.save()  # important
        user.profile.company = 'A Company'
        self.assertEqual('Susie Sorglos', str(user.profile))
        self.assertEqual('A Company', str(user.profile.company))

    def test_group_head(self):
        """
        Create the Person of a group first. Then the group itselv and finally
        define the group as work_group of the heads Person instance.
        """
        user1 = User(username='sandra', first_name='Sandra', last_name='Superschlau', email='foo@bar.de')
        user2 = User(username='hein', first_name='Heiner', last_name='Hirni', email='foo@bar.de')
        group = WorkGroup(group_head='group1')
        group.save()
        user1.save()
        user2.save()
        user1.profile.town = 'Freiburg'
        user1.profile.work_group = group
        user2.profile.work_group = group
        # the second save is necessary:
        user1.save()
        user2.save()
        self.assertEqual(User.objects.filter(username='sandra').first().profile.town, 'Freiburg')
        self.assertEqual(str(User.objects.filter(username='sandra').first().profile.work_group), 'AK group1')

    def test_validate_email(self):
        pers = User(first_name='DAniel', last_name='Kratzert', email='-!ß\/()')
        pers.save()
        self.assertEqual(pers.email, '-!ß\/()')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestOtherTables(DeleteFilesMixin, TestCase):

    def test_machine(self):
        mach = Machine.objects.get(diffrn_measurement_device__contains='APEXII')
        self.assertEqual('APEXII', str(mach))
        self.assertEqual('Bruker APEXII QUAZAR', mach.diffrn_measurement_device)
        self.assertEqual('APEXII', mach.diffrn_measurement_device_type)

    def test_supports(self):
        sup = CrystalSupport.objects.get(support__contains='fiber')
        self.assertEqual(str(sup), 'glass fiber')
        sup = CrystalSupport(support='glass rod')
        sup.save()
        self.assertEqual(str(sup), 'glass rod')

    def test_glues(self):
        g = CrystalGlue.objects.get(glue__contains='polyether')
        self.assertEqual(str(g), 'polyether oil')
        glue = CrystalGlue(glue='other ether oil')
        glue.save()
        self.assertEqual(str(glue), 'other ether oil')
