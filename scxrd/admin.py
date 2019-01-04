from django.contrib import admin

# Register your models here.
from scxrd.cif_model import Atom
from scxrd.models import Customer, CifFile
from .models import Experiment, Machine, Solvent


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'cif')
    list_filter = ['measure_date']
    search_fields = ['experiment', 'number', 'sum_formula']
    ordering = ['number']


class AtomsInline(admin.TabularInline):
    model = Atom
    extra = 0
    readonly_fields = ('name', 'element', 'x', 'y', 'z', 'part', 'occupancy')
    #list_display = ('__str__',)
    fieldsets = (
        ('Atoms in cif file', {
            'fields': ('name', 'element', 'x', 'y', 'z'),
            #'fields': ('__str__',),
            'classes': ('collapse',),
        }),

    )


class CifAdmin(admin.ModelAdmin):
    inlines = [AtomsInline]


admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Machine)
admin.site.register(Solvent)
admin.site.register(Customer)
admin.site.register(CifFile, CifAdmin)
