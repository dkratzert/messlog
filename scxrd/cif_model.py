import textwrap
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from scxrd.cif.cif_file_io import CifContainer
from scxrd.utils import get_float

DEBUG = False


def validate_cif_file_extension(value):
    error = ValidationError(_('Only .cif files are allowed to upload here.'))
    if not isinstance(value.name, str):
        raise error
    if not value.name.lower().endswith('.cif'):
        raise error


class CifFileModel(models.Model):
    """
    The database model for a single cif file. The following table rows are filled during file upload
    wR2, R1, Space group, symmcards, atoms, cell, sumformula, completeness, Goof, temperature, Z, Rint, Peak/hole
    """
    experiment = models.OneToOneField(to='Experiment', on_delete=models.CASCADE, verbose_name='cif file data',
                                      related_name='ciffilemodel')
    sha256 = models.CharField(max_length=256, blank=True)
    date_created = models.DateTimeField(verbose_name=_('upload date'), null=True, blank=True)
    date_updated = models.DateTimeField(verbose_name=_('change date'), null=True, blank=True)
    filesize = models.PositiveIntegerField(null=True, blank=True)
    #########################################
    data = models.CharField(blank=True, max_length=256)
    cell_length_a = models.FloatField(null=True, blank=True)
    cell_length_b = models.FloatField(null=True, blank=True)
    cell_length_c = models.FloatField(null=True, blank=True)
    cell_angle_alpha = models.FloatField(null=True, blank=True)
    cell_angle_beta = models.FloatField(null=True, blank=True)
    cell_angle_gamma = models.FloatField(null=True, blank=True)
    cell_volume = models.FloatField(null=True, blank=True)
    cell_formula_units_Z = models.PositiveIntegerField(null=True, blank=True)
    space_group_name_H_M_alt = models.CharField(max_length=255, blank=True)
    space_group_IT_number = models.PositiveIntegerField(null=True, blank=True)
    space_group_crystal_system = models.CharField(max_length=255, blank=True)
    space_group_symop_operation_xyz = models.TextField(null=True, blank=True)
    # This is the sum formula directly from the cif key/value:
    chemical_formula_sum = models.CharField(max_length=2048, blank=True)
    diffrn_radiation_wavelength = models.FloatField(null=True, blank=True)
    diffrn_radiation_type = models.CharField(max_length=255, blank=True)
    diffrn_reflns_av_R_equivalents = models.FloatField(null=True, blank=True)
    diffrn_reflns_theta_min = models.FloatField(null=True, blank=True)
    diffrn_reflns_theta_max = models.FloatField(null=True, blank=True)
    diffrn_measured_fraction_theta_max = models.FloatField(null=True, blank=True)
    refine_ls_abs_structure_Flack = models.CharField(blank=True, max_length=255)
    refine_ls_R_factor_gt = models.FloatField(null=True, blank=True)
    refine_ls_wR_factor_ref = models.FloatField(null=True, blank=True)
    refine_ls_goodness_of_fit_ref = models.FloatField(null=True, blank=True)
    refine_diff_density_max = models.FloatField(null=True, blank=True)
    refine_diff_density_min = models.FloatField(null=True, blank=True)
    diffrn_reflns_av_unetI_netI = models.FloatField(null=True, blank=True)
    ccdc_number = models.CharField(max_length=255, blank=True, verbose_name=_('CCDC number'))
    cif_file_on_disk = models.FileField(upload_to='cifs', null=True, blank=True,
                                        validators=[validate_cif_file_extension],
                                        verbose_name='cif file')

    def __str__(self):
        try:
            return self.cif_file_on_disk.name
        except ValueError:
            return '# no file found #'
        # data is the cif data_ value

    def fill_residuals_table(self, cif: CifContainer):
        """
        Fill the table with residuals of the refinement.
        """
        self.data = cif.block.name
        self.cell_length_a, self.cell_length_b, self.cell_length_c, \
        self.cell_angle_alpha, self.cell_angle_beta, self.cell_angle_gamma, self.cell_volume = cif.cell
        self.cell_formula_units_Z = cif["_cell_formula_units_Z"] if cif["_cell_formula_units_Z"] else 99
        self.space_group_name_H_M_alt = cif.space_group
        self.space_group_name_Hall = cif["_space_group_name_Hall"]
        self.space_group_IT_number = cif.spgr_number_from_symmops
        self.space_group_crystal_system = cif.crystal_system
        self.space_group_symop_operation_xyz = cif.symmops
        self.shelx_res_file = cif.resdata
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
        self.ccdc_number = cif["_database_code_depnum_ccdc_archive"]

    def wr2_in_percent(self):
        if self.refine_ls_R_factor_gt:
            return round(self.refine_ls_R_factor_gt * 100, 1)
        else:
            return ''

    def r1_in_percent(self):
        if self.refine_ls_wR_factor_ref:
            return round(self.refine_ls_wR_factor_ref * 100, 1)
        else:
            return ''

    def rint_in_percent(self):
        if self.diffrn_reflns_av_R_equivalents:
            return round(self.diffrn_reflns_av_R_equivalents * 100, 1)
        else:
            return ''

    def completeness_in_percent(self) -> float:
        if self.diffrn_measured_fraction_theta_max:
            return round(self.diffrn_measured_fraction_theta_max * 100, 1)

    def temperature(self):
        if not self.cif_file_on_disk:
            return ''
        return CifContainer(self.cif_file_path)['_diffrn_ambient_temperature']

    @property
    def cif_file_path(self) -> Path:
        """The complete absolute path of the CIF file with file name and ending"""
        return Path(str(self.cif_file_on_disk.file))

    @property
    def cif_name_only(self) -> str:
        """The CIF file name without path"""
        return self.cif_file_path.name

    def cif_exists(self):
        """Check if the CIF exists"""
        if self.cif_file_path.exists():
            return True
        return False

    @staticmethod
    def quote_string(string):
        """
        Quotes the string value in a way that the line maximum of cif 1.1 with 2048 characters is fulfilled and longer
        strings are embedded into ; quotes.
        :param string: The string to save
        :return: a quoted string
        """
        if not string:
            return '?'
        if isinstance(string, (int, float)):
            return str(string)
        if not isinstance(string, (str)):
            # To get the string representation of model instances first:
            string = str(string)
        if len(string) < 2047 and (not '\n' in string or not '\r' in string):
            return "'{}'".format(string)
        else:
            return ";{}\n;".format('\n'.join(textwrap.wrap(string, width=2047)))
