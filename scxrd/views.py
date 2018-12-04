from django.http import HttpResponse
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.shortcuts import render, get_object_or_404
from bootstrap_datepicker_plus import DatePickerInput
from django_tables2 import SingleTableView

from scxrd.forms import ExperimentForm
from django.urls import reverse_lazy

# Create your views here.
from django.views import generic

from scxrd.models import Experiment, SimpleTable


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


class IndexView(generic.ListView):
    template_name = 'scxrd/index.html'
    # defines the context object name to be used with {% if experiment_list %} etc.
    context_object_name = 'experiment_list'
    queryset = Experiment.objects.all()

    # add other contexts if needed
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = Experiment.objects.all()
        return context


