from django.contrib import admin

# Register your models here.
from django import forms
from django.forms import MultipleChoiceField

from .models import Experiment, Machine, Solvent


class SolventInline(admin.TabularInline):
    model = Solvent


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'number', 'date', 'machine', 'solvents_used', 'sum_formula')
    list_filter = ['date']
    search_fields = ['experiment', 'number', 'sum_formula']
    empty_value_display = 'unknown'
    #inlines = [SolventInline, ]
    formfield_overrides = {
        Solvent: {'widget': MultipleChoiceField},
    }


admin.site.register(Experiment, ExperimentAdmin)
#admin.site.register(Machine)
#admin.site.register(Solvent)
