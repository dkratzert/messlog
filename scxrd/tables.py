
import django_tables2 as tables
from .models import Experiment


class ExperimentTable(tables.Table):
    #experiment = tables.Column(accessor="experiment")
    #number = tables.Column(accessor="number")
    #measure_date = tables.Column(accessor="measure_date")
    sum_formula = tables.Column(visible=False)
    id = tables.Column(attrs={'td': {'style': 'visibility:hidden'}})

    class Meta:
        model = Experiment
        sequence = ('number', 'experiment', 'measure_date')  # order of displayed items
        exclude = (#'id',
                   'machine',
                   'solvents_used',
                   'submit_date',
                   'result_date',
                   'actual_hours',
                   #'sum_formula',
                   )
        # already in settings.py:
        # template_name = 'django_tables2/bootstrap-responsive.html'


