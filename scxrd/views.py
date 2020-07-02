from datetime import datetime
from pathlib import Path
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_naive
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django_robohash.robotmaker import make_robot_svg

from mysite.settings import MEDIA_ROOT
from scxrd.cif.cif_file_io import CifContainer
from scxrd.cif.mol_file_writer import MolFile
from scxrd.cif.sdm import SDM
from scxrd.cif_model import CifFileModel
from scxrd.customer_models import SCXRDSample
from scxrd.forms.edit_experiment import ExperimentEditForm
from scxrd.forms.new_cust_sample import SubmitNewForm
from scxrd.forms.new_exp_from_sample import ExperimentFromSampleForm
from scxrd.forms.new_experiment import ExperimentNewForm
from scxrd.models import Experiment
from scxrd.utils import randstring, generate_sha256


class ExperimentIndexView(LoginRequiredMixin, TemplateView):
    """
    The view for the main scxrd page.
    """
    model = Experiment
    template_name = 'scxrd/scxrd_index.html'


class ExperimentCreateView(LoginRequiredMixin, CreateView):
    """
    Start a new experiment
    """
    model = Experiment
    form_class = ExperimentNewForm
    template_name = 'scxrd/experiment_new.html'
    # Fields are defined in form_class:
    # fields = ('experiment_name', 'number', 'measure_date', 'machine', 'sum_formula', 'operator')
    success_url = reverse_lazy('scxrd:index')

    def form_valid(self, form):
        """Save the current user from the request into the experiment"""
        self.object: Experiment = form.save(commit=False)
        self.object.operator = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Add current user to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ExperimentFromSampleCreateView(LoginRequiredMixin, UpdateView):
    """
    Start a new experiment from a prior sample. The experiment gets as much data from the sample submission
    form of the customer as possible.
    """
    model = SCXRDSample
    form_class = ExperimentFromSampleForm
    template_name = 'scxrd/experiment_new.html'
    # Fields are defined in form_class:
    # fields = ('experiment_name', 'number', 'measure_date', 'machine', 'sum_formula', 'operator')
    success_url = reverse_lazy('scxrd:index')

    def get_initial(self) -> dict:
        """
        Initial data for the form.
        """
        initial = super().get_initial()
        pk = self.kwargs.get('pk')
        try:
            expnum = Experiment.objects.first().number + 1
        except AttributeError as e:
            expnum = 1
        initial.update({
            'experiment_name': SCXRDSample.objects.get(pk=pk).sample_name_samp,
            'customer': SCXRDSample.objects.get(pk=pk).customer_samp_id,
            'number': expnum,
            'sum_formula': SCXRDSample.objects.get(pk=pk).sum_formula_samp,
            'submit_date': SCXRDSample.objects.get(pk=pk).submit_date_samp,
            'exptl_special_details': SCXRDSample.objects.get(pk=pk).special_remarks_samp,
        })
        return initial

    def post(self, request: WSGIRequest, *args, **kwargs) -> WSGIRequest:
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        pprint(request.POST)
        # self.object is an SCXRDSample because of the views model class:
        self.object: SCXRDSample = self.get_object()
        if form.is_valid():
            # form.instance is Experiment, because of the form class:
            exp: Experiment = form.instance
            exp.number = form.cleaned_data['number']
            exp.experiment_name = form.cleaned_data.get('experiment_name')
            exp.exptl_special_details = form.cleaned_data.get('exptl_special_details')
            # TODO: is form.cleaned_data.get('customer') sufficient?
            exp.customer = User.objects.get(pk=form.cleaned_data.get('customer').pk)
            exp.submit_date_samp = form.cleaned_data.get('submit_date')
            exp.sum_formula = form.cleaned_data.get('sum_formula')
            exp.crystal_colour = form.cleaned_data.get('crystal_colour')
            exp.measure_date = timezone.now()
            exp.was_measured = not form.cleaned_data.get('was_measured')
            exp.not_measured_cause = form.cleaned_data.get('not_measured_cause')
            exp.conditions = form.cleaned_data.get('crystal_cond_samp')
            # Assigns the currently logged in user to the submitted sample:
            exp.operator = request.user
            self.object.save()
            exp.sample = self.object
            exp.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self) -> dict:
        """Add current user to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ExperimentEditView(LoginRequiredMixin, UpdateView):
    """
    Edit an experiment as Operator.
    """
    model = Experiment
    form_class = ExperimentEditForm
    template_name = 'scxrd/experiment_edit.html'
    success_url = reverse_lazy('scxrd:all_experiments')

    def get_initial(self) -> dict:
        """
        Initial data for the form.
        """
        pk = self.kwargs.get('pk')
        exp = Experiment.objects.get(pk=pk)
        cif = None
        if hasattr(exp, 'ciffilemodel'):
            # noinspection PyUnresolvedReferences
            cif = exp.ciffilemodel.cif_file_on_disk
        return {
            'cif_file_on_disk': cif,
        }

    def post(self, request: WSGIRequest, *args, **kwargs) -> WSGIRequest:
        print('request from new measurement:')
        pprint(request.POST)
        self.object = self.get_object()
        form: ExperimentEditForm = self.get_form()
        if form.is_valid():
            cif_model = CifFileModel()
            exp: Experiment = form.save(commit=False)
            exp.operator = request.user
            if request.POST.get('cif_file_on_disk-clear'):
                exp.ciffilemodel.delete()
            if form.files.get('cif_file_on_disk'):
                if hasattr(exp, 'ciffilemodel') and exp.ciffilemodel.cif_exists():
                    exp.ciffilemodel.delete()
                cif_file = form.files['cif_file_on_disk']
                try:
                    cif = CifContainer(
                        chunks='\n'.join([x.decode(encoding='cp1250', errors='ignore') for x in cif_file.chunks()]))
                    cif_model.fill_residuals_table(cif)
                except Exception as e:
                    print('Error during CIF parsing:', e)
                    # TODO: handle bad cif parsing
                cif_model.cif_file_on_disk = cif_file
                cif_model.sha256 = generate_sha256(cif_file)
                cif_model.filesize = cif_file.size
                if not cif_model.date_created:
                    cif_model.date_created = timezone.now()
                cif_model.date_updated = timezone.now()
                exp.ciffilemodel = cif_model
            exp.save()
            if form.files.get('cif_file_on_disk'):
                cif_model.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class NewSampleByCustomer(LoginRequiredMixin, CreateView):
    """
    Add a new SCXRDSample in order to submit it to the X-ray facility.
    """
    model = SCXRDSample
    form_class = SubmitNewForm
    template_name = 'scxrd/new_sample_by_customer.html'
    success_url = reverse_lazy('scxrd:index')

    def post(self, request: WSGIRequest, *args, **kwargs) -> WSGIRequest:
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        super().post(request, *args, **kwargs)
        print('request from new sample:')
        pprint(request.POST)
        form = self.get_form()
        if form.is_valid():
            sample = form.save(commit=False)
            # Assigns the currently logged in user to the submetted sample:
            sample.customer_samp = request.user
            # Assigns the current date to the sample submission date field
            sample.submit_date_samp = timezone.now()
            sample.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['randstring'] = randstring()
        return context


class MySamplesList(LoginRequiredMixin, ListView):
    """
    The view for the samples list of a customer submitted for measurement by an operator.
    """
    model = SCXRDSample
    template_name = 'scxrd/submitted_samples_list_by_customer.html'
    ordering = '-submit_date_samp'

    def get_queryset(self):
        super(MySamplesList, self).get_queryset()
        return SCXRDSample.objects.filter(customer_samp_id=self.request.user)


class OperatorSamplesList(LoginRequiredMixin, ListView):
    """
    The list of all samples submitted by customers.
    """
    model = SCXRDSample
    # queryset = SCXRDSample.objects.filter(was_measured=False)
    template_name = 'scxrd/submitted_samples_list_operator.html'

    '''def get_queryset(self):
        """Returns as default the unmeasured samples context."""
        filter_val = self.request.GET.get('filter', 'False')
        new_context = SCXRDSample.objects.all()#filter(experiments__was_measured=filter_val)
        return new_context

    def get_context_data(self, **kwargs):
        # TODO: I should use a cookie for the state
        context = super().get_context_data(**kwargs)
        context['filterstate'] = False
        return context'''


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


class MoleculeView(LoginRequiredMixin, View):
    """
    View to get atom data as .mol file.
    """

    def post(self, request: WSGIRequest, *args, **kwargs):
        print('# Molecule request:')
        pprint(request.POST)
        # TODO: use cleaned data:
        cif_file = request.POST.get('cif_file')
        exp_id = request.POST.get('experiment_id')
        if not cif_file:
            print('Experiment with id {} has no cif file.'.format(exp_id))
            # Show a robot where no cif is found:
            robot = make_robot_svg(randstring(), width=300, height=300)
            return HttpResponse(robot[1:])
        grow = request.POST.get('grow')
        cif = CifContainer(Path(MEDIA_ROOT).joinpath(Path(cif_file)))
        if cif.atoms_fract:
            return HttpResponse(self.make_molfile(cif, grow))
        print('Cif file with id {} of experiment_name {} has no atoms!'.format(cif_file, exp_id))
        return HttpResponse('')

    def make_molfile(self, cif: CifContainer, grow: str) -> str:
        """
        Returns a mol file with the molecule from the CIF file.
        :param cif: The CIF object
        :param grow: wheather to grow or not
        :return: molfile string
        """
        molfile = ' '
        if grow == 'true':
            sdm = SDM(list(cif.atoms_fract), cif.symmops, cif.cell[:6], centric=cif.is_centrosymm)
            try:
                needsymm = sdm.calc_sdm()
                atoms = sdm.packer(sdm, needsymm)
            except Exception as e:
                print('Error in SDM:', e)
                return molfile
        else:
            atoms = cif.atoms_orth
        try:
            molfile = MolFile(atoms)
            molfile = molfile.make_mol()
        except (TypeError, KeyError):
            print("Error while writing mol file.")
        return molfile

    # always reload complete molecule:
    @never_cache
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ExperimentListJson(LoginRequiredMixin, BaseDatatableView):
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
    columns = ['id', 'number', 'experiment_name', 'measure_date', 'machine', 'operator', 'publishable', 'ciffilemodel',
               'edit']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', 'number', 'experiment_name', 'measure_date', 'machine', 'operator', 'publishable',
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


class ExperimentsListJsonUser(ExperimentListJson):

    def get(self, request, *args, **kwargs):
        self.user = request.user.username
        return super().get(request, *args, **kwargs)

    def filter_queryset(self, qs):
        """Get only experiment from current user"""
        return qs.filter(Q(operator=User.objects.get(username=self.user)))
