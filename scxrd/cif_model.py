from django.db import models
from django.utils import timezone
from scxrd.cif.cifparser import Cif
from .utils import generate_sha256


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
    _cell_formula_units_Z = models.PositiveIntegerField(null=True, blank=True)
    _space_group_name_H_M_alt = models.CharField(max_length=255, null=True, blank=True)
    _space_group_name_Hall = models.CharField(max_length=255, null=True, blank=True)
    _space_group_centring_type = models.CharField(max_length=255, null=True, blank=True)
    _space_group_IT_number = models.PositiveIntegerField(null=True, blank=True)
    _space_group_crystal_system = models.CharField(max_length=255, null=True, blank=True)
    _space_group_symop_operation_xyz = models.TextField(max_length=255, null=True, blank=True)
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
    _diffrn_ambient_temperature  = models.FloatField(null=True, blank=True)
    _diffrn_radiation_wavelength  = models.FloatField(null=True, blank=True)
    _diffrn_radiation_type  = models.CharField(max_length=255, null=True, blank=True)
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
    _computing_structure_solution  = models.CharField(max_length=255, null=True, blank=True)
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
    _shelx_res_file = models.TextField(max_length=255, null=True, blank=True)
    #################################

    def save(self, *args, **kwargs):
        super(CifFile, self).save(*args, **kwargs)
        with open(self.cif.file.name, encoding='ascii', errors='ignore') as cf:
            self.fill_residuals_table(cf.readlines())
        checksum = generate_sha256(self.cif.file)
        self.filesize = self.cif.size
        # TODO: Make check if file exists work:
        #inst = CifFile.objects.filter(sha1=checksum).first()
        #if inst:
        #    self.cif = inst
        #    return
        self.sha1 = checksum
        if not self.id:
            self.date_created = timezone.now()
        self.date_updated = timezone.now()
        super(CifFile, self).save(*args, **kwargs)

    def __str__(self):
        return self.cif.url

    def delete(self, *args, **kwargs):
        self.cif.delete()
        super().delete(*args, **kwargs)

    def __getitem__(self, item):
        return self.item

    def __setitem__(self, key, value):
        self.key = value

    def fill_residuals_table(self, fullpath):
        """
        Fill the table with residuals of the refinement.
        """
        #if cif.cif_data['calculated_formula_sum']:
        #    self.fill_formula(structure_id, cif.cif_data['calculated_formula_sum'])
        cif = Cif()
        cifok = cif.parsefile(fullpath)
        print('file parsed')

        cif_keys = [
                        "data",
                        "_cell_length_a",
                        '_cell_length_b',
                        '_cell_length_c',
                        '_cell_angle_alpha',
                        '_cell_angle_beta'
                        '_cell_angle_gamma'
                        "_cell_volume"
                        "_cell_formula_units_Z",
                        "_space_group_name_H-M_alt",
                        "_space_group_name_Hall",
                        "_space_group_centring_type",
                        "_space_group_IT_number",
                        "_space_group_crystal_system",
                        "_space_group_symop_operation_xyz",
                        "_audit_creation_method",
                        "_chemical_formula_sum",
                        "_chemical_formula_weight",
                        "_exptl_crystal_description",
                        "_exptl_crystal_colour",
                        "_exptl_crystal_size_max",
                        "_exptl_crystal_size_mid",
                        "_exptl_crystal_size_min",
                        "_exptl_absorpt_coefficient_mu",
                        "_exptl_absorpt_correction_type",
                        "_diffrn_ambient_temperature",
                        "_diffrn_radiation_wavelength",
                        "_diffrn_radiation_type",
                        "_diffrn_source",
                        "_diffrn_measurement_device_type",
                        "_diffrn_reflns_number",
                        "_diffrn_reflns_av_R_equivalents",
                        "_diffrn_reflns_av_unetI/netI",
                        "_diffrn_reflns_theta_min",
                        "_diffrn_reflns_theta_max",
                        "_diffrn_reflns_theta_full",
                        "_diffrn_measured_fraction_theta_max",
                        "_diffrn_measured_fraction_theta_full",
                        "_reflns_number_total",
                        "_reflns_number_gt",
                        "_reflns_threshold_expression",
                        "_reflns_Friedel_coverage",
                        "_computing_structure_solution",
                        "_computing_structure_refinement",
                        "_refine_special_details",
                        "_refine_ls_abs_structure_Flack",
                        "_refine_ls_structure_factor_coef",
                        "_refine_ls_weighting_details",
                        "_refine_ls_number_reflns",
                        "_refine_ls_number_parameters",
                        "_refine_ls_number_restraints",
                        "_refine_ls_R_factor_all",
                        "_refine_ls_R_factor_gt",
                        "_refine_ls_wR_factor_ref",
                        "_refine_ls_wR_factor_gt",
                        "_refine_ls_goodness_of_fit_ref",
                        "_refine_ls_restrained_S_all",
                        "_refine_ls_shift/su_max",
                        "_refine_ls_shift/su_mean",
                        "_refine_diff_density_max",
                        "_refine_diff_density_min",
                        "_diffrn_reflns_av_unetI_netI",
                        "_database_code_depnum_ccdc_archive",
                        "_shelx_res_file",
                    ]
        db_columns = [
                    self._cell_formula_units_Z,                 
                    self._space_group_name_H_M_alt,             
                    self._space_group_name_Hall,                
                    self._space_group_centring_type,            
                    self._space_group_IT_number,                
                    self._space_group_crystal_system,           
                    self._space_group_symop_operation_xyz,      
                    self._chemical_formula_sum,                 
                    self._chemical_formula_weight,              
                    self._exptl_crystal_description,            
                    self._exptl_crystal_colour,                 
                    self._exptl_crystal_size_max,               
                    self._exptl_crystal_size_mid,               
                    self._exptl_crystal_size_min,               
                    self._audit_creation_method,                
                    self._exptl_absorpt_coefficient_mu,         
                    self._exptl_absorpt_correction_type,        
                    self._diffrn_ambient_temperature,           
                    self._diffrn_radiation_wavelength,          
                    self._diffrn_radiation_type,                
                    self._diffrn_source,                        
                    self._diffrn_measurement_device_type,       
                    self._diffrn_reflns_number,                 
                    self._diffrn_reflns_av_R_equivalents,       
                    self._diffrn_reflns_theta_min,              
                    self._diffrn_reflns_theta_max,              
                    self._diffrn_reflns_theta_full,             
                    self._diffrn_measured_fraction_theta_max,   
                    self._diffrn_measured_fraction_theta_full,  
                    self._reflns_number_total,                  
                    self._reflns_number_gt,                                                                            
                    self._reflns_threshold_expression,          
                    self._reflns_Friedel_coverage,                          
                    self._computing_structure_solution,         
                    self._computing_structure_refinement,       
                    self._refine_special_details,               
                    self._refine_ls_abs_structure_Flack,        
                    self._refine_ls_structure_factor_coef,      
                    self._refine_ls_weighting_details,          
                    self._refine_ls_number_reflns,              
                    self._refine_ls_number_parameters,          
                    self._refine_ls_number_restraints,          
                    self._refine_ls_R_factor_all,               
                    self._refine_ls_R_factor_gt,                
                    self._refine_ls_wR_factor_ref,              
                    self._refine_ls_wR_factor_gt,               
                    self._refine_ls_goodness_of_fit_ref,        
                    self._refine_ls_restrained_S_all,                                  
                    self._refine_ls_shift_su_max,                                   
                    self._refine_ls_shift_su_mean,              
                    self._refine_diff_density_max,              
                    self._refine_diff_density_min,              
                    self._diffrn_reflns_av_unetI_netI,          
                    self._database_code_depnum_ccdc_archive,    
                    self._shelx_res_file,                       
                    ]
        for key, column in zip(cif_keys, db_columns):
            try:
                self.column = cif.cif_data[key]
            except Exception as e:
                print(e)
            
            





