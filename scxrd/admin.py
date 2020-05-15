from django.conf.urls import url
from django.contrib import admin

from scxrd.cif_model import Atom
from scxrd.models import CifFileModel, Machine, Experiment, WorkGroup
from scxrd.models import CrystalSupport, CrystalShape, CrystalGlue
from scxrd.models import Person


# Register your models here.
# from myuser.models import MyUser


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'cif')
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


class AtomsInline(admin.TabularInline):
    model = Atom
    extra = 0
    readonly_fields = ('name', 'element', 'x', 'y', 'z', 'part', 'occupancy')
    fieldsets = (
        ('Atoms in cif file', {
            'fields': ('name', 'element', 'x', 'y', 'z'),
            'classes': ('collapse',),
        }),
    )


"""class SumFormInline(admin.TabularInline):
    model = SumFormula
    extra = 0
    can_delete = False

    def get_sumf(self, obj):
        return obj.__str__"""


class CifAdmin(admin.ModelAdmin):
    model = CifFileModel
    list_display = ['edit_file', 'cif_file_on_disk', 'related_experiment', 'number_of_atoms']

    def edit_file(self, obj):
        return self.model.objects.get(id=obj.id)

    def related_experiment(self, obj):
        return Experiment.objects.get(cif_id=obj.pk)

    def number_of_atoms(self, obj):
        return Atom.objects.filter(cif_id=obj.pk).count()


"""class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = MyUser"""

# class MyUserAdmin(UserAdmin):
#    form = MyUserChangeForm
#
# fieldsets = UserAdmin.fieldsets + (
#        (None, {'fields': ('some_extra_data',)}),
# )


# admin.site.register(MyUser)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(CifFileModel, CifAdmin)
admin.site.register(Person)
admin.site.register(WorkGroup)
admin.site.register(Machine)
#admin.site.register(Solvent)
admin.site.register(CrystalSupport)
admin.site.register(CrystalShape)
admin.site.register(CrystalGlue)
