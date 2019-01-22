# Generated by Django 2.1.5 on 2019-01-22 16:46

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import scxrd.cif_model
import scxrd.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Atom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('element', models.CharField(max_length=2)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
                ('xc', models.FloatField(default=0)),
                ('yc', models.FloatField(default=0)),
                ('zc', models.FloatField(default=0)),
                ('occupancy', models.FloatField()),
                ('part', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CifFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cif_file_on_disk', models.FileField(blank=True, null=True, upload_to='cifs', validators=[scxrd.cif_model.validate_file_extension], verbose_name='cif file name')),
                ('sha256', models.CharField(blank=True, max_length=256, null=True)),
                ('date_created', models.DateTimeField(blank=True, null=True, verbose_name='upload date')),
                ('date_updated', models.DateTimeField(blank=True, null=True, verbose_name='change date')),
                ('filesize', models.PositiveIntegerField(blank=True, null=True)),
                ('data', models.CharField(blank=True, max_length=256, null=True)),
                ('cell_length_a', models.FloatField(blank=True, null=True)),
                ('cell_length_b', models.FloatField(blank=True, null=True)),
                ('cell_length_c', models.FloatField(blank=True, null=True)),
                ('cell_angle_alpha', models.FloatField(blank=True, null=True)),
                ('cell_angle_beta', models.FloatField(blank=True, null=True)),
                ('cell_angle_gamma', models.FloatField(blank=True, null=True)),
                ('cell_volume', models.FloatField(blank=True, null=True)),
                ('cell_formula_units_Z', models.PositiveIntegerField(blank=True, null=True)),
                ('space_group_name_H_M_alt', models.CharField(blank=True, max_length=255, null=True)),
                ('space_group_name_Hall', models.CharField(blank=True, max_length=255, null=True)),
                ('space_group_centring_type', models.CharField(blank=True, max_length=255, null=True)),
                ('space_group_IT_number', models.PositiveIntegerField(blank=True, null=True)),
                ('space_group_crystal_system', models.CharField(blank=True, max_length=255, null=True)),
                ('space_group_symop_operation_xyz', models.TextField(blank=True, null=True)),
                ('audit_creation_method', models.CharField(blank=True, max_length=2048, null=True)),
                ('chemical_formula_sum', models.CharField(blank=True, max_length=2048, null=True)),
                ('chemical_formula_weight', models.CharField(blank=True, max_length=255, null=True)),
                ('exptl_crystal_description', models.CharField(blank=True, max_length=2048, null=True)),
                ('exptl_crystal_colour', models.CharField(blank=True, max_length=255, null=True)),
                ('exptl_crystal_size_max', models.FloatField(blank=True, null=True)),
                ('exptl_crystal_size_mid', models.FloatField(blank=True, null=True)),
                ('exptl_crystal_size_min', models.FloatField(blank=True, null=True)),
                ('exptl_absorpt_coefficient_mu', models.FloatField(blank=True, null=True)),
                ('exptl_absorpt_correction_type', models.CharField(blank=True, max_length=255, null=True)),
                ('diffrn_ambient_temperature', models.FloatField(blank=True, null=True)),
                ('diffrn_radiation_wavelength', models.FloatField(blank=True, null=True)),
                ('diffrn_radiation_type', models.CharField(blank=True, max_length=255, null=True)),
                ('diffrn_source', models.CharField(blank=True, max_length=2048, null=True)),
                ('diffrn_measurement_device_type', models.CharField(blank=True, max_length=2048, null=True)),
                ('diffrn_reflns_number', models.IntegerField(blank=True, null=True)),
                ('diffrn_reflns_av_R_equivalents', models.FloatField(blank=True, null=True)),
                ('diffrn_reflns_theta_min', models.FloatField(blank=True, null=True)),
                ('diffrn_reflns_theta_max', models.FloatField(blank=True, null=True)),
                ('diffrn_reflns_theta_full', models.FloatField(blank=True, null=True)),
                ('diffrn_measured_fraction_theta_max', models.FloatField(blank=True, null=True)),
                ('diffrn_measured_fraction_theta_full', models.FloatField(blank=True, null=True)),
                ('reflns_number_total', models.PositiveIntegerField(blank=True, null=True)),
                ('reflns_number_gt', models.PositiveIntegerField(blank=True, null=True)),
                ('reflns_threshold_expression', models.CharField(blank=True, max_length=255, null=True)),
                ('reflns_Friedel_coverage', models.FloatField(blank=True, null=True)),
                ('computing_structure_solution', models.CharField(blank=True, max_length=255, null=True)),
                ('computing_structure_refinement', models.CharField(blank=True, max_length=255, null=True)),
                ('refine_special_details', models.TextField(blank=True, null=True)),
                ('refine_ls_abs_structure_Flack', models.FloatField(blank=True, null=True)),
                ('refine_ls_structure_factor_coef', models.CharField(blank=True, max_length=255, null=True)),
                ('refine_ls_weighting_details', models.TextField(blank=True, null=True)),
                ('refine_ls_number_reflns', models.PositiveIntegerField(blank=True, null=True)),
                ('refine_ls_number_parameters', models.PositiveIntegerField(blank=True, null=True)),
                ('refine_ls_number_restraints', models.PositiveIntegerField(blank=True, null=True)),
                ('refine_ls_R_factor_all', models.FloatField(blank=True, null=True)),
                ('refine_ls_R_factor_gt', models.FloatField(blank=True, null=True)),
                ('refine_ls_wR_factor_ref', models.FloatField(blank=True, null=True)),
                ('refine_ls_wR_factor_gt', models.FloatField(blank=True, null=True)),
                ('refine_ls_goodness_of_fit_ref', models.FloatField(blank=True, null=True)),
                ('refine_ls_restrained_S_all', models.FloatField(blank=True, null=True)),
                ('refine_ls_shift_su_max', models.FloatField(blank=True, null=True)),
                ('refine_ls_shift_su_mean', models.FloatField(blank=True, null=True)),
                ('refine_diff_density_max', models.FloatField(blank=True, null=True)),
                ('refine_diff_density_min', models.FloatField(blank=True, null=True)),
                ('refine_diff_density_rms', models.FloatField(blank=True, null=True)),
                ('diffrn_reflns_av_unetI_netI', models.FloatField(blank=True, null=True)),
                ('database_code_depnum_ccdc_archive', models.CharField(blank=True, max_length=255, null=True, verbose_name='CCDC number')),
                ('shelx_res_file', models.TextField(blank=True, max_length=10000000, null=True)),
                ('shelx_res_checksum', models.PositiveIntegerField(blank=True, null=True)),
                ('reflns_Friedel_fraction_full', models.FloatField(blank=True, null=True)),
                ('refine_ls_abs_structure_details', models.FloatField(blank=True, null=True)),
                ('reflns_special_details', models.FloatField(blank=True, null=True)),
                ('computing_data_collection', models.CharField(blank=True, max_length=2048, null=True)),
                ('computing_cell_refinement', models.CharField(blank=True, max_length=2048, null=True)),
                ('computing_data_reduction', models.CharField(blank=True, max_length=2048, null=True)),
                ('computing_molecular_graphics', models.CharField(blank=True, max_length=2048, null=True)),
                ('computing_publication_material', models.CharField(blank=True, max_length=2048, null=True)),
                ('atom_sites_solution_primary', models.CharField(blank=True, max_length=2048, null=True)),
                ('atom_sites_solution_secondary', models.CharField(blank=True, max_length=2048, null=True)),
                ('atom_sites_solution_hydrogens', models.CharField(blank=True, max_length=2048, null=True)),
                ('refine_ls_hydrogen_treatment', models.CharField(blank=True, max_length=2048, null=True)),
                ('refine_ls_extinction_method', models.CharField(blank=True, max_length=2048, null=True)),
                ('refine_ls_extinction_coef', models.FloatField(blank=True, null=True)),
                ('refine_ls_extinction_expression', models.CharField(blank=True, max_length=2048, null=True)),
                ('geom_special_details', models.TextField(blank=True, max_length=2048, null=True)),
                ('diffrn_radiation_monochromator', models.CharField(blank=True, max_length=2048, null=True)),
                ('diffrn_measurement_method', models.CharField(blank=True, max_length=2048, null=True)),
                ('shelx_estimated_absorpt_T_min', models.FloatField(blank=True, null=True)),
                ('shelx_estimated_absorpt_T_max', models.FloatField(blank=True, null=True)),
                ('exptl_absorpt_correction_T_min', models.FloatField(blank=True, null=True)),
                ('exptl_absorpt_correction_T_max', models.FloatField(blank=True, null=True)),
                ('exptl_absorpt_process_details', models.CharField(blank=True, max_length=2048, null=True)),
                ('exptl_absorpt_special_details', models.CharField(blank=True, max_length=2048, null=True)),
                ('diffrn_radiation_probe', models.CharField(blank=True, max_length=2048, null=True)),
                ('diffrn_measurement_details', models.CharField(blank=True, max_length=2048, null=True)),
                ('diffrn_detector', models.CharField(blank=True, max_length=2048, null=True)),
                ('diffrn_detector_type', models.CharField(blank=True, max_length=2048, null=True)),
                ('diffrn_detector_area_resol_mean', models.FloatField(blank=True, null=True)),
                ('diffrn_reflns_limit_h_max', models.IntegerField(blank=True, null=True)),
                ('diffrn_reflns_limit_h_min', models.IntegerField(blank=True, null=True)),
                ('diffrn_reflns_limit_k_max', models.IntegerField(blank=True, null=True)),
                ('diffrn_reflns_limit_k_min', models.IntegerField(blank=True, null=True)),
                ('diffrn_reflns_limit_l_max', models.IntegerField(blank=True, null=True)),
                ('diffrn_reflns_limit_l_min', models.IntegerField(blank=True, null=True)),
                ('diffrn_reflns_Laue_measured_fraction_full', models.FloatField(blank=True, null=True)),
                ('diffrn_reflns_Laue_measured_fraction_max', models.FloatField(blank=True, null=True)),
                ('exptl_crystal_density_meas', models.FloatField(blank=True, null=True)),
                ('exptl_crystal_density_method', models.CharField(blank=True, max_length=2048, null=True)),
                ('exptl_crystal_density_diffrn', models.FloatField(blank=True, null=True)),
                ('exptl_crystal_F_000', models.FloatField(blank=True, null=True)),
                ('exptl_transmission_factor_min', models.FloatField(blank=True, null=True)),
                ('exptl_transmission_factor_max', models.FloatField(blank=True, null=True)),
                ('exptl_crystal_face_x', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CrystalGlue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('glue', models.CharField(max_length=200, unique=True, verbose_name='crystal glue')),
            ],
        ),
        migrations.CreateModel(
            name='CrystalShape',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('habitus', models.CharField(max_length=200, unique=True, verbose_name='crystal shape')),
            ],
        ),
        migrations.CreateModel(
            name='CrystalSupport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('support', models.CharField(max_length=200, unique=True, verbose_name='crystal support')),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experiment', models.CharField(default='', max_length=200, unique=True, verbose_name='experiment name')),
                ('number', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='number')),
                ('publishable', models.BooleanField(default=False, verbose_name='structure is publishable')),
                ('sum_formula', models.CharField(blank=True, max_length=300)),
                ('prelim_unit_cell', models.CharField(blank=True, max_length=250, verbose_name='preliminary unit cell')),
                ('measure_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='measurement date')),
                ('submit_date', models.DateField(blank=True, null=True, verbose_name='sample submission date')),
                ('result_date', models.DateField(blank=True, null=True, verbose_name='results sent date')),
                ('crystal_size_x', models.FloatField(blank=True, null=True, verbose_name='crystal size max')),
                ('crystal_size_y', models.FloatField(blank=True, null=True, verbose_name='crystal size mid')),
                ('crystal_size_z', models.FloatField(blank=True, null=True, verbose_name='crystal size min')),
                ('crystal_colour', models.IntegerField(choices=[(0, 'not applicable'), (1, 'colourless'), (2, 'white'), (3, 'black'), (4, 'gray'), (5, 'brown'), (6, 'red'), (7, 'pink'), (8, 'orange'), (9, 'yellow'), (10, 'green'), (11, 'blue'), (12, 'violet')], default=0)),
                ('crystal_colour_mod', models.IntegerField(choices=[(0, 'not applicable'), (1, 'light'), (2, 'dark'), (3, 'whitish'), (4, 'blackish'), (5, 'grayish'), (6, 'brownish'), (7, 'reddish'), (8, 'pinkish'), (9, 'orangish'), (10, 'yellowish'), (11, 'greenish'), (12, 'bluish')], default=0, verbose_name='crystal colour modifier')),
                ('crystal_colour_lustre', models.IntegerField(choices=[(0, 'not applicable'), (1, 'metallic'), (2, 'dull'), (3, 'clear')], default=0)),
                ('special_details', models.TextField(blank=True, default='', null=True, verbose_name='experimental special details')),
                ('base', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='scxrd.CrystalSupport', verbose_name='sample base')),
                ('cif', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experiments', to='scxrd.CifFile', verbose_name='cif file')),
            ],
            options={
                'ordering': ['-number'],
            },
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='machines name')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=200)),
                ('last_name', models.CharField(blank=True, max_length=200)),
                ('company', models.CharField(blank=True, max_length=200, verbose_name='company')),
                ('street', models.CharField(blank=True, max_length=250)),
                ('house_number', models.CharField(blank=True, max_length=200)),
                ('building', models.CharField(blank=True, max_length=200)),
                ('town', models.CharField(blank=True, max_length=200)),
                ('country', models.CharField(blank=True, max_length=200)),
                ('postal_code', models.CharField(blank=True, max_length=200)),
                ('email_adress', models.EmailField(blank=True, max_length=250, validators=[scxrd.models.validate_email])),
                ('phone_number', models.CharField(blank=True, max_length=17)),
                ('comment', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Solvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='solvents name')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SumFormula',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('C', models.FloatField(default=0)),
                ('D', models.FloatField(default=0)),
                ('H', models.FloatField(default=0)),
                ('N', models.FloatField(default=0)),
                ('O', models.FloatField(default=0)),
                ('Cl', models.FloatField(default=0)),
                ('Br', models.FloatField(default=0)),
                ('I', models.FloatField(default=0)),
                ('F', models.FloatField(default=0)),
                ('S', models.FloatField(default=0)),
                ('P', models.FloatField(default=0)),
                ('Ac', models.FloatField(default=0)),
                ('Ag', models.FloatField(default=0)),
                ('Al', models.FloatField(default=0)),
                ('Am', models.FloatField(default=0)),
                ('Ar', models.FloatField(default=0)),
                ('As', models.FloatField(default=0)),
                ('At', models.FloatField(default=0)),
                ('Au', models.FloatField(default=0)),
                ('B', models.FloatField(default=0)),
                ('Ba', models.FloatField(default=0)),
                ('Be', models.FloatField(default=0)),
                ('Bi', models.FloatField(default=0)),
                ('Bk', models.FloatField(default=0)),
                ('Ca', models.FloatField(default=0)),
                ('Cd', models.FloatField(default=0)),
                ('Ce', models.FloatField(default=0)),
                ('Cf', models.FloatField(default=0)),
                ('Cm', models.FloatField(default=0)),
                ('Co', models.FloatField(default=0)),
                ('Cr', models.FloatField(default=0)),
                ('Cs', models.FloatField(default=0)),
                ('Cu', models.FloatField(default=0)),
                ('Dy', models.FloatField(default=0)),
                ('Er', models.FloatField(default=0)),
                ('Eu', models.FloatField(default=0)),
                ('Fe', models.FloatField(default=0)),
                ('Fr', models.FloatField(default=0)),
                ('Ga', models.FloatField(default=0)),
                ('Gd', models.FloatField(default=0)),
                ('Ge', models.FloatField(default=0)),
                ('He', models.FloatField(default=0)),
                ('Hf', models.FloatField(default=0)),
                ('Hg', models.FloatField(default=0)),
                ('Ho', models.FloatField(default=0)),
                ('In', models.FloatField(default=0)),
                ('Ir', models.FloatField(default=0)),
                ('K', models.FloatField(default=0)),
                ('Kr', models.FloatField(default=0)),
                ('La', models.FloatField(default=0)),
                ('Li', models.FloatField(default=0)),
                ('Lu', models.FloatField(default=0)),
                ('Mg', models.FloatField(default=0)),
                ('Mn', models.FloatField(default=0)),
                ('Mo', models.FloatField(default=0)),
                ('Na', models.FloatField(default=0)),
                ('Nb', models.FloatField(default=0)),
                ('Nd', models.FloatField(default=0)),
                ('Ne', models.FloatField(default=0)),
                ('Ni', models.FloatField(default=0)),
                ('Np', models.FloatField(default=0)),
                ('Os', models.FloatField(default=0)),
                ('Pa', models.FloatField(default=0)),
                ('Pb', models.FloatField(default=0)),
                ('Pd', models.FloatField(default=0)),
                ('Pm', models.FloatField(default=0)),
                ('Po', models.FloatField(default=0)),
                ('Pr', models.FloatField(default=0)),
                ('Pt', models.FloatField(default=0)),
                ('Pu', models.FloatField(default=0)),
                ('Ra', models.FloatField(default=0)),
                ('Rb', models.FloatField(default=0)),
                ('Re', models.FloatField(default=0)),
                ('Rh', models.FloatField(default=0)),
                ('Rn', models.FloatField(default=0)),
                ('Ru', models.FloatField(default=0)),
                ('Sb', models.FloatField(default=0)),
                ('Sc', models.FloatField(default=0)),
                ('Se', models.FloatField(default=0)),
                ('Si', models.FloatField(default=0)),
                ('Sm', models.FloatField(default=0)),
                ('Sn', models.FloatField(default=0)),
                ('Sr', models.FloatField(default=0)),
                ('Ta', models.FloatField(default=0)),
                ('Tb', models.FloatField(default=0)),
                ('Tc', models.FloatField(default=0)),
                ('Te', models.FloatField(default=0)),
                ('Th', models.FloatField(default=0)),
                ('Ti', models.FloatField(default=0)),
                ('Tl', models.FloatField(default=0)),
                ('Tm', models.FloatField(default=0)),
                ('U', models.FloatField(default=0)),
                ('V', models.FloatField(default=0)),
                ('W', models.FloatField(default=0)),
                ('Xe', models.FloatField(default=0)),
                ('Y', models.FloatField(default=0)),
                ('Yb', models.FloatField(default=0)),
                ('Zn', models.FloatField(default=0)),
                ('Zr', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='WorkGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_head', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='group', to='scxrd.Person')),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='work_group',
            field=models.ForeignKey(blank=True, max_length=200, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='person', to='scxrd.WorkGroup'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experiment', to='scxrd.Person'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='glue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='scxrd.CrystalGlue', verbose_name='sample glue'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='experiments', to='scxrd.Machine', verbose_name='diffractometer'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiments', to=settings.AUTH_USER_MODEL, verbose_name='operator'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='solvent1',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experiment1', to='scxrd.Solvent', verbose_name='solvent 1'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='solvent2',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experiment2', to='scxrd.Solvent', verbose_name='solvent 2'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='solvent3',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experiment3', to='scxrd.Solvent', verbose_name='solvents 3'),
        ),
        migrations.AddField(
            model_name='ciffile',
            name='sumform_calc',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='cif_file', to='scxrd.SumFormula'),
        ),
        migrations.AddField(
            model_name='atom',
            name='cif',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scxrd.CifFile'),
        ),
    ]
