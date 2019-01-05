from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput

from scxrd import widgets
from scxrd.cif.mol_file_writer import MolFile
from scxrd.cif_model import SumFormula, Atom
from scxrd.forms import ExperimentForm, ExperimentTableForm
from django.urls import reverse_lazy
from django.shortcuts import render

from scxrd.models import Experiment, Customer, CifFile
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


class DetailsTable(DetailView):
    model = Experiment
    template_name = 'scxrd/details_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['sumform'] = SumFormula.objects.get(pk=self.kwargs['pk'])
        except SumFormula.DoesNotExist:
            pass
        return context


class UploadView(CreateView):
    model = Experiment
    template_name = "scxrd/upload.html"
    #success_url = reverse_lazy('scxrd:index')
    form_class = ExperimentForm

    def get_success_url(self):
        return reverse_lazy('scxrd:upload', kwargs=dict(pk=self.object.pk))


class ExperimentView(TemplateView):
    model = Experiment
    template_name = 'scxrd/scxrd_index.html'


class Customers(ListView):
    model = Customer
    template_name = 'scxrd/customers.html'


class AtomsView(DetailView):
    """
    View to get atom data as .mol file.
    """
    model = Experiment
    template_name = 'scxrd/molecule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #atoms = Experiment.cif.atoms.get(pk=self.kwargs['pk'])
        atoms = Atom.objects.all().filter(cif_id=2)
        try:
            # TODO: adapt to this atom format
            m = MolFile(atoms)
            return m.make_mol()
        except(KeyError, TypeError) as e:
            print('Exception in jsmol_request: {}'.format(e))
        return context


class OrderListJson(BaseDatatableView):
    # The model we're going to show
    model = Experiment
    # template_name = 'scxrd/experiment_grid.html'

    # define the columns that will be returned
    columns = ['-id', 'number', 'experiment', 'measure_date', 'machine']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', 'number', 'experiment', 'measure_date', 'machine']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 5000000

