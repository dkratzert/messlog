from django.contrib import admin

# Register your models here.
from scxrd.cif_model import Atom, SumFormula
from scxrd.models import Customer, CifFile, Machine, Solvent, Experiment


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
    inlines = [AtomsInline]

"""
admin.site.register(MyUser, UserAdmin)

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    #fieldsets = UserAdmin.fieldsets + (
    #        (None, {'fields': ('some_extra_data',)}),
    #)

"""

admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Machine)
admin.site.register(Solvent)
admin.site.register(Customer)
admin.site.register(CifFile, CifAdmin)

