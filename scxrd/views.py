from django.http import HttpResponse
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.shortcuts import render, get_object_or_404
from bootstrap_datepicker_plus import DatePickerInput
from django_tables2 import SingleTableView, Table
from djangow2ui.grid import W2UIGridView

from scxrd.forms import ExperimentForm, ExperimentTableForm
from django.urls import reverse_lazy

# Create your views here.
from django.views import generic

from scxrd.models import Experiment
from scxrd.tables import ExperimentTable


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
        show__header = False
        show__toolbar = False
        show__footer = False
        show__lineNumbers = False
    
    
    
    """
    def getQueryset(self, request, *args, **kwargs):
        qs = super().getQueryset(request, *args, **kwargs)
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            qs = qs.filter(pk=pk)
        return qs
    
    #def get_context_data(self, **kwargs):
    #    context = super().get_context_data(**kwargs)
    #    context['grid'] = Experiment.objects.all() # .filer() for example
    #    return context
    """