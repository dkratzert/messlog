from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from djangow2ui.grid import W2UIGridView

from scxrd.forms import ExperimentForm
from django.urls import reverse_lazy
from django.shortcuts import render

from scxrd.models import Experiment
from django_datatables_view.base_datatable_view import BaseDatatableView


class ExperimentCreateView(CreateView):
    """
    A new experimen
    """
    model = Experiment
    form_class = ExperimentForm
    template_name = 'scxrd/new_experiment.html'
    # Fields are defined in form_class:
    #fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'operator')
    success_url = reverse_lazy('scxrd:index')


class ExperimentEditView(UpdateView):
    """
    Edit an experiment
    """
    model = Experiment
    form_class = ExperimentForm
    template_name = 'scxrd/experiment_edit_form.html'
    success_url = reverse_lazy('scxrd:index')


class ExperimentDetailView(DetailView):
    """
    Show details of an experiment
    """
    model = Experiment
    template_name = 'scxrd/experiment_detail.html'


def experiment_test(request, pk):
    #print(pk)
    object = Experiment.objects.get(pk=pk)
    template = 'scxrd/details_table.html'
    return render(request, template, {'object': object})


class ExperimentView(TemplateView):
    model = Experiment
    template_name = 'scxrd/scxrd_index.html'


class OrderListJson(BaseDatatableView):
    # The model we're going to show
    model = Experiment
    # template_name = 'scxrd/experiment_grid.html'

    # define the columns that will be returned
    columns = ['id', 'number', 'experiment', 'measure_date', 'machine', 'solvent']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['id', 'number', 'experiment', 'measure_date', 'machine', 'solvent']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 5000000


