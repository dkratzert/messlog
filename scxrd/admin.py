from pathlib import Path

from django.contrib import admin
from django.contrib.admin import StackedInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from scxrd.cif.cif_file_io import CifContainer
from scxrd.customer_models import SCXRDSample
from scxrd.models import CifFileModel, Machine, Experiment, WorkGroup, CrystalSupport, CrystalGlue, Profile


# Register your models here.
# from myuser.models import MyUser


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'cif_file_on_disk')
    list_filter = ['measure_date']
    search_fields = ['experiment', 'number', 'sum_formula']
    ordering = ['-number']

    def get_form(self, request, obj=None, **kwargs):
        form = super(ExperimentAdmin, self).get_form(request, obj, **kwargs)
        try:
            form.base_fields['number'].initial = Experiment.objects.first().number + 1
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
        return Experiment.objects.get(cif=obj.pk)

    def number_of_atoms(self, obj):
        try:
            exp = Experiment.objects.get(cif=obj.pk)
            # Path(MEDIA_ROOT).joinpath()
            cif = CifContainer(Path(str(exp.cif_file_on_disk.file)))
        except RuntimeError:
            return _('no atoms found')
        # Example:
        # return exp.get_cif_file_parameter('_audit_creation_method')
        return cif.natoms()


class PersonInline(StackedInline):
    model = Profile
    can_delete = False


class WorkGroupInline(admin.TabularInline):
    fields = ('group_head',)
    ordering = ('group_head',)
    model = WorkGroup
    extra = 3

class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)


# admin.site.register(MyUser)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(CifFileModel, CifAdmin)
admin.site.register(SCXRDSample)
# admin.site.register(Person)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(WorkGroup)
admin.site.register(Machine)
admin.site.register(CrystalSupport)
admin.site.register(CrystalGlue)
