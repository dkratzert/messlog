from django.contrib import admin

# Register your models here.
from .models import Experiment, Machine, Solvent


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula')
    list_filter = ['measure_date']
    search_fields = ['experiment', 'number', 'sum_formula']
    ordering = ['number']


admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Machine)
admin.site.register(Solvent)

