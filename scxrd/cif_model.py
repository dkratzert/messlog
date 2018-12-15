from django.db import models
from django.utils import timezone

from scxrd.cif.atoms import sorted_atoms
from scxrd.cif.cifparser import Cif
from .utils import generate_sha256


def get_float(line: str) -> (int, None):
    try:
        return float(line.split('(')[0].split(' ')[0])
    except ValueError:
        return None


def get_int(line: str) -> (int, None):
    try:
        return int(line.split('(')[0].split(' ')[0])
    except ValueError:
        return None


class CifFile(models.Model):
    """
    The database model for a single cif file. The following table rows are filled during file upload
    """
    cif = models.FileField(upload_to='cifs', null=True, blank=True)
    sha256 = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(verbose_name='upload date', null=True, blank=True)
    date_updated = models.DateTimeField(verbose_name='change date', null=True, blank=True)
    filesize = models.PositiveIntegerField(null=True, blank=True)
    #########################################
    data = models.CharField(null=True, blank=True, max_length=256)
    _cell_length_a = models.FloatField(null=True, blank=True)
    _cell_length_b = models.FloatField(null=True, blank=True)
    _cell_length_c = models.FloatField(null=True, blank=True)
    _cell_angle_alpha = models.FloatField(null=True, blank=True)
    _cell_angle_beta = models.FloatField(null=True, blank=True)
    _cell_angle_gamma = models.FloatField(null=True, blank=True)
    _cell_volume = models.FloatField(null=True, blank=True)
    _cell_formula_units_Z = models.PositiveIntegerField(null=True, blank=True)
    _space_group_name_H_M_alt = models.CharField(max_length=255, null=True, blank=True)
    _space_group_name_Hall = models.CharField(max_length=255, null=True, blank=True)
    _space_group_centring_type = models.CharField(max_length=255, null=True, blank=True)
    _space_group_IT_number = models.PositiveIntegerField(null=True, blank=True)
    _space_group_crystal_system = models.CharField(max_length=255, null=True, blank=True)
    _space_group_symop_operation_xyz = models.TextField(null=True, blank=True)
    _audit_creation_method = models.CharField(max_length=255, null=True, blank=True)
    _chemical_formula_sum = models.CharField(max_length=255, null=True, blank=True)
    _chemical_formula_weight = models.CharField(max_length=255, null=True, blank=True)
    _exptl_crystal_description = models.CharField(max_length=255, null=True, blank=True)
    _exptl_crystal_colour = models.CharField(max_length=255, null=True, blank=True)
    _exptl_crystal_size_max = models.FloatField(null=True, blank=True)
    _exptl_crystal_size_mid = models.FloatField(null=True, blank=True)
    _exptl_crystal_size_min = models.FloatField(null=True, blank=True)
    _exptl_absorpt_coefficient_mu = models.FloatField(null=True, blank=True)
    _exptl_absorpt_correction_type = models.CharField(max_length=255, null=True, blank=True)
    _diffrn_ambient_temperature = models.FloatField(null=True, blank=True)
    _diffrn_radiation_wavelength = models.FloatField(null=True, blank=True)
    _diffrn_radiation_type = models.CharField(max_length=255, null=True, blank=True)
    _diffrn_source = models.CharField(max_length=255, null=True, blank=True)
    _diffrn_measurement_device_type = models.CharField(max_length=255, null=True, blank=True)
    _diffrn_reflns_number = models.IntegerField(null=True, blank=True)
    _diffrn_reflns_av_R_equivalents = models.PositiveIntegerField(null=True, blank=True)
    _diffrn_reflns_theta_min = models.FloatField(null=True, blank=True)
    _diffrn_reflns_theta_max = models.FloatField(null=True, blank=True)
    _diffrn_reflns_theta_full = models.FloatField(null=True, blank=True)
    _diffrn_measured_fraction_theta_max = models.FloatField(null=True, blank=True)
    _diffrn_measured_fraction_theta_full = models.FloatField(null=True, blank=True)
    _reflns_number_total = models.PositiveIntegerField(null=True, blank=True)
    _reflns_number_gt = models.PositiveIntegerField(null=True, blank=True)
    _reflns_threshold_expression = models.CharField(max_length=255, null=True, blank=True)
    _reflns_Friedel_coverage = models.FloatField(null=True, blank=True)
    _computing_structure_solution = models.CharField(max_length=255, null=True, blank=True)
    _computing_structure_refinement = models.CharField(max_length=255, null=True, blank=True)
    _refine_special_details = models.TextField(null=True, blank=True)
    _refine_ls_abs_structure_Flack = models.CharField(max_length=255, null=True, blank=True)
    _refine_ls_structure_factor_coef = models.CharField(max_length=255, null=True, blank=True)
    _refine_ls_weighting_details = models.TextField(null=True, blank=True)
    _refine_ls_number_reflns = models.PositiveIntegerField(null=True, blank=True)
    _refine_ls_number_parameters = models.PositiveIntegerField(null=True, blank=True)
    _refine_ls_number_restraints = models.PositiveIntegerField(null=True, blank=True)
    _refine_ls_R_factor_all = models.FloatField(null=True, blank=True)
    _refine_ls_R_factor_gt = models.FloatField(null=True, blank=True)
    _refine_ls_wR_factor_ref = models.FloatField(null=True, blank=True)
    _refine_ls_wR_factor_gt = models.FloatField(null=True, blank=True)
    _refine_ls_goodness_of_fit_ref = models.FloatField(null=True, blank=True)
    _refine_ls_restrained_S_all = models.FloatField(null=True, blank=True)
    _refine_ls_shift_su_max = models.FloatField(null=True, blank=True)
    _refine_ls_shift_su_mean = models.FloatField(null=True, blank=True)
    _refine_diff_density_max = models.FloatField(null=True, blank=True)
    _refine_diff_density_min = models.FloatField(null=True, blank=True)
    _diffrn_reflns_av_unetI_netI = models.FloatField(null=True, blank=True)
    _database_code_depnum_ccdc_archive = models.CharField(max_length=255, null=True, blank=True)
    _shelx_res_file = models.TextField(null=True, blank=True)

    #################################

    def save(self, *args, **kwargs):
        super(CifFile, self).save(*args, **kwargs)
        checksum = generate_sha256(self.cif.file)
        self.sha256 = checksum
        with open(self.cif.file.name, encoding='ascii', errors='ignore') as cf:
            self.fill_residuals_table(cf.readlines())
        self.filesize = self.cif.size
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
        print(checksum)

    def __str__(self):
        return self.cif.url

    def delete(self, *args, **kwargs):
        self.cif.delete()
        super().delete(*args, **kwargs)

    def fill_residuals_table(self, ciflist):
        """
        Fill the table with residuals of the refinement.
        """
        cif = Cif()
        cifok = cif.parsefile(ciflist)
        if cifok:
            print('file parsed')
        else:
            return None
        print(cif.cif_data['calculated_formula_sum'])
        if cif.cif_data['calculated_formula_sum']:
            self.fill_formula(cif.cif_data['calculated_formula_sum'])
        self.data = cif.cif_data["data"]
        self._cell_length_a = get_float(cif.cif_data["_cell_length_a"])
        self._cell_length_b = get_float(cif.cif_data['_cell_length_b'])
        self._cell_length_c = get_float(cif.cif_data['_cell_length_c'])
        self._cell_angle_alpha = get_float(cif.cif_data['_cell_angle_alpha'])
        self._cell_angle_beta = get_float(cif.cif_data['_cell_angle_beta'])
        self._cell_angle_gamma = get_float(cif.cif_data['_cell_angle_gamma'])
        self._cell_volume = get_float(cif.cif_data["_cell_volume"])
        self._cell_formula_units_Z = get_int(cif.cif_data["_cell_formula_units_Z"])
        self._space_group_name_H_M_alt = cif.cif_data["_space_group_name_H-M_alt"]
        self._space_group_name_Hall = cif.cif_data["_space_group_name_Hall"]
        self._space_group_centring_type = cif.cif_data["_space_group_centring_type"]
        self._space_group_IT_number = get_int(cif.cif_data["_space_group_IT_number"])
        self._space_group_crystal_system = cif.cif_data["_space_group_crystal_system"]
        self._space_group_symop_operation_xyz = cif.cif_data["_space_group_symop_operation_xyz"]
        self._audit_creation_method = cif.cif_data["_audit_creation_method"]
        self._chemical_formula_sum = cif.cif_data["_chemical_formula_sum"]
        self._chemical_formula_weight = cif.cif_data["_chemical_formula_weight"]
        self._exptl_crystal_description = cif.cif_data["_exptl_crystal_description"]
        self._exptl_crystal_colour = cif.cif_data["_exptl_crystal_colour"]
        self._exptl_crystal_size_max = get_float(cif.cif_data["_exptl_crystal_size_max"])
        self._exptl_crystal_size_mid = get_float(cif.cif_data["_exptl_crystal_size_mid"])
        self._exptl_crystal_size_min = get_float(cif.cif_data["_exptl_crystal_size_min"])
        self._exptl_absorpt_coefficient_mu = get_float(cif.cif_data["_exptl_absorpt_coefficient_mu"])
        self._exptl_absorpt_correction_type = cif.cif_data["_exptl_absorpt_correction_type"]
        self._diffrn_ambient_temperature = get_float(cif.cif_data["_diffrn_ambient_temperature"])
        self._diffrn_radiation_wavelength = get_float(cif.cif_data["_diffrn_radiation_wavelength"])
        self._diffrn_radiation_type = cif.cif_data["_diffrn_radiation_type"]
        self._diffrn_source = cif.cif_data["_diffrn_source"]
        self._diffrn_measurement_device_type = cif.cif_data["_diffrn_measurement_device_type"]
        self._diffrn_reflns_number = get_int(cif.cif_data["_diffrn_reflns_number"])
        self._diffrn_reflns_av_R_equivalents = get_int(cif.cif_data["_diffrn_reflns_av_R_equivalents"])
        self._diffrn_reflns_theta_min = get_float(cif.cif_data["_diffrn_reflns_theta_min"])
        self._diffrn_reflns_theta_max = get_float(cif.cif_data["_diffrn_reflns_theta_max"])
        self._diffrn_reflns_theta_full = get_float(cif.cif_data["_diffrn_reflns_theta_full"])
        self._diffrn_measured_fraction_theta_max = get_float(cif.cif_data["_diffrn_measured_fraction_theta_max"])
        self._diffrn_measured_fraction_theta_full = get_float(cif.cif_data["_diffrn_measured_fraction_theta_full"])
        self._reflns_number_total = get_int(cif.cif_data["_reflns_number_total"])
        self._reflns_number_gt = get_int(cif.cif_data["_reflns_number_gt"])
        self._reflns_threshold_expression = cif.cif_data["_reflns_threshold_expression"]
        self._reflns_Friedel_coverage = get_float(cif.cif_data["_reflns_Friedel_coverage"])
        self._computing_structure_solution = cif.cif_data["_computing_structure_solution"]
        self._computing_structure_refinement = cif.cif_data["_computing_structure_refinement"]
        self._refine_special_details = cif.cif_data["_refine_special_details"]
        self._refine_ls_abs_structure_Flack = cif.cif_data["_refine_ls_abs_structure_Flack"]
        self._refine_ls_structure_factor_coef = cif.cif_data["_refine_ls_structure_factor_coef"]
        self._refine_ls_weighting_details = cif.cif_data["_refine_ls_weighting_details"]
        self._refine_ls_number_reflns = get_int(cif.cif_data["_refine_ls_number_reflns"])
        self._refine_ls_number_parameters = get_int(cif.cif_data["_refine_ls_number_parameters"])
        self._refine_ls_number_restraints = get_int(cif.cif_data["_refine_ls_number_restraints"])
        self._refine_ls_R_factor_all = get_float(cif.cif_data["_refine_ls_R_factor_all"])
        self._refine_ls_R_factor_gt = get_float(cif.cif_data["_refine_ls_R_factor_gt"])
        self._refine_ls_wR_factor_ref = get_float(cif.cif_data["_refine_ls_wR_factor_ref"])
        self._refine_ls_wR_factor_gt = get_float(cif.cif_data["_refine_ls_wR_factor_gt"])
        self._refine_ls_goodness_of_fit_ref = get_float(cif.cif_data["_refine_ls_goodness_of_fit_ref"])
        self._refine_ls_restrained_S_all = get_float(cif.cif_data["_refine_ls_restrained_S_all"])
        self._refine_ls_shift_su_max = get_float(cif.cif_data["_refine_ls_shift/su_max"])
        self._refine_ls_shift_su_mean = get_float(cif.cif_data["_refine_ls_shift/su_mean"])
        self._refine_diff_density_max = get_float(cif.cif_data["_refine_diff_density_max"])
        self._refine_diff_density_min = get_float(cif.cif_data["_refine_diff_density_min"])
        self._diffrn_reflns_av_unetI_netI = get_float(cif.cif_data["_diffrn_reflns_av_unetI/netI"])
        self._database_code_depnum_ccdc_archive = cif.cif_data["_database_code_depnum_ccdc_archive"]
        self._shelx_res_file = cif.cif_data["_shelx_res_file"]

    @staticmethod
    def fill_formula(formula: dict):
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
        sum = sumFormula(**formula)
        sum.save()


class sumFormula(models.Model):
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




