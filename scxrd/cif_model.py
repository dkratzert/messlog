from pathlib import Path

from django.db import models
from django.utils import timezone
import os
from scxrd.cif.atoms import sorted_atoms, format_sum_formula
from gemmi import cif as gcif

from scxrd.utils import frac_to_cart, get_float, get_int, get_string
from scxrd.utils import generate_sha256

DEBUG = False


class CifFile(models.Model):
    """
    The database model for a single cif file. The following table rows are filled during file upload
    """
    cif_file_on_disk = models.FileField(upload_to='cifs', null=True, blank=True)
    sha256 = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(verbose_name='upload date', null=True, blank=True)
    date_updated = models.DateTimeField(verbose_name='change date', null=True, blank=True)
    filesize = models.PositiveIntegerField(null=True, blank=True)
    # TODO: Find a better solution:
    # sumform_exact = models.OneToOneField('SumFormula', null=True, blank=True, on_delete=models.DO_NOTHING,
    #                                     related_name='cif_file')
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
    space_group_name_Hall = models.CharField(max_length=255, null=True, blank=True)
    space_group_centring_type = models.CharField(max_length=255, null=True, blank=True)
    space_group_IT_number = models.PositiveIntegerField(null=True, blank=True)
    space_group_crystal_system = models.CharField(max_length=255, null=True, blank=True)
    space_group_symop_operation_xyz = models.TextField(null=True, blank=True)
    audit_creation_method = models.CharField(max_length=255, null=True, blank=True)
    chemical_formula_sum = models.CharField(max_length=255, null=True, blank=True)
    chemical_formula_weight = models.CharField(max_length=255, null=True, blank=True)
    exptl_crystal_description = models.CharField(max_length=255, null=True, blank=True)
    exptl_crystal_colour = models.CharField(max_length=255, null=True, blank=True)
    exptl_crystal_size_max = models.FloatField(null=True, blank=True)
    exptl_crystal_size_mid = models.FloatField(null=True, blank=True)
    exptl_crystal_size_min = models.FloatField(null=True, blank=True)
    exptl_absorpt_coefficient_mu = models.FloatField(null=True, blank=True)
    exptl_absorpt_correction_type = models.CharField(max_length=255, null=True, blank=True)
    diffrn_ambient_temperature = models.FloatField(null=True, blank=True)
    diffrn_radiation_wavelength = models.FloatField(null=True, blank=True)
    diffrn_radiation_type = models.CharField(max_length=255, null=True, blank=True)
    diffrn_source = models.CharField(max_length=255, null=True, blank=True)
    diffrn_measurement_device_type = models.CharField(max_length=255, null=True, blank=True)
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
    refine_ls_abs_structure_Flack = models.CharField(max_length=255, null=True, blank=True)
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
    diffrn_reflns_av_unetI_netI = models.FloatField(null=True, blank=True)
    database_code_depnum_ccdc_archive = models.CharField(max_length=255, null=True, blank=True,
                                                         verbose_name='CCDC number')
    shelx_res_file = models.TextField(null=True, blank=True, max_length=10000000)

    #################################

    def save(self, *args, **kwargs):
        super(CifFile, self).save(*args, **kwargs)
        self.sha256 = generate_sha256(self.cif_file_on_disk.file)
        Atom.objects.filter(cif_id=self.pk).delete()  # delete previous atoms version
        # save cif content to db table:
        self.fill_residuals_table(self.cif_file_on_disk.file.name)
        self.filesize = self.cif_file_on_disk.size
        # TODO: Make check if file exists work:
        # inst = CifFile.objects.filter(sha1=checksum).first()
        # if inst:
        #    self.cif = inst
        #    return
        # https://timonweb.com/posts/cleanup-files-and-images-on-model-delete-in-django/
        if not self.date_created:
            self.date_created = timezone.now()
        self.date_updated = timezone.now()
        super(CifFile, self).save(*args, **kwargs)

    def __str__(self):
        try:
            return os.path.basename(self.cif_file_on_disk.url)
        except ValueError:
            return 'no file'
        # data is the cif _data value
        # return self.data

    def delete(self, *args, **kwargs):
        cf = Path(self.cif_file_on_disk.path)
        if DEBUG:
            print('deleting', cf.name, 'in', cf.absolute())
        cf.unlink()
        super().delete(*args, **kwargs)

    def fill_residuals_table(self, cif_file):
        """
        Fill the table with residuals of the refinement.
        """
        cif_parsed = gcif.read_file(cif_file)
        cif_block = cif_parsed.sole_block()
        fw = cif_block.find_value
        cell = get_float(fw('_cell_length_a')), \
               get_float(fw('_cell_length_b')), \
               get_float(fw('_cell_length_c')), \
               get_float(fw('_cell_angle_alpha')), \
               get_float(fw('_cell_angle_beta')), \
               get_float(fw('_cell_angle_gamma')), \
               get_float(fw('_cell_volume'))
        # TODO: This might be optimized by
        table = cif_block.find(['_atom_site_label',
                                '_atom_site_type_symbol',
                                '_atom_site_fract_x',
                                '_atom_site_fract_y',
                                '_atom_site_fract_z',
                                '_atom_site_occupancy',
                                '_atom_site_disorder_group'])
        for name, element, x, y, z, occ, part in table:
            try:
                xc, yc, zc = frac_to_cart((get_float(x), get_float(y), get_float(z)), cell[:6])
            except (TypeError, ValueError):
                continue
            part = get_int(part)
            self.atoms = Atom(cif=self,
                              name=name,
                              element=element,
                              x=get_float(x), y=get_float(y), z=get_float(z),
                              xc=xc, yc=yc, zc=zc,
                              occupancy=gcif.as_number(occ),
                              part=part if part else 0)
            self.atoms.save()
        self.data = cif_block.name
        self.cell_length_a, self.cell_length_b, self.cell_length_c, self.cell_angle_alpha, \
        self.cell_angle_beta, self.cell_angle_gamma, self.cell_volume = cell
        self.cell_formula_units_Z = get_int(fw("_cell_formula_units_Z"))
        self.space_group_name_H_M_alt = get_string(fw("_space_group_name_H-M_alt"))
        self.space_group_name_Hall = get_string(fw("_space_group_name_Hall"))
        self.space_group_centring_type = get_string(fw("_space_group_centring_type"))
        self.space_group_IT_number = get_int(fw("_space_group_IT_number"))
        self.space_group_crystal_system = get_string(fw("_space_group_crystal_system"))
        self.space_group_symop_operation_xyz = get_string(fw("_space_group_symop_operation_xyz"))
        self.audit_creation_method = get_string(fw("_audit_creation_method"))
        self.chemical_formula_sum = get_string(fw("_chemical_formula_sum"))
        self.chemical_formula_weight = get_string(fw("_chemical_formula_weight"))
        self.exptl_crystal_description = get_string(fw("_exptl_crystal_description"))
        self.exptl_crystal_colour = get_string(fw("_exptl_crystal_colour"))
        self.exptl_crystal_size_max = get_float(fw("_exptl_crystal_size_max"))
        self.exptl_crystal_size_mid = get_float(fw("_exptl_crystal_size_mid"))
        self.exptl_crystal_size_min = get_float(fw("_exptl_crystal_size_min"))
        self.exptl_absorpt_coefficient_mu = get_float(fw("_exptl_absorpt_coefficient_mu"))
        self.exptl_absorpt_correction_type = get_string(fw("_exptl_absorpt_correction_type"))
        self.diffrn_ambient_temperature = get_float(fw("_diffrn_ambient_temperature"))
        self.diffrn_radiation_wavelength = get_float(fw("_diffrn_radiation_wavelength"))
        self.diffrn_radiation_type = get_string(fw("_diffrn_radiation_type"))
        self.diffrn_source = get_string(fw("_diffrn_source"))
        self.diffrn_measurement_device_type = get_string(fw("_diffrn_measurement_device_type"))
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
        self.refine_ls_shift_su_max = get_float(fw("_refine_ls_shift/su_max"))
        self.refine_ls_shift_su_mean = get_float(fw("_refine_ls_shift/su_mean"))
        self.refine_diff_density_max = get_float(fw("_refine_diff_density_max"))
        self.refine_diff_density_min = get_float(fw("_refine_diff_density_min"))
        self.diffrn_reflns_av_unetI_netI = get_float(fw("_diffrn_reflns_av_unetI/netI"))
        self.database_code_depnum_ccdc_archive = get_string(fw("_database_code_depnum_ccdc_archive"))
        self.shelx_res_file = get_string(fw("_shelx_res_file"))

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

    def completeness_in_percent(self):
        if self.diffrn_measured_fraction_theta_max:
            return round(self.diffrn_measured_fraction_theta_max * 100, 1)

    def fill_formula(self, cif):
        """
        Fills formula data into the sum formula table.
        """
        out = []
        formula = cif.cif_data['calculated_formula_sum']
        for x in formula:
            if not x.capitalize() in sorted_atoms:
                out.append(x)
        # Delete non-existing atoms from formula:
        for x in out:
            del formula[x]
        if not formula:
            return
        return SumFormula(cif=self, **formula)


class SumFormula(models.Model):
    cif = models.ForeignKey(CifFile, null=True, blank=True, on_delete=models.CASCADE)
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
    cif = models.ForeignKey(CifFile, null=True, blank=True, on_delete=models.CASCADE)
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

    def __str__(self):
        # print(self.name, self.element, self.x, self.y, self.z, self.occupancy, self.part)
        # "{:4.6s}{:4}{:8.6f}{:8.6f}{:8.6f}{:6.4f}{:4}"
        """if all([self.name, self.element, self.x, self.y, self.z]):
            return "{} {} {:8.6f}{:8.6f}{:8.6f} {} {}".format(self.name, self.element, self.x, self.y, self.z,
                                                              self.occupancy, self.part)"""
        return self.name
