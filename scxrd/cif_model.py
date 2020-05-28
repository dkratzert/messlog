import os
from pathlib import Path
from typing import List

import gemmi
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import FileField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mysite.settings import MEDIA_ROOT
from scxrd.cif.cif_file_io import CifContainer
from scxrd.utils import generate_sha256
from scxrd.utils import get_float

DEBUG = True


def validate_cif_file_extension(value):
    if not value.name.endswith('.cif'):
        raise ValidationError(_('Only .cif files are allowed to upload here.'))


class CifFileModel(models.Model):
    """
    The database model for a single cif file. The following table rows are filled during file upload
    wR2, R1, Space group, symmcards, atoms, cell, sumformula, completeness, Goof, temperature, Z, Rint, Peak/hole
    """
    cif_file_on_disk = FileField(upload_to='cifs', null=True, blank=True,
                                   validators=[validate_cif_file_extension],
                                   verbose_name='cif file')
    sha256 = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(verbose_name='upload date', null=True, blank=True)
    date_updated = models.DateTimeField(verbose_name='change date', null=True, blank=True)
    filesize = models.PositiveIntegerField(null=True, blank=True)
    #########################################
    data = models.CharField(null=True, blank=True, max_length=256)
    cell_length_a = models.FloatField(null=True, blank=True)
    cell_length_b = models.FloatField(null=True, blank=True)
    cell_length_c = models.FloatField(null=True, blank=True)
    cell_angle_alpha = models.FloatField(null=True, blank=True)
    cell_angle_beta = models.FloatField(null=True, blank=True)
    cell_angle_gamma = models.FloatField(null=True, blank=True)
    cell_volume = models.FloatField(null=True, blank=True)
    cell_formula_units_Z = models.PositiveIntegerField(null=True, blank=True)
    space_group_name_H_M_alt = models.CharField(max_length=255, null=True, blank=True)
    space_group_IT_number = models.PositiveIntegerField(null=True, blank=True)
    space_group_crystal_system = models.CharField(max_length=255, null=True, blank=True)
    space_group_symop_operation_xyz = models.TextField(null=True, blank=True)
    # This is the sum formula directly from the cif key/value:
    chemical_formula_sum = models.CharField(max_length=2048, null=True, blank=True)
    diffrn_radiation_wavelength = models.FloatField(null=True, blank=True)
    diffrn_radiation_type = models.CharField(max_length=255, null=True, blank=True)
    diffrn_reflns_av_R_equivalents = models.FloatField(null=True, blank=True)
    diffrn_reflns_theta_min = models.FloatField(null=True, blank=True)
    diffrn_reflns_theta_max = models.FloatField(null=True, blank=True)
    diffrn_measured_fraction_theta_max = models.FloatField(null=True, blank=True)
    refine_ls_abs_structure_Flack = models.CharField(null=True, blank=True, max_length=255)
    refine_ls_R_factor_gt = models.FloatField(null=True, blank=True)
    refine_ls_wR_factor_ref = models.FloatField(null=True, blank=True)
    refine_ls_goodness_of_fit_ref = models.FloatField(null=True, blank=True)
    refine_diff_density_max = models.FloatField(null=True, blank=True)
    refine_diff_density_min = models.FloatField(null=True, blank=True)
    diffrn_reflns_av_unetI_netI = models.FloatField(null=True, blank=True)
    database_code_depnum_ccdc_archive = models.CharField(max_length=255, null=True, blank=True,
                                                         verbose_name='CCDC number')

    def save(self, *args, **kwargs):
        #super(CifFileModel, self).save(*args, **kwargs)
        print(str(self.cif_file_on_disk.chunks()))
        try:
            cif = CifContainer(chunks = self.cif_file_on_disk.chunks())
        except Exception as e:
            print(e)
            print('Unable to parse cif file:', self.cif_file_on_disk.file.name)
            # raise ValidationError('Unable to parse cif file:', e)
            return False
        # Atom.objects.filter(cif_id=self.pk).delete()  # delete previous atoms version
        # save cif content to db table:
        try:
            # self.cif_file_on_disk.file.name
            self.fill_residuals_table(cif)
        except RuntimeError as e:
            print('Error while saving cif file:', e)
            return False
        self.sha256 = generate_sha256(self.cif_file_on_disk)
        self.filesize = self.cif_file_on_disk.size
        if not self.date_created:
            self.date_created = timezone.now()
        self.date_updated = timezone.now()
        super(CifFileModel, self).save(*args, **kwargs)
        # Do not do this:
        #print('Duplicates:', self.duplicates)
        #for d in self.duplicates:
        #    d.delete()

    def find_duplicates(self):
        return [i for i in CifFileModel.objects.exclude(pk=self.pk).filter(sha256=self.sha256)]

    @property
    def duplicates(self):
        return self.find_duplicates()

    def __str__(self):
        try:
            return os.path.basename(self.cif_file_on_disk.url)
        except ValueError:
            return '# no file found #'
        # data is the cif _data value
        # return self.data

    @property
    def exists(self):
        if Path(self.cif_file_on_disk.path).exists():
            return True
        return False

    def delete(self, *args, **kwargs):
        if not self.exists:
            return 
        cf = Path(self.cif_file_on_disk.path)
        #if DEBUG:
        print('deleting', cf.name, 'in', cf.absolute())
        cf.unlink()
        super().delete(*args, **kwargs)

    def fill_residuals_table(self, cif: CifContainer):
        """
        Fill the table with residuals of the refinement.

        >>> cell = gemmi.UnitCell(25.14, 39.50, 45.07, 90, 90, 90)
        >>> cell
        <gemmi.UnitCell(25.14, 39.5, 45.07, 90, 90, 90)>
        >>> cell.fractionalize(gemmi.Position(10, 10, 10))
        <gemmi.Fractional(0.397772, 0.253165, 0.221877)>
        >>> cell.orthogonalize(gemmi.Fractional(0.5, 0.5, 0.5))
        <gemmi.Position(12.57, 19.75, 22.535)>
        """
        # with transaction.atomic():
        #    for at_orth, at_frac in zip(cif.atoms_orth, cif.atoms_fract):
        #        self.atoms = Atom(cif=self, name=at_orth['name'], element=at_orth['symbol'],
        #                          x=at_frac['x'], y=at_frac['y'], z=at_frac['z'],
        #                          xc=at_orth['x'], yc=at_orth['y'], zc=at_orth['z'],
        #                          occupancy=at_orth['occ'], part=at_orth['part'], asym=True)
        #        self.atoms.save()
        self.data = cif.block.name
        self.cell_length_a, self.cell_length_b, self.cell_length_c, \
        self.cell_angle_alpha, self.cell_angle_beta, self.cell_angle_gamma, self.cell_volume = cif.cell
        self.cell_formula_units_Z = cif["_cell_formula_units_Z"] if cif["_cell_formula_units_Z"] else 99
        self.space_group_name_H_M_alt = cif["_space_group_name_H-M_alt"]
        self.space_group_name_Hall = cif["_space_group_name_Hall"]
        self.space_group_IT_number = cif.spgr_number_from_symmops
        self.space_group_crystal_system = cif["_space_group_crystal_system"]
        self.space_group_symop_operation_xyz = cif["_space_group_symop_operation_xyz"]
        self.shelx_res_file = cif["_shelx_res_file"]
        self.shelx_res_checksum = cif['_shelx_res_checksum']
        # self.shelx_hkl_file = cif['_shelx_hkl_file']
        # self.shelx_hkl_checksum = cif['_shelx_hkl_checksum']
        self.chemical_formula_sum = cif["_chemical_formula_sum"]
        self.diffrn_radiation_wavelength = cif["_diffrn_radiation_wavelength"] if cif[
            "_diffrn_radiation_wavelength"] else 0
        self.diffrn_radiation_type = cif["_diffrn_radiation_type"]
        self.diffrn_reflns_av_R_equivalents = get_float(cif["_diffrn_reflns_av_R_equivalents"])
        self.diffrn_reflns_theta_min = get_float(cif["_diffrn_reflns_theta_min"])
        self.diffrn_reflns_theta_max = get_float(cif["_diffrn_reflns_theta_max"])
        self.diffrn_measured_fraction_theta_max = get_float(cif["_diffrn_measured_fraction_theta_max"])
        self.refine_ls_abs_structure_Flack = cif["_refine_ls_abs_structure_Flack"]
        self.refine_ls_R_factor_gt = get_float(cif["_refine_ls_R_factor_gt"])
        self.refine_ls_wR_factor_ref = get_float(cif["_refine_ls_wR_factor_ref"])
        self.refine_ls_goodness_of_fit_ref = get_float(cif["_refine_ls_goodness_of_fit_ref"])
        self.refine_diff_density_max = get_float(cif["_refine_diff_density_max"])
        self.refine_diff_density_min = get_float(cif["_refine_diff_density_min"])
        self.diffrn_reflns_av_unetI_netI = get_float(cif["_diffrn_reflns_av_unetI/netI"])
        self.database_code_depnum_ccdc_archive = cif["_database_code_depnum_ccdc_archive"]

    def wr2_in_percent(self):
        if self.refine_ls_wR_factor_ref:
            return round(self.refine_ls_wR_factor_ref * 100, 1)
        else:
            return '---'

    def rint_in_percent(self):
        if self.diffrn_reflns_av_R_equivalents:
            return round(self.diffrn_reflns_av_R_equivalents * 100, 1)
        else:
            return '---'

    def completeness_in_percent(self) -> float:
        if self.diffrn_measured_fraction_theta_max:
            return round(self.diffrn_measured_fraction_theta_max * 100, 1)

    def get_cif_instance(self) -> CifContainer:
        cif = CifContainer(Path(MEDIA_ROOT).joinpath(self.cif_file_on_disk.name))
        return cif

    @staticmethod
    def get_cif_item(file: str, item: str) -> List[str]:
        """
        "testfiles/p21c.cif"
        """
        doc = gemmi.cif.read_file(file)
        pair = doc.sole_block().find_pair(item)
        return pair

    def get_cif_model(self):
        """Reads the current cif file from tzhe model"""
        filepth = Path(MEDIA_ROOT).joinpath(self.cif_file_on_disk.name)
        print('loadinf cif:', filepth)
        cif = CifContainer(filepth)
        return cif


'''
class Atom(models.Model):
    """
    This table holds the atoms of a cif file.
    """
    cif = models.ForeignKey(CifFileModel, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    # Element as element symbol:
    element = models.CharField(max_length=2)
    # Fractional coordinates:
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    # Cartesian coordinates:
    xc = models.FloatField(default=0)
    yc = models.FloatField(default=0)
    zc = models.FloatField(default=0)
    occupancy = models.FloatField()
    part = models.IntegerField()
    # incicates wether the atom belongs to the asymmetric unit:
    asym = models.BooleanField(default=False)

    def __str__(self):
        """
        return "{} {} {:8.6f}{:8.6f}{:8.6f} {} {}".format(self.name, self.element, self.x, self.y, self.z,
                                                              self.occupancy, self.part)
        """
        return self.name
'''
