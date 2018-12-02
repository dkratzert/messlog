from django.contrib import admin

# Register your models here.
from django import forms
from django.forms import MultipleChoiceField

from .models import Experiment, Machine, Solvent


class SolventInline(admin.TabularInline):
    model = Experiment.solvents_used.through


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'date', 'machine', 'sum_formula')
    list_filter = ['date']
    search_fields = ['experiment', 'number', 'sum_formula']
    ordering = ['number']
    #empty_value_display = 'unknown'
    #formfield_overrides = {
    #    Solvent: {'widget': MultipleChoiceField},
    #}


admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Machine)
admin.site.register(Solvent)
