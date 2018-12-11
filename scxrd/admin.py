from django.contrib import admin

# Register your models here.
from scxrd.models import Customer
from .models import Experiment, Machine, Solvent, Upload


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula')
    list_filter = ['measure_date']
    search_fields = ['experiment', 'number', 'sum_formula']
    ordering = ['number']




admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Machine)
admin.site.register(Solvent)
admin.site.register(Customer)
admin.site.register(Upload)

