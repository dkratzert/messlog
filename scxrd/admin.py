from django.contrib import admin

# Register your models here.
from filer.admin import FileAdmin

from scxrd.models import Customer
from .models import Experiment, Machine, Solvent


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'cif')
    list_filter = ['measure_date']
    search_fields = ['experiment', 'number', 'sum_formula']
    ordering = ['number']





admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Machine)
admin.site.register(Solvent)
admin.site.register(Customer)
#admin.site.register()

