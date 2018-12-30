# Create your tests here.
from datetime import datetime
from pathlib import Path
from pprint import pprint

import pytz
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from scxrd.cif.cifparser import Cif
from scxrd.models import Experiment, Customer, Machine

"""
TODO: 
The position of 
migrations.CreateModel(
    name='Machine',
    [...]
is critical. By default, its position in the migration is faulty.         
"""


def create_experiment(number, cif=None):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    cust = Customer.objects.create(name='Horst', last_name='Meyerhof')
    mach = Machine.objects.create(name='FobarMachine')
    op = User.objects.create(username='foouser')
    exp = Experiment.objects.create(
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

    def test_no_experiements(self):
        response = self.client.get(reverse('scxrd:index'))
        # print('response:', response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['request']), "<WSGIRequest: GET '/scxrd/'>")
        # pprint(response.context)
        # pprint(response.content)


class ExperimentCreateTest(TestCase):
    def test_makeexp(self):
        ex = create_experiment(100)
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




if __name__ == '__main':
    pass
    # create_experiment(12)
