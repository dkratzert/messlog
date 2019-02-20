import datetime
import textwrap

import gemmi
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, EmailValidator, RegexValidator
from django.db import models
# Create your models here.
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.cif_model import CifFile
from scxrd.datafiles.sadabs_model import SadabsModel
from scxrd.utils import COLOUR_CHOICES, COLOUR_MOD_CHOICES, COLOUR_LUSTRE_COICES

"""
TODO:

- addd delete experiment
- improve details page
- add upload results dropdown
- A really simple file upload handler: https://github.com/ipartola/django-upman
- https://github.com/sibtc/form-rendering-examples
- upload all needed files from work dir (foo.abs, foo.raw, foo_0m._ls, foo.prp, foo.lst, foo.res, foo.cif) and 
  have a button "generate report and final cif files"
- for charts: https://www.chartjs.org/docs/latest/
- http://ccbv.co.uk/projects/Django/2.0
"""


def validate_email(value):
    """
    Validate that a username is email like.
    """
    _validate_email = EmailValidator()
    try:
        _validate_email(value)
    except ValidationError:
        raise ValidationError(_('Enter a valid email address.'))
    return value


phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: "
                                         "'+999999999'. Up to 15 digits allowed.")


class Person(models.Model):
    """
    Persons where samples belong to.
    A Person is a Human that has no authentication.
    A Person does not need to have a User account.
    """
    # TODO: Check if this is a good idea:
    # user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, verbose_name='company', blank=True)
    work_group = models.ForeignKey('WorkGroup', related_name='person', max_length=200, blank=True, null=True,
                                   on_delete=models.DO_NOTHING)
    street = models.CharField(max_length=250, blank=True)
    house_number = models.CharField(max_length=200, blank=True)
    building = models.CharField(max_length=200, blank=True)
    town = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=200, blank=True)
    email_adress = models.EmailField(max_length=250, blank=True, validators=[validate_email])
    phone_number = models.CharField(max_length=17, blank=True
                                    # validators=[phone_validator],
                                    )
    comment = models.TextField(blank=True)

    def __str__(self):
        name = '{} {}'.format(self.first_name, self.last_name)
        try:
            self.work_group.group_head
        except AttributeError:
            return name
        else:
            if self.work_group.group_head == self:
                return name + '*'
            else:
                return name


class WorkGroup(models.Model):
    """
    A work group is a group of Person()s with a leading group_head (which is also a Person).
    """
    group_head = models.OneToOneField(Person, related_name='group', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "AK {}".format(self.group_head.last_name)


class Machine(models.Model):
    """
    A diffractometer name and type.
    """
    fixtures = ['machines']
    # The make, model or name of the measurement device (goniometer) used:
    diffrn_measurement_device_type = models.CharField(verbose_name="machine model name", max_length=200)
    # The general class of goniometer or device used to support and orient the specimen:
    # e.g. 'three-circle diffractometer'
    diffrn_measurement_device = models.CharField(verbose_name="machine type", max_length=200, null=True, blank=True)
    # A description of special aspects of the device used to measure the diffraction intensities:
    diffrn_measurement_device_details = models.CharField(verbose_name="machine special aspects",
                                                         max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.diffrn_measurement_device_type


class Solvent(models.Model):
    """
    A solvent to be used in the reaction or for crystallisation.
    """
    fixtures = ['solvents.json']
    name = models.CharField(verbose_name="solvents name", max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CrystalSupport(models.Model):
    """
    The support where the crystal was mounted on the diffraktometer.
    _diffrn_measurement_specimen_support e.g. 'glass capillary'
    """
    support = models.CharField(verbose_name='crystal support', max_length=200, unique=True)

    def __str__(self):
        return self.support

    #def __getattribute__(self, item):
    #    print('foo2')
    #    return dontknow


class CrystalGlue(models.Model):
    """
    What kind of addhesive was used?
    """
    glue = models.CharField(verbose_name='crystal glue', max_length=200, unique=True)

    def __str__(self):
        return self.glue


class CrystalShape(models.Model):
    """
    A description of the quality and habit of the crystal.
    """
    habitus = models.CharField(verbose_name='crystal shape', max_length=200, unique=True)

    def __str__(self):
        return self.habitus


class Experiment(models.Model):
    fixtures = ['experiment']
    experiment = models.CharField(verbose_name='experiment name', max_length=200, blank=False, default='', unique=True)
    number = models.PositiveIntegerField(verbose_name='number', unique=True, validators=[MinValueValidator(1)])
    publishable = models.BooleanField(verbose_name="structure is publishable", default=False)
    customer = models.ForeignKey(to=Person, on_delete=models.CASCADE, null=True, blank=True, related_name='experiment')
    # Operator has to be an authenticated User:
    operator = models.ForeignKey(User, verbose_name='operator', related_name='experiments', on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, verbose_name='diffractometer', on_delete=models.SET_NULL,
                                related_name='experiments', null=True, blank=True)
    sum_formula = models.CharField(max_length=300, verbose_name="sum formula", blank=True)
    prelim_unit_cell = models.CharField(max_length=250, blank=True, verbose_name='assumed formula')
    solvent1 = models.ForeignKey(Solvent, verbose_name='solvent 1', null=True, blank=True,
                                 related_name='experiment1', on_delete=models.CASCADE, default='')
    solvent2 = models.ForeignKey(Solvent, verbose_name='solvent 2', null=True, blank=True,
                                 related_name='experiment2', on_delete=models.CASCADE, default='')
    solvent3 = models.ForeignKey(Solvent, verbose_name='solvents 3', null=True, blank=True,
                                 related_name='experiment3', on_delete=models.CASCADE, default='')
    measure_date = models.DateTimeField(verbose_name='measurement date', default=timezone.now, blank=False)
    submit_date = models.DateField(verbose_name='sample submission date', blank=True, null=True)
    result_date = models.DateField(verbose_name='results sent date', blank=True, null=True)
    base = models.ForeignKey(CrystalSupport, verbose_name='sample base', related_name='+', blank=True, null=True,
                             on_delete=models.DO_NOTHING)
    glue = models.ForeignKey(CrystalGlue, verbose_name='sample glue', related_name='+', blank=True, null=True,
                             on_delete=models.DO_NOTHING)
    cif = models.OneToOneField(CifFile, null=True, blank=True, related_name="experiments",
                               verbose_name='cif file', on_delete=models.CASCADE)
    absfile = models.OneToOneField(SadabsModel, null=True, blank=True, related_name="experiments",
                                   verbose_name='sadabs list file', on_delete=models.CASCADE)
    crystal_size_x = models.FloatField(verbose_name='crystal size max', null=True, blank=True)
    crystal_size_y = models.FloatField(verbose_name='crystal size mid', null=True, blank=True)
    crystal_size_z = models.FloatField(verbose_name='crystal size min', null=True, blank=True)
    crystal_colour = models.IntegerField(choices=COLOUR_CHOICES, default=COLOUR_CHOICES[0][0])
    crystal_colour_mod = models.IntegerField(choices=COLOUR_MOD_CHOICES, verbose_name='crystal colour modifier',
                                             default=COLOUR_MOD_CHOICES[0][0])
    crystal_colour_lustre = models.IntegerField(choices=COLOUR_LUSTRE_COICES,
                                                default=COLOUR_LUSTRE_COICES[0][0])  # no blank=True here!
    # _exptl_special_details:
    exptl_special_details = models.TextField(verbose_name='experimental special details', blank=True, null=True,
                                             default='')

    class Meta:
        ordering = ["-number"]

    def solvents_list(self):
        slist = ''
        for x in [str(self.solvent1), str(self.solvent2), str(self.solvent3)]:
            if x != 'None' and slist:
                slist += ', <wbr>' + x
            if x != 'None' and not slist:
                slist += x
        return slist

    def was_measured_recently(self) -> bool:
        now = timezone.now()
        return now - datetime.timedelta(days=2) <= self.measure_date <= now

    was_measured_recently.admin_order_field = 'measure_date'
    was_measured_recently.boolean = True
    was_measured_recently.short_description = 'Measured recently?'

    def __str__(self):
        return self.experiment

    def save(self, *args, **kwargs):
        """
        Saves all differences between the database items into the cif file.

        # TODO: for cif parser:
          - It should detect if string should be written into ; ; quotes
            _foo_bar_baz
            ;
            I am a multiline string
            with some text.
            ;
          - strings with spaces should be quoted like 'I am a string'
          - set_pair() should accept numbers
        """
        super().save()
        try:
            p = self.push_info_to_cif()
            print(p, '####')
        except Exception as e:
            print('Error during push_info_to_cif() ->', e)
            raise
        if p:
            print('Cif updated sucessfully!')

    def push_info_to_cif(self):
        """
        Writes information from the database into the cif file
        """
        print('----- Pushing values -----')
        try:
            file = self.cif.cif_file_on_disk.path
            print(file, '345#')
            if not file:
                return False
        except AttributeError:
            # There is no cif file for this Experiment:
            print('No cif file...')
            return False
        try:
            doc = gemmi.cif.read_file(file)
        except RuntimeError:
            print('unable to open file')
            return False
        # CifFile Model field names:
        # names = [f.name for f in CifFile._meta.get_fields()]

        # Data from Experiment:
        self.write_cif_item(doc, '_exptl_crystal_size_max', str(getattr(self, 'crystal_size_x')))
        self.write_cif_item(doc, '_exptl_crystal_size_mid', str(getattr(self, 'crystal_size_y')))
        self.write_cif_item(doc, '_exptl_crystal_size_min', str(getattr(self, 'crystal_size_z')))
        self.write_cif_item(doc, '_exptl_crystal_colour', self.get_choice(COLOUR_CHOICES, 'crystal_colour'))
        self.write_cif_item(doc, '_exptl_crystal_colour_mod', self.get_choice(COLOUR_MOD_CHOICES, 'crystal_colour_mod'))
        self.write_cif_item(doc, '_exptl_crystal_colour_lustre',
                            self.get_choice(COLOUR_LUSTRE_COICES, 'crystal_colour_lustre'))
        self.write_cif_item(doc, '_exptl_special_details', self.quote_string(getattr(self, 'exptl_special_details')))
        # TODO: Handle getattr of None:
        self.write_cif_item(doc, '_diffrn_measurement_specimen_support', self.quote_string(getattr(self.base,
                                                                                                   'support')))

        # Data from Cif:
        self.write_cif_item(doc, '_exptl_absorpt_correction_T_min',
                            str(getattr(self.cif, 'exptl_absorpt_correction_T_min')))
        self.write_cif_item(doc, '_exptl_absorpt_correction_T_max',
                            str(getattr(self.cif, 'exptl_absorpt_correction_T_max')))
        self.write_cif_item(doc, '_exptl_crystal_description',
                            self.quote_string(getattr(self.cif, 'exptl_crystal_description')))
        self.write_cif_item(doc, '_cell_measurement_temperature',
                            self.quote_string(getattr(self.cif, 'cell_measurement_temperature')))
        self.write_cif_item(doc, '_cell_measurement_reflns_used',
                            str(getattr(self.cif, 'cell_measurement_reflns_used')))
        self.write_cif_item(doc, '_cell_measurement_theta_min',
                            self.quote_string(getattr(self.cif, 'cell_measurement_theta_min')))

        try:
            doc.write_file(file)
        except Exception as e:
            print('Error during cif write:', e, '##set_cif_item')
            return False
        return True

    def get_choice(self, choices, attibute, na_0=True):
        """
        Get the choice value from a choices field.
        :param choices: The choice dictionary
        :param attibute: the attribute to retrieve from the choice
        :param na_0: Decide wether 0 should be translated to '?' or not.
        :return: Choice value
        """
        value = getattr(self, attibute)
        if na_0:
            if value == 0:
                return '?'
            else:
                return choices[value][1]
        else:
            return choices[value][1]

    def quote_string(self, string):
        """
        Quotes the string value in a way that the line maximum of cif 1.1 with 2048 characters is fulfilled and longer
        strings are embedded into ; quotes.
        :param string: The string to save
        :return: a quoted string
        """
        if isinstance(string, (int, float)):
            print('Warning! You tried to quote a number!')
            return str(string)
        if not string:
            return '?'
        if len(string) < 2047 and (not '\n' in string or not '\r' in string):
            return "'{}'".format(string)
        else:
            return ";{}\n;".format('\n'.join(textwrap.wrap(string, width=2047)))

    def write_cif_item(self, doc, key, value):
        try:
            doc.sole_block().set_pair(key, value)
        except Exception as e:
            pass
            print('Error in write_cif_item() -> set_pair:\n', e)
