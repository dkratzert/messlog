from django.views.generic import CreateView, UpdateView, DetailView
from bootstrap_datepicker_plus import DatePickerInput
from djangow2ui.grid import W2UIGridView

from scxrd.forms import ExperimentForm
from django.urls import reverse_lazy

from scxrd.models import Experiment
from django_datatables_view.base_datatable_view import BaseDatatableView


class ExperimentCreateView(CreateView):
    model = Experiment
    template_name = 'scxrd/new_experiment.html'
    fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'owner')
    success_url = reverse_lazy('scxrd:index')


class ExperimentEditView(UpdateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = 'scxrd/experiment_edit_form.html'
    success_url = reverse_lazy('scxrd:index')

    def get_form(self,  form_class=None):
        form = super().get_form()
        form.fields['measure_date'].widget = DatePickerInput(format='%Y-%m-%d')
        form.fields['submit_date'].widget = DatePickerInput(format='%Y-%m-%d')
        form.fields['result_date'].widget = DatePickerInput(format='%Y-%m-%d')
        return form


class ExperimentShowView(DetailView):
    model = Experiment
    template_name = 'scxrd/experiment_detail.html'

"""
class IndexView(SingleTableView):
    SingleTableView.table_pagination = False
    model = Experiment
    table_class = ExperimentTable
    template_name = 'scxrd/scxrd_index.html'

    # defines the context object name to be used with {% if experiment_list %} etc.
    #context_object_name = 'experiment_table'

   # # add other contexts if needed
   # def get_context_data(self, **kwargs):
   #     context = super().get_context_data(**kwargs)
   #     context['table'] = Experiment.objects.all() # .filer() for example
   #     return context
"""


class ExperimentView(W2UIGridView):
    model = Experiment
    fields = ('experiment', 
              'measure_date',
              'sum_formula',
              'machine',
              #'machine_name',
              #'owner'
              )
    editable = False
    template_name = 'scxrd/scxrd_index.html'

    class W2UI:
        name = 'grid'
        show__header = False
        show__toolbar = False
        show__footer = False
        show__lineNumbers = True
        show__selectColumn = False
        show__selectRow = True


class OrderListJson(BaseDatatableView):
    # The model we're going to show
    model = Experiment
    template_name = "scxrd/grid.html"
    # define the columns that will be returned
    columns = ('number', 'experiment', 'measure_date', 'machine', 'sum_formula', 'owner')

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['number', 'experiment', 'measure_date', 'machine', 'sum_formula', 'owner']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    #def get_context_data(self, **kwargs):
    #    context = super().get_context_data(**kwargs)
    #    context['index'] = Experiment.objects.all()  # .filer() for example
    #    return context

    """
    def getQueryset(self, request, *args, **kwargs):
        qs = super().getQueryset(request, *args, **kwargs)
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            qs = qs.filter(pk=pk)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grid'] = Experiment.objects.all() # .filer() for example
        return context
    """

