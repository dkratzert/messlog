from django.contrib import admin

from scxrd.cif_model import Atom
from scxrd.models import CifFile, Machine, Solvent, Experiment, WorkGroup
from scxrd.models import CrystalSupport, CrystalShape, CrystalGlue
from scxrd.models import Person


# Register your models here.
# from myuser.models import MyUser


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'cif')
    list_filter = ['measure_date']
    search_fields = ['experiment', 'number', 'sum_formula']
    ordering = ['-number']


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
    pass
    #inlines = [AtomsInline]


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
admin.site.register(CifFile, CifAdmin)
admin.site.register(Person)
admin.site.register(WorkGroup)
admin.site.register(Machine)
admin.site.register(Solvent)
admin.site.register(CrystalSupport)
admin.site.register(CrystalShape)
admin.site.register(CrystalGlue)

