from django.http import HttpResponse
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.shortcuts import render, get_object_or_404
from bootstrap_datepicker_plus import DatePickerInput
from django_tables2 import SingleTableView, Table

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


class IndexView(SingleTableView):
    SingleTableView.table_pagination = False
    template_name = 'scxrd/scxrd_index.html'
    #fields = ('experiment', 'number', 'measure_date')
    model = Experiment
    table_class = ExperimentTable

    # defines the context object name to be used with {% if experiment_list %} etc.
    #context_object_name = 'experiment_table'


   # # add other contexts if needed
   # def get_context_data(self, **kwargs):
   #     context = super().get_context_data(**kwargs)
   #     context['table'] = Experiment.objects.all() # .filer() for example
   #     return context


