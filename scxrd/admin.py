from pathlib import Path

from django.contrib import admin
from django.contrib.admin import StackedInline, TabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.db.models import Count
from django.utils.datetime_safe import datetime
from django.utils.translation import gettext_lazy as _

from scxrd.cif.cif_file_io import CifContainer
from scxrd.models.cif_model import CifFileModel
from scxrd.models.sample_model import Sample
from scxrd.models.models import Machine, WorkGroup, CrystalSupport, CrystalGlue, Profile
from scxrd.models.experiment_model import Measurement

admin.site.site_header = "MESSLOG Admin"
admin.site.site_title = "MESSLOG Admin Portal"
admin.site.index_title = "MESSLOG Administration"


class WorkGroupInline(TabularInline):
    model = Profile
    list_display = ('members',)
    #fields = ('user',)
    extra = 0

    fieldsets = (
        ('user', {
            'fields': ('user', )
        }),
    )

    def members(self, obj: WorkGroup):
        WorkGroup.objects.filter(profiles__user=obj)


class WorkGroupAdmin(admin.ModelAdmin):
    model = WorkGroup
    list_display = ('group_head', 'members', 'measurements_this_year')
    inlines = (WorkGroupInline,)

    def members(self, obj: WorkGroup):
        return len(User.objects.filter(profile__work_group_id=obj.pk))

    def measurements_this_year(self, group: WorkGroup):
        today = datetime.now()
        return Measurement.objects.filter(measure_date__gt=str(today.year) + '-1-1',
                                          customer__profile__work_group=group).count()


class ExperimentInline(StackedInline):
    model = CifFileModel
    can_delete = True


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment_name', 'number', 'measure_date', 'machine', 'sum_formula', 'customer')
    list_filter = ['measure_date']
    search_fields = ['experiment_name', 'number', 'sum_formula']
    ordering = ['-number']
    inlines = (ExperimentInline,)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ExperimentAdmin, self).get_form(request, obj, **kwargs)
        try:
            form.base_fields['number'].initial = Measurement.objects.first().number + 1
        except AttributeError:
            form.base_fields['number'].initial = 1
        return form


class CifAdmin(admin.ModelAdmin):
    model = CifFileModel
    list_display = ['edit_file', 'data', 'related_experiment', 'number_of_atoms']

    def edit_file(self, obj):
        return self.model.objects.get(id=obj.id)

    @staticmethod
    def related_experiment(obj):
        return Measurement.objects.get(ciffilemodel=obj.pk)

    def number_of_atoms(self, obj):
        try:
            # cif = CifFileModel.objects.get(cif_file_on_disk=obj.pk)
            cif = CifContainer(Path(str(obj.cif_file_on_disk.file)))
        except RuntimeError:
            return _('no atoms found')
        # Example:
        # return exp.get_cif_file_parameter('_audit_creation_method')
        return cif.natoms()


class PersonInline(StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)
    list_display = ['username', 'first_name', 'last_name', 'number_of_experiments', 'work_group', 'is_staff',
                    'is_operator']
    list_filter = ('is_superuser', 'profile__work_group')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def is_operator(self, obj: User):
        return obj.profile.is_operator

    def work_group(self, obj: User):
        return obj.profile.work_group

    def number_of_experiments(self, obj: User):
        return obj.operator_experiments.count()  # Measurement.objects.filter(operator=obj).count()

    is_operator.boolean = True


class GluesAdmin(admin.ModelAdmin):
    model = CrystalGlue
    list_display = ['glue', 'used_by']

    def get_queryset(self, request):
        """Method to do the sorting for the admin_order_field"""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _used_by=Count('experiments', distinct=True),
        )
        return queryset

    def used_by(self, obj):
        """Returns the number of experiment that use this glue"""
        return obj.experiments.count()

    used_by.admin_order_field = '_used_by'


class CrystalSupportAdmin(admin.ModelAdmin):
    model = CrystalSupport
    list_display = ['support', 'used_by']

    def used_by(self, obj):
        """Returns the number of experiment that use this glue"""
        return obj.experiments.count()


class MachinesAdmin(admin.ModelAdmin):
    model = Machine
    list_display = ['diffrn_measurement_device_type', 'measurements', 'measurements_last_year',
                    'measurements_this_year']

    def measurements(self, machine):
        """Returns the number of experiment that use this machine"""
        return machine.experiments.count()

    def measurements_last_year(self, machine: Machine):
        today = datetime.now()
        return machine.experiments.filter(measure_date__gt=str(today.year - 1) + '-1-1',
                                          measure_date__lt=str(today.year) + '-1-1').count()

    def measurements_this_year(self, machine: Machine):
        today = datetime.now()
        return machine.experiments.filter(measure_date__gt=str(today.year) + '-1-1').count()


admin.site.unregister(Group)
admin.site.register(Measurement, ExperimentAdmin)
admin.site.register(CifFileModel, CifAdmin)
# admin.site.register(CifFileModel)
admin.site.register(Sample)
# admin.site.register(Person)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(WorkGroup, WorkGroupAdmin)
admin.site.register(Machine, MachinesAdmin)
admin.site.register(CrystalSupport, CrystalSupportAdmin)
admin.site.register(CrystalGlue, GluesAdmin)
