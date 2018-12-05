
import django_tables2 as tables
from .models import Experiment


class ExperimentTable(tables.Table):
    #experiment = tables.Column(accessor="experiment")
    #number = tables.Column(accessor="number")
    #measure_date = tables.Column(accessor="measure_date")
    sum_formula = tables.Column(visible=False)

    class Meta:
        model = Experiment
        sequence = ('number', 'experiment', 'measure_date')  # order of displayed items
        exclude = ('machine', 
                   #'sum_formula', 
                   'solvents_used', 'submit_date', 'result_date', 'actual_hours', 'id')


