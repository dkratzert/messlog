import os
from pathlib import Path
from typing import List

import gemmi
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from gemmi import cif as gcif

from scxrd.utils import frac_to_cart, get_float, get_int, get_string, vol_unitcell
from scxrd.utils import generate_sha256

DEBUG = True


def validate_cif_file_extension(value):
    if not value.name.endswith('.cif'):
        raise ValidationError(_('Only .cif files are allowed to upload here.'))


class CifFileModel(models.Model):
    """
    The database model for a single cif file. The following table rows are filled during file upload
    wR2, R1, Space group, symmcards, atoms, cell, sumformula, completeness, Goof, temperature, Z, Rint, Peak/hole
    """
    cif_file_on_disk = models.FileField(upload_to='cifs', null=True, blank=True,
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

    # shelx_res_file = models.TextField(null=True, blank=True, max_length=10000000)
    # shelx_res_checksum = models.PositiveIntegerField(null=True, blank=True)
    # shelx_hkl_file = models.TextField(null=True, blank=True)
    # shelx_hkl_checksum = models.IntegerField(null=True, blank=True)

    #################################

    def save(self, *args, **kwargs):
        super(CifFileModel, self).save(*args, **kwargs)
        try:
            cif_parsed = gcif.read_file(self.cif_file_on_disk.file.name)
            cif_block = cif_parsed.sole_block()
        except Exception as e:
            print(e)
            print('Unable to parse cif file:', self.cif_file_on_disk.file.name)
            # raise ValidationError('Unable to parse cif file:', e)
            return False
        Atom.objects.filter(cif_id=self.pk).delete()  # delete previous atoms version
        # save cif content to db table:
        try:
            # self.cif_file_on_disk.file.name
            self.fill_residuals_table(cif_block)
        except RuntimeError as e:
            print('Error while saving cif file:', e)
            return False
        self.sha256 = generate_sha256(self.cif_file_on_disk)
        self.filesize = self.cif_file_on_disk.size
        if not self.date_created:
            self.date_created = timezone.now()
        self.date_updated = timezone.now()
        super(CifFileModel, self).save(*args, **kwargs)

    def __str__(self):
        try:
            return os.path.basename(self.cif_file_on_disk.url)
        except ValueError:
            return 'no file'
        # data is the cif _data value
        # return self.data

    @property
    def exists(self):
        if Path(self.cif_file_on_disk.path).exists():
            return True
        return False

    def delete(self, *args, **kwargs):
        cf = Path(self.cif_file_on_disk.path)
        if DEBUG:
            print('deleting', cf.name, 'in', cf.absolute())
        cf.unlink()
        super().delete(*args, **kwargs)

    def fill_residuals_table(self, cif_block):
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
        fw = cif_block.find_value
        cell = get_float(fw('_cell_length_a')), \
               get_float(fw('_cell_length_b')), \
               get_float(fw('_cell_length_c')), \
               get_float(fw('_cell_angle_alpha')), \
               get_float(fw('_cell_angle_beta')), \
               get_float(fw('_cell_angle_gamma')), \
               get_float(fw('_cell_volume'))
        table = cif_block.find(['_atom_site_label',
                                '_atom_site_type_symbol',
                                '_atom_site_fract_x',
                                '_atom_site_fract_y',
                                '_atom_site_fract_z',
                                '_atom_site_occupancy',
                                '_atom_site_disorder_group'])
        for name, element, x, y, z, occ, part in table:
            x, y, z = (get_float(x), get_float(y), get_float(z))
            try:
                xc, yc, zc = frac_to_cart((x, y, z), cell[:6])
            except (TypeError, ValueError) as e:
                print("Error while calculating cart. coords:", e)
                continue
            part = get_int(part)
            occ = get_float(occ)
            self.atoms = Atom(cif=self, name=name, element=element,
                              x=x, y=y, z=z,
                              xc=xc, yc=yc, zc=zc,
                              occupancy=occ, part=part if part else 0)
            self.atoms.save()
        self.data = cif_block.name
        self.cell_length_a, self.cell_length_b, self.cell_length_c, \
        self.cell_angle_alpha, self.cell_angle_beta, self.cell_angle_gamma, self.cell_volume = cell
        if not self.cell_volume and all(cell[:6]):
            self.cell_volume = vol_unitcell(*cell[:6])
        self.cell_formula_units_Z = get_int(fw("_cell_formula_units_Z"))
        if fw("_symmetry_space_group_name_H-M"):
            self.space_group_name_H_M_alt = get_string(fw("_symmetry_space_group_name_H-M"))
        else:
            self.space_group_name_H_M_alt = get_string(fw("_space_group_name_H-M_alt"))
        if fw('_symmetry_space_group_name_Hall'):
            self.space_group_name_Hall = get_string(fw("_symmetry_space_group_name_Hall"))
        else:
            self.space_group_name_Hall = get_string(fw("_space_group_name_Hall"))
        self.space_group_centring_type = get_string(fw("_space_group_centring_type"))
        if not self.space_group_centring_type:
            if fw("_space_group_name_H-M_alt"):
                self.space_group_centring_type = get_string(fw("_space_group_name_H-M_alt")).split()[0][:1]
            elif fw('_space_group_name_Hall'):
                self.space_group_centring_type = get_string(fw("_space_group_name_Hall")).split()[0][:1]
        if fw('_symmetry_Int_Tables_number'):
            self.space_group_IT_number = get_int(fw("_symmetry_Int_Tables_number"))
        else:
            self.space_group_IT_number = get_int(fw("_space_group_IT_number"))
        self.space_group_crystal_system = get_string(fw("_space_group_crystal_system"))
        # loop
        xyz1 = cif_block.find(("_symmetry_equiv_pos_as_xyz",))  # deprecated
        xyz2 = cif_block.find(("_space_group_symop_operation_xyz",))  # New definition
        if xyz1:
            self.space_group_symop_operation_xyz = '\n'.join([i.str(0) for i in xyz1])
        else:
            self.space_group_symop_operation_xyz = '\n'.join([i.str(0) for i in xyz2])
        self.shelx_res_file = get_string(fw("_shelx_res_file"))
        self.shelx_res_checksum = get_int(fw('_shelx_res_checksum'))

        # self.shelx_hkl_file = get_string(fw('_shelx_hkl_file'))
        # self.shelx_hkl_checksum = get_int(fw('_shelx_hkl_checksum'))

        self.cell_measurement_temperature = get_string(fw('_cell_measurement_temperature'))
        self.cell_measurement_reflns_used = get_int(fw('_cell_measurement_reflns_used'))
        self.cell_measurement_theta_min = get_string(fw('_cell_measurement_theta_min'))
        self.cell_measurement_theta_max = get_string(fw('_cell_measurement_theta_max'))
        self.audit_creation_method = get_string(fw("_audit_creation_method"))
        self.chemical_formula_sum = get_string(fw("_chemical_formula_sum"))
        self.chemical_formula_weight = get_string(fw("_chemical_formula_weight"))
        self.exptl_crystal_description = get_string(fw("_exptl_crystal_description"))
        self.exptl_crystal_colour = get_string(fw("_exptl_crystal_colour"))
        self.exptl_crystal_size_max = get_float(fw("_exptl_crystal_size_max"))
        self.exptl_crystal_size_mid = get_float(fw("_exptl_crystal_size_mid"))
        self.exptl_crystal_size_min = get_float(fw("_exptl_crystal_size_min"))
        self.diffrn_radiation_wavelength = get_float(fw("_diffrn_radiation_wavelength"))
        self.diffrn_ambient_temperature = get_float(fw("_diffrn_ambient_temperature"))
        self.diffrn_radiation_type = get_string(fw("_diffrn_radiation_type"))
        self.diffrn_source = get_string(fw("_diffrn_source"))
        self.exptl_absorpt_coefficient_mu = get_float(fw("_exptl_absorpt_coefficient_mu"))
        self.exptl_absorpt_correction_type = get_string(fw("_exptl_absorpt_correction_type"))
        self.diffrn_measurement_device = get_string(fw("_diffrn_measurement_device"))
        self.diffrn_measurement_device_type = get_string(fw("_diffrn_measurement_device_type"))
        self.diffrn_measurement_specimen_support = get_string(fw("_diffrn_measurement_specimen_support"))
        self.diffrn_reflns_number = get_int(fw("_diffrn_reflns_number"))
        self.diffrn_reflns_av_R_equivalents = get_float(fw("_diffrn_reflns_av_R_equivalents"))
        self.diffrn_reflns_theta_min = get_float(fw("_diffrn_reflns_theta_min"))
        self.diffrn_reflns_theta_max = get_float(fw("_diffrn_reflns_theta_max"))
        self.diffrn_reflns_theta_full = get_float(fw("_diffrn_reflns_theta_full"))
        self.diffrn_measured_fraction_theta_max = get_float(fw("_diffrn_measured_fraction_theta_max"))
        self.refine_ls_abs_structure_Flack = get_string(fw("_refine_ls_abs_structure_Flack"))

        self.refine_ls_R_factor_gt = get_float(fw("_refine_ls_R_factor_gt"))
        self.refine_ls_wR_factor_ref = get_float(fw("_refine_ls_wR_factor_ref"))

        self.refine_ls_goodness_of_fit_ref = get_float(fw("_refine_ls_goodness_of_fit_ref"))
        self.refine_diff_density_max = get_float(fw("_refine_diff_density_max"))
        self.refine_diff_density_min = get_float(fw("_refine_diff_density_min"))
        if fw('_diffrn_reflns_av_sigmaI/netI'):
            self.diffrn_reflns_av_unetI_netI = get_float(fw("_diffrn_reflns_av_unetI/netI"))
        else:
            self.diffrn_reflns_av_unetI_netI = get_float(fw("_diffrn_reflns_av_unetI/netI"))
        self.database_code_depnum_ccdc_archive = get_string(fw("_database_code_depnum_ccdc_archive"))

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

    @staticmethod
    def get_cif_item(file: str, item: str) -> List[str]:
        """
        "testfiles/p21c.cif"
        """
        doc = gemmi.cif.read_file(file)
        pair = doc.sole_block().find_pair(item)
        return pair


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
