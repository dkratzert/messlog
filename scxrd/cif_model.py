import os
from pathlib import Path
from typing import List

import gemmi
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from gemmi import cif as gcif

from scxrd.cif.atoms import sorted_atoms, format_sum_formula
from scxrd.utils import frac_to_cart, get_float, get_int, get_string, vol_unitcell
from scxrd.utils import generate_sha256

DEBUG = True


def validate_cif_file_extension(value):
    if not value.name.endswith('.cif'):
        raise ValidationError(_('Only .cif files are allowed to upload here.'))


class CifFileModel(models.Model):
    """
    The database model for a single cif file. The following table rows are filled during file upload
    """
    cif_file_on_disk = models.FileField(upload_to='cifs', null=True, blank=True,
                                        validators=[validate_cif_file_extension],
                                        verbose_name='cif file')
    sha256 = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(verbose_name='upload date', null=True, blank=True)
    date_updated = models.DateTimeField(verbose_name='change date', null=True, blank=True)
    filesize = models.PositiveIntegerField(null=True, blank=True)
    # This is the sum formula calculated from the atoms in the cif file:
    sumform_calc = models.OneToOneField('SumFormula', null=True, blank=True, on_delete=models.DO_NOTHING,
                                        related_name='cif_file')
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
    cell_measurement_temperature = models.CharField(max_length=255, null=True, blank=True)
    cell_measurement_reflns_used = models.PositiveIntegerField(null=True, blank=True)
    cell_measurement_theta_min = models.CharField(max_length=255, null=True, blank=True)
    cell_measurement_theta_max = models.CharField(max_length=255, null=True, blank=True)
    space_group_name_H_M_alt = models.CharField(max_length=255, null=True, blank=True)
    space_group_name_Hall = models.CharField(max_length=255, null=True, blank=True)
    space_group_centring_type = models.CharField(max_length=255, null=True, blank=True)
    space_group_IT_number = models.PositiveIntegerField(null=True, blank=True)
    space_group_crystal_system = models.CharField(max_length=255, null=True, blank=True)
    space_group_symop_operation_xyz = models.TextField(null=True, blank=True)
    audit_creation_method = models.CharField(max_length=2048, null=True, blank=True)
    # This is the sum formula directly from the cif key/value:
    chemical_formula_sum = models.CharField(max_length=2048, null=True, blank=True)
    chemical_formula_weight = models.CharField(max_length=255, null=True, blank=True)
    exptl_crystal_description = models.CharField(max_length=2048, null=True, blank=True)
    exptl_crystal_colour = models.CharField(max_length=255, null=True, blank=True)
    exptl_crystal_size_max = models.FloatField(null=True, blank=True)
    exptl_crystal_size_mid = models.FloatField(null=True, blank=True)
    exptl_crystal_size_min = models.FloatField(null=True, blank=True)
    exptl_absorpt_coefficient_mu = models.FloatField(null=True, blank=True)
    exptl_absorpt_correction_type = models.CharField(max_length=255, null=True, blank=True)
    diffrn_ambient_temperature = models.FloatField(null=True, blank=True)
    diffrn_radiation_wavelength = models.FloatField(null=True, blank=True)
    diffrn_radiation_type = models.CharField(max_length=255, null=True, blank=True)
    diffrn_source = models.CharField(max_length=2048, null=True, blank=True)
    diffrn_measurement_device = models.CharField(max_length=2048, null=True, blank=True)
    diffrn_measurement_device_type = models.CharField(max_length=2048, null=True, blank=True)
    diffrn_reflns_number = models.IntegerField(null=True, blank=True)
    diffrn_reflns_av_R_equivalents = models.FloatField(null=True, blank=True)
    diffrn_reflns_theta_min = models.FloatField(null=True, blank=True)
    diffrn_reflns_theta_max = models.FloatField(null=True, blank=True)
    diffrn_reflns_theta_full = models.FloatField(null=True, blank=True)
    diffrn_measured_fraction_theta_max = models.FloatField(null=True, blank=True)
    diffrn_measured_fraction_theta_full = models.FloatField(null=True, blank=True)
    reflns_number_total = models.PositiveIntegerField(null=True, blank=True)
    reflns_number_gt = models.PositiveIntegerField(null=True, blank=True)
    reflns_threshold_expression = models.CharField(max_length=255, null=True, blank=True)
    reflns_Friedel_coverage = models.FloatField(null=True, blank=True)
    computing_structure_solution = models.CharField(max_length=255, null=True, blank=True)
    computing_structure_refinement = models.CharField(max_length=255, null=True, blank=True)
    refine_special_details = models.TextField(null=True, blank=True)
    # has to be a charfield, because of the error value:
    refine_ls_abs_structure_Flack = models.CharField(null=True, blank=True, max_length=255)
    refine_ls_structure_factor_coef = models.CharField(max_length=255, null=True, blank=True)
    refine_ls_weighting_details = models.TextField(null=True, blank=True)
    refine_ls_number_reflns = models.PositiveIntegerField(null=True, blank=True)
    refine_ls_number_parameters = models.PositiveIntegerField(null=True, blank=True)
    refine_ls_number_restraints = models.PositiveIntegerField(null=True, blank=True)
    refine_ls_R_factor_all = models.FloatField(null=True, blank=True)
    refine_ls_R_factor_gt = models.FloatField(null=True, blank=True)
    refine_ls_wR_factor_ref = models.FloatField(null=True, blank=True)
    refine_ls_wR_factor_gt = models.FloatField(null=True, blank=True)
    refine_ls_goodness_of_fit_ref = models.FloatField(null=True, blank=True)
    refine_ls_restrained_S_all = models.FloatField(null=True, blank=True)
    refine_ls_shift_su_max = models.FloatField(null=True, blank=True)
    refine_ls_shift_su_mean = models.FloatField(null=True, blank=True)
    refine_diff_density_max = models.FloatField(null=True, blank=True)
    refine_diff_density_min = models.FloatField(null=True, blank=True)
    refine_diff_density_rms = models.FloatField(null=True, blank=True)
    diffrn_reflns_av_unetI_netI = models.FloatField(null=True, blank=True)
    database_code_depnum_ccdc_archive = models.CharField(max_length=255, null=True, blank=True,
                                                         verbose_name='CCDC number')
    shelx_res_file = models.TextField(null=True, blank=True, max_length=10000000)
    shelx_res_checksum = models.PositiveIntegerField(null=True, blank=True)

    # shelx_hkl_file = models.TextField(null=True, blank=True)
    # shelx_hkl_checksum = models.IntegerField(null=True, blank=True)

    reflns_Friedel_fraction_full = models.FloatField(null=True, blank=True)
    refine_ls_abs_structure_details = models.FloatField(null=True, blank=True)
    reflns_special_details = models.FloatField(null=True, blank=True)
    computing_data_collection = models.CharField(null=True, blank=True, max_length=2048)
    computing_cell_refinement = models.CharField(null=True, blank=True, max_length=2048)
    computing_data_reduction = models.CharField(null=True, blank=True, max_length=2048)
    computing_molecular_graphics = models.CharField(null=True, blank=True, max_length=2048)
    computing_publication_material = models.CharField(null=True, blank=True, max_length=2048)
    atom_sites_solution_primary = models.CharField(null=True, blank=True, max_length=2048)
    atom_sites_solution_secondary = models.CharField(null=True, blank=True, max_length=2048)
    atom_sites_solution_hydrogens = models.CharField(null=True, blank=True, max_length=2048)
    refine_ls_hydrogen_treatment = models.CharField(null=True, blank=True, max_length=255)
    refine_ls_extinction_method = models.CharField(null=True, blank=True, max_length=2048)
    refine_ls_extinction_coef = models.FloatField(null=True, blank=True)
    refine_ls_extinction_expression = models.CharField(null=True, blank=True, max_length=2048)
    geom_special_details = models.TextField(null=True, blank=True, max_length=2048)
    shelx_estimated_absorpt_T_min = models.FloatField(null=True, blank=True)
    shelx_estimated_absorpt_T_max = models.FloatField(null=True, blank=True)
    exptl_absorpt_correction_T_min = models.FloatField(null=True, blank=True)
    exptl_absorpt_correction_T_max = models.FloatField(null=True, blank=True)
    exptl_absorpt_process_details = models.CharField(null=True, blank=True, max_length=2048)
    exptl_absorpt_special_details = models.CharField(null=True, blank=True, max_length=2048)
    diffrn_radiation_monochromator = models.CharField(null=True, blank=True, max_length=2048)
    diffrn_measurement_method = models.CharField(null=True, blank=True, max_length=2048)
    diffrn_radiation_probe = models.CharField(null=True, blank=True, max_length=2048)
    diffrn_measurement_details = models.CharField(null=True, blank=True, max_length=2048)
    diffrn_detector = models.CharField(null=True, blank=True, max_length=2048)
    diffrn_detector_type = models.CharField(null=True, blank=True, max_length=2048)
    diffrn_detector_area_resol_mean = models.FloatField(null=True, blank=True)
    diffrn_measurement_specimen_support = models.CharField(null=True, blank=True, max_length=2048)
    diffrn_reflns_limit_h_max = models.IntegerField(null=True, blank=True)
    diffrn_reflns_limit_h_min = models.IntegerField(null=True, blank=True)
    diffrn_reflns_limit_k_max = models.IntegerField(null=True, blank=True)
    diffrn_reflns_limit_k_min = models.IntegerField(null=True, blank=True)
    diffrn_reflns_limit_l_max = models.IntegerField(null=True, blank=True)
    diffrn_reflns_limit_l_min = models.IntegerField(null=True, blank=True)
    diffrn_reflns_Laue_measured_fraction_full = models.FloatField(null=True, blank=True)
    diffrn_reflns_Laue_measured_fraction_max = models.FloatField(null=True, blank=True)
    exptl_crystal_density_meas = models.FloatField(null=True, blank=True)
    exptl_crystal_density_method = models.CharField(null=True, blank=True, max_length=2048)
    exptl_crystal_density_diffrn = models.FloatField(null=True, blank=True)
    exptl_crystal_F_000 = models.FloatField(null=True, blank=True)
    exptl_transmission_factor_min = models.FloatField(null=True, blank=True)
    exptl_transmission_factor_max = models.FloatField(null=True, blank=True)
    exptl_crystal_face_x = models.TextField(null=True, blank=True)

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

    def add_to_sumform(self, occ=None, atype=None):
        #  0     1   2 3 4   5  6  7   8       9
        # [Name type x y z  xc xc zc occupancy part]
        atom_type_symbol = ''
        try:
            if occ:
                occu = occ
            else:
                occu = 1.0
            if atype:
                atom_type_symbol = atype
            else:
                assert KeyError
            elem = atom_type_symbol.capitalize()
            if elem in self.sum_form_dict:
                self.sum_form_dict[elem] += occu
            else:
                self.sum_form_dict[elem] = occu
        except KeyError:
            pass

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
        self.sum_form_dict = {}
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
            self.add_to_sumform(occ=occ, atype=element)
            self.atoms.save()
        if self.sum_form_dict:
            self.sumform_from_atoms = self.fill_formula(self.sum_form_dict)
            # safes the SumFormula instanse into the respectiva table:
            self.sumform_from_atoms.save()

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
        self.diffrn_measured_fraction_theta_full = get_float(fw("_diffrn_measured_fraction_theta_full"))
        self.reflns_number_total = get_int(fw("_reflns_number_total"))
        self.reflns_number_gt = get_int(fw("_reflns_number_gt"))
        self.reflns_threshold_expression = get_string(fw("_reflns_threshold_expression"))
        self.reflns_Friedel_coverage = get_float(fw("_reflns_Friedel_coverage"))
        self.computing_structure_solution = get_string(fw("_computing_structure_solution"))
        self.computing_structure_refinement = get_string(fw("_computing_structure_refinement"))
        self.refine_special_details = get_string(fw("_refine_special_details"))
        self.refine_ls_abs_structure_Flack = get_string(fw("_refine_ls_abs_structure_Flack"))
        self.refine_ls_structure_factor_coef = get_string(fw("_refine_ls_structure_factor_coef"))
        self.refine_ls_weighting_details = get_string(fw("_refine_ls_weighting_details"))
        self.refine_ls_number_reflns = get_int(fw("_refine_ls_number_reflns"))
        self.refine_ls_number_parameters = get_int(fw("_refine_ls_number_parameters"))
        self.refine_ls_number_restraints = get_int(fw("_refine_ls_number_restraints"))
        self.refine_ls_R_factor_all = get_float(fw("_refine_ls_R_factor_all"))
        self.refine_ls_R_factor_gt = get_float(fw("_refine_ls_R_factor_gt"))
        self.refine_ls_wR_factor_ref = get_float(fw("_refine_ls_wR_factor_ref"))
        self.refine_ls_wR_factor_gt = get_float(fw("_refine_ls_wR_factor_gt"))
        self.refine_ls_goodness_of_fit_ref = get_float(fw("_refine_ls_goodness_of_fit_ref"))
        self.refine_ls_restrained_S_all = get_float(fw("_refine_ls_restrained_S_all"))
        if fw("_refine_ls_shift/esd_max"):
            self.refine_ls_shift_su_max = get_float(fw("_refine_ls_shift/esd_max"))
        else:
            self.refine_ls_shift_su_max = get_float(fw("_refine_ls_shift/su_max"))
        if fw('_refine_ls_shift/esd_mean'):
            self.refine_ls_shift_su_mean = get_float(fw("_refine_ls_shift/esd_mean"))
        else:
            self.refine_ls_shift_su_mean = get_float(fw("_refine_ls_shift/su_mean"))
        self.refine_diff_density_max = get_float(fw("_refine_diff_density_max"))
        self.refine_diff_density_min = get_float(fw("_refine_diff_density_min"))
        self.refine_diff_density_rms = get_float(fw('_refine_diff_density_rms'))
        if fw('_diffrn_reflns_av_sigmaI/netI'):
            self.diffrn_reflns_av_unetI_netI = get_float(fw("_diffrn_reflns_av_unetI/netI"))
        else:
            self.diffrn_reflns_av_unetI_netI = get_float(fw("_diffrn_reflns_av_unetI/netI"))
        self.database_code_depnum_ccdc_archive = get_string(fw("_database_code_depnum_ccdc_archive"))
        self.reflns_Friedel_fraction_full = get_float(fw('_reflns_Friedel_fraction_full'))
        self.reflns_Friedel_fraction_max = get_float(fw('_reflns_Friedel_fraction_max'))
        self.refine_ls_abs_structure_details = get_float(fw('_refine_ls_abs_structure_details'))
        self.reflns_special_details = get_float(fw('_reflns_special_details'))
        self.computing_data_collection = get_string(fw('_computing_data_collection'))
        self.computing_cell_refinement = get_string(fw('_computing_cell_refinement'))
        self.computing_data_reduction = get_string(fw('_computing_data_reduction'))
        self.computing_molecular_graphics = get_string(fw('_computing_molecular_graphics'))
        self.computing_publication_material = get_string(fw('_computing_publication_material'))
        self.atom_sites_solution_primary = get_string(fw('_atom_sites_solution_primary'))
        self.atom_sites_solution_secondary = get_string(fw('_atom_sites_solution_secondary'))
        self.atom_sites_solution_hydrogens = get_string(fw('_atom_sites_solution_hydrogens'))
        self.refine_ls_hydrogen_treatment = get_string(fw('_refine_ls_hydrogen_treatment'))
        self.refine_ls_extinction_method = get_string(fw('_refine_ls_extinction_method'))
        self.refine_ls_extinction_coef = get_float(fw('_refine_ls_extinction_coef'))
        self.refine_ls_extinction_expression = get_string(fw('_refine_ls_extinction_expression'))
        self.geom_special_details = get_string(fw('_geom_special_details'))
        self.diffrn_radiation_monochromator = get_string(fw('_diffrn_radiation_monochromator'))
        self.diffrn_measurement_method = get_string(fw('_diffrn_measurement_method'))
        self.shelx_estimated_absorpt_T_min = get_float(fw('_shelx_estimated_absorpt_T_min'))
        self.shelx_estimated_absorpt_T_max = get_float(fw('_shelx_estimated_absorpt_T_max'))
        self.exptl_absorpt_correction_T_min = get_float(fw('_exptl_absorpt_correction_T_min'))
        self.exptl_absorpt_correction_T_max = get_float(fw('_exptl_absorpt_correction_T_max'))
        self.exptl_absorpt_process_details = get_string(fw('_exptl_absorpt_process_details'))
        self.exptl_absorpt_special_details = get_string(fw('_exptl_absorpt_special_details'))
        self.diffrn_radiation_probe = get_string(fw('_diffrn_radiation_probe'))
        self.diffrn_measurement_details = get_string(fw('_diffrn_measurement_details'))
        self.diffrn_detector = get_string(fw('_diffrn_detector'))
        self.diffrn_detector_type = get_string(fw('_diffrn_detector_type'))
        self.diffrn_detector_area_resol_mean = get_float(fw('_diffrn_detector_area_resol_mean'))
        self.diffrn_reflns_limit_h_max = get_int(fw('_diffrn_reflns_limit_h_max'))
        self.diffrn_reflns_limit_h_min = get_int(fw('_diffrn_reflns_limit_h_min'))
        self.diffrn_reflns_limit_k_max = get_int(fw('_diffrn_reflns_limit_k_max'))
        self.diffrn_reflns_limit_k_min = get_int(fw('_diffrn_reflns_limit_k_min'))
        self.diffrn_reflns_limit_l_max = get_int(fw('_diffrn_reflns_limit_l_max'))
        self.diffrn_reflns_limit_l_min = get_int(fw('_diffrn_reflns_limit_l_min'))
        self.diffrn_reflns_Laue_measured_fraction_full = get_float(fw('_diffrn_reflns_Laue_measured_fraction_full'))
        self.diffrn_reflns_Laue_measured_fraction_max = get_float(fw('_diffrn_reflns_Laue_measured_fraction_max'))
        self.exptl_crystal_density_meas = get_float(fw('_exptl_crystal_density_meas'))
        self.exptl_crystal_density_method = get_string(fw('_exptl_crystal_density_method'))
        self.exptl_crystal_density_diffrn = get_float(fw('_exptl_crystal_density_diffrn'))
        self.exptl_crystal_F_000 = get_float(fw('_exptl_crystal_F_000'))
        self.exptl_transmission_factor_min = get_float(fw('_exptl_transmission_factor_min'))
        self.exptl_transmission_factor_max = get_float(fw('_exptl_transmission_factor_max'))
        # loop:
        self.exptl_crystal_face_x = '\n'.join([i.str(0) for i in cif_block.find(
            ("_exptl_crystal_face_index_h",
             '_exptl_crystal_face_index_k',
             '_exptl_crystal_face_index_l',
             '_exptl_crystal_face_perp_dist'
             ))])

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
    def fill_formula(formula):
        """
        Fills formula data into the sum formula table.
        """
        out = []
        for x in formula:
            if not x.capitalize() in sorted_atoms:
                out.append(x)
        # Delete non-existing atoms from formula:
        for x in out:
            del formula[x]
        if not formula:
            return
        return SumFormula(**formula)

    @staticmethod
    def get_cif_item(file: str, item: str) -> List[str]:
        """
        "testfiles/p21c.cif"
        """
        doc = gemmi.cif.read_file(file)
        pair = doc.sole_block().find_pair(item)
        return pair

    # probably move this into a view?
    # @login_required
    @staticmethod
    def set_cif_item(file: str, pair: List[str]) -> bool:
        """
        sets a new cif item value and writes the file
        """
        doc = gemmi.cif.read_file(file)
        doc.sole_block().set_pair(*pair)
        try:
            doc.write_file(file)
        except Exception as e:
            print('Error during cif write:', e, '##set_cif_item')
            return False
        return True


class SumFormula(models.Model):
    # Is a OneToOne field in CifFile now:
    # cif = models.ForeignKey(CifFile, null=True, blank=True, on_delete=models.CASCADE, related_name='sumform')
    C = models.FloatField(default=0)
    D = models.FloatField(default=0)
    H = models.FloatField(default=0)
    N = models.FloatField(default=0)
    O = models.FloatField(default=0)
    Cl = models.FloatField(default=0)
    Br = models.FloatField(default=0)
    I = models.FloatField(default=0)
    F = models.FloatField(default=0)
    S = models.FloatField(default=0)
    P = models.FloatField(default=0)
    Ac = models.FloatField(default=0)
    Ag = models.FloatField(default=0)
    Al = models.FloatField(default=0)
    Am = models.FloatField(default=0)
    Ar = models.FloatField(default=0)
    As = models.FloatField(default=0)
    At = models.FloatField(default=0)
    Au = models.FloatField(default=0)
    B = models.FloatField(default=0)
    Ba = models.FloatField(default=0)
    Be = models.FloatField(default=0)
    Bi = models.FloatField(default=0)
    Bk = models.FloatField(default=0)
    Ca = models.FloatField(default=0)
    Cd = models.FloatField(default=0)
    Ce = models.FloatField(default=0)
    Cf = models.FloatField(default=0)
    Cm = models.FloatField(default=0)
    Co = models.FloatField(default=0)
    Cr = models.FloatField(default=0)
    Cs = models.FloatField(default=0)
    Cu = models.FloatField(default=0)
    Dy = models.FloatField(default=0)
    Er = models.FloatField(default=0)
    Eu = models.FloatField(default=0)
    Fe = models.FloatField(default=0)
    Fr = models.FloatField(default=0)
    Ga = models.FloatField(default=0)
    Gd = models.FloatField(default=0)
    Ge = models.FloatField(default=0)
    He = models.FloatField(default=0)
    Hf = models.FloatField(default=0)
    Hg = models.FloatField(default=0)
    Ho = models.FloatField(default=0)
    In = models.FloatField(default=0)
    Ir = models.FloatField(default=0)
    K = models.FloatField(default=0)
    Kr = models.FloatField(default=0)
    La = models.FloatField(default=0)
    Li = models.FloatField(default=0)
    Lu = models.FloatField(default=0)
    Mg = models.FloatField(default=0)
    Mn = models.FloatField(default=0)
    Mo = models.FloatField(default=0)
    Na = models.FloatField(default=0)
    Nb = models.FloatField(default=0)
    Nd = models.FloatField(default=0)
    Ne = models.FloatField(default=0)
    Ni = models.FloatField(default=0)
    Np = models.FloatField(default=0)
    Os = models.FloatField(default=0)
    Pa = models.FloatField(default=0)
    Pb = models.FloatField(default=0)
    Pd = models.FloatField(default=0)
    Pm = models.FloatField(default=0)
    Po = models.FloatField(default=0)
    Pr = models.FloatField(default=0)
    Pt = models.FloatField(default=0)
    Pu = models.FloatField(default=0)
    Ra = models.FloatField(default=0)
    Rb = models.FloatField(default=0)
    Re = models.FloatField(default=0)
    Rh = models.FloatField(default=0)
    Rn = models.FloatField(default=0)
    Ru = models.FloatField(default=0)
    Sb = models.FloatField(default=0)
    Sc = models.FloatField(default=0)
    Se = models.FloatField(default=0)
    Si = models.FloatField(default=0)
    Sm = models.FloatField(default=0)
    Sn = models.FloatField(default=0)
    Sr = models.FloatField(default=0)
    Ta = models.FloatField(default=0)
    Tb = models.FloatField(default=0)
    Tc = models.FloatField(default=0)
    Te = models.FloatField(default=0)
    Th = models.FloatField(default=0)
    Ti = models.FloatField(default=0)
    Tl = models.FloatField(default=0)
    Tm = models.FloatField(default=0)
    U = models.FloatField(default=0)
    V = models.FloatField(default=0)
    W = models.FloatField(default=0)
    Xe = models.FloatField(default=0)
    Y = models.FloatField(default=0)
    Yb = models.FloatField(default=0)
    Zn = models.FloatField(default=0)
    Zr = models.FloatField(default=0)

    def __str__(self):
        """
        Returns a html formated sum formula.
        """
        atomsdict = {key: getattr(self, key) for key in sorted_atoms}
        return format_sum_formula(atomsdict)


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
