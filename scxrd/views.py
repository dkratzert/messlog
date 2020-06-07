from datetime import datetime
from pathlib import Path
from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.timezone import make_naive
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView
from django.views.generic.edit import FormMixin
from django_datatables_view.base_datatable_view import BaseDatatableView

from mysite.settings import MEDIA_ROOT
from scxrd.cif.cif_file_io import CifContainer
from scxrd.cif.mol_file_writer import MolFile
from scxrd.cif.sdm import SDM
from scxrd.customer_models import SCXRDSample
from scxrd.forms import ExperimentEditForm, ExperimentNewForm
from scxrd.models import Experiment
from scxrd.models import Person


class FormActionMixin(LoginRequiredMixin, FormMixin):

    def post(self, request, *args, **kwargs):
        """Add 'Cancel' button redirect."""
        print('The post request:')
        pprint(request.POST)
        print('end request ----------------')
        c = request.POST.get("cancel")
        if c and c.lower() == 'cancel':
            url = reverse_lazy('scxrd:index')  # or e.g. reverse(self.get_success_url())
            return HttpResponseRedirect(url)
        # if 'upload_cif' in request.POST:
        #    return HttpResponseRedirect(reverse_lazy('scxrd:upload_cif_file', ))
        # if 'submit' in request.POST:
        #    form = self.form_class(request.POST)
        #    if form.is_valid():
        #        form.save()
        #        print('The form is valid!!')
        #        return HttpResponseRedirect(reverse_lazy('scxrd:index'))
        return super().post(request, *args, **kwargs)


class ExperimentIndexView(LoginRequiredMixin, TemplateView):
    """
    The view for the main scxrd page.
    """
    model = Experiment
    template_name = 'scxrd/scxrd_index.html'


class ExperimentCreateView(FormActionMixin, LoginRequiredMixin, CreateView):
    """
    Start a new experiment
    """
    model = Experiment
    form_class = ExperimentNewForm
    template_name = 'scxrd/experiment_new.html'
    # Fields are defined in form_class:
    # fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'operator')
    success_url = reverse_lazy('scxrd:index')


class ExperimentEditView(FormActionMixin, LoginRequiredMixin, UpdateView):
    """
    Edit an experiment as Operator.
    """
    model = Experiment
    form_class = ExperimentEditForm
    template_name = 'scxrd/experiment_edit.html'
    success_url = reverse_lazy('scxrd:index')

    '''def form_valid(self, form):
        pprint(form.instance) # instance of current Experiment model
        pprint(self.request.POST) # POST request dictionary
        return super().form_valid(form)'''


class NewExperimentByCustomer(LoginRequiredMixin, CreateView):
    """
    Add a new experiment in order to submit it to the X-ray facility.
    """
    model = SCXRDSample
    template_name = 'scxrd/new_exp_by_customer.html'
    # TODO: Make this the url of the users experiments list later:
    success_url = reverse_lazy('scxrd:index')
    fields = '__all__'


class ResidualsTable(DetailView):
    """
    Show residuals of the in-table selected experiment by ajax request.
    """
    model = Experiment
    template_name = 'scxrd/residuals_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FilesUploadedView(ListView):
    """
    creates a list of the uploaded files for the respective experiment.
    # TODO: This is not used at the moment.
    """
    model = Experiment
    template_name = 'scxrd/uploaded_files.html'


class Customers(LoginRequiredMixin, ListView):
    """
    The customers list view.
    """
    model = Person
    template_name = 'scxrd/customers.html'


class MoleculeView(LoginRequiredMixin, View):
    """
    View to get atom data as .mol file.
    """

    def post(self, request, *args, **kwargs):
        molfile = ''
        print('# Molecule request:')
        pprint(request.POST)
        cif_file = request.POST.get('cif_file')
        exp_id = request.POST.get('experiment_id')
        if not cif_file:
            print('Experiment with id {} has no cif file.'.format(exp_id))
            # Makes structure view blank:
            return HttpResponse(' ')
        cif = CifContainer(Path(MEDIA_ROOT).joinpath(Path(cif_file)))
        grow = request.POST.get('grow')
        if cif.atoms_fract:
            if grow == 'true':
                sdm = SDM(list(cif.atoms_fract), cif.symmops, cif.cell[:6], centric=cif.is_centrosymm)
                try:
                    needsymm = sdm.calc_sdm()
                    atoms = sdm.packer(sdm, needsymm)
                except Exception as e:
                    print('Error in SDM:', e)
                    return HttpResponse(' ')
            else:
                atoms = cif.atoms_orth
            try:
                molfile = MolFile(atoms)
                molfile = molfile.make_mol()
            except (TypeError, KeyError):
                print("Error while writing mol file.")
            return HttpResponse(molfile)
        print('Cif file with id {} of experiment {} has no atoms!'.format(cif_file, exp_id))
        return HttpResponse(' ')

    # always reload complete molecule:
    @never_cache
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ExperimentListJson(BaseDatatableView):
    """
    The view to show the datatabes table for the list of experiments.

    https://datatables.net/
    https://bitbucket.org/pigletto/django-datatables-view-example/
    This implementation is also promising: https://github.com/pivotal-energy-solutions/django-datatable-view
    """
    # The model we're going to show
    model = Experiment
    template_name = 'scxrd/experiment_table.html'
    title = 'Experiments'

    # define the columns that will be returned
    columns = ['id', 'number', 'experiment', 'measure_date', 'machine', 'operator', 'publishable', 'cif_file_on_disk',
               'edit']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', 'number', 'experiment', 'measure_date', 'machine', 'operator', 'publishable',
                     'cif_file_on_disk', '']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500000

    pre_camel_case_notation = False

    def get_filter_method(self):
        return self.FILTER_ICONTAINS

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'publishable':
            if row.publishable:
                return '<span class="badge badge-success ml-1">ok</span>'
            else:
                return '<span class="badge badge-warning ml-1">no</span>'
        if column == 'edit':
            return '<a class="btn-outline-danger m-0 p-1" href=edit/{}>Edit</a>'.format(row.id)
        # I need the id in the table! Therefore I add the check in javascript later.
        # if column == 'cif.id' and row.cif_id:
        #    return """<svg class="bi bi-check" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        #            <path fill-rule="evenodd" d="M13.854 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L6.5 10.293l6.646-6.647a.5.5 0 01.708 0z" clip-rule="evenodd"/>
        #            </svg>"""
        if column == 'measure_date':
            return datetime.strftime(make_naive(row.measure_date), '%d.%m.%Y %H:%M')
        else:
            return super(ExperimentListJson, self).render_column(row, column)
