from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView
from django_datatables_view.base_datatable_view import BaseDatatableView

from scxrd.models import Person
from scxrd.cif.mol_file_writer import MolFile
from scxrd.cif_model import SumFormula, Atom
from scxrd.forms import ExperimentForm, ExperimentnewForm
from scxrd.models import Experiment


class FormActionMixin(object):

    def post(self, request, *args, **kwargs):
        """Add 'Cancel' button redirect."""
        if "cancel" in request.POST:
            url = reverse_lazy('scxrd:index')  # or e.g. reverse(self.get_success_url())
            return HttpResponseRedirect(url)
        if 'submit' in request.POST:
            form = ExperimentnewForm(request.POST)
            print(form.is_valid(), '####')
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse_lazy('scxrd:index'))
            else:
                return super(FormActionMixin, self).post(request, *args, **kwargs)
        else:
            return super(FormActionMixin, self).post(request, *args, **kwargs)


class ExperimentIndexView(TemplateView):
    """
    The view for the main scxrd page.
    """
    model = Experiment
    template_name = 'scxrd/scxrd_index.html'


class ExperimentCreateView(CreateView):
    """
    Start a new experiment
    """
    model = Experiment
    form_class = ExperimentForm
    template_name = 'scxrd/new_experiment.html'
    # Fields are defined in form_class:
    # fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'operator')
    success_url = reverse_lazy('scxrd:index')


class ExperimentEditView(LoginRequiredMixin, FormActionMixin, UpdateView):
    """
    Edit an experiment
    """
    model = Experiment
    form_class = ExperimentnewForm
    template_name = 'scxrd/experiment_edit.html'
    success_url = reverse_lazy('scxrd:index')

    def get_success_url(self):
        return reverse_lazy('scxrd:index')

    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['solvents'] = MyCheckBoxForm()
        except Solvent.DoesNotExist as e:
            print(e, '#')
            pass
        return context"""


class ExperimentDetailView(DetailView):
    """
    Show details of an experiment
    """
    model = Experiment
    template_name = 'scxrd/experiment_detail.html'


class DetailsTable(DetailView):
    """
    Show rediduals of the in-table selected experiment by ajax request.
    """
    model = Experiment
    template_name = 'scxrd/residuals_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            exp_id = self.kwargs['pk']
            context['sumform'] = SumFormula.objects.get(pk=exp_id)
        except SumFormula.DoesNotExist as e:
            print(e, '#')
            pass
        return context


class UploadView(CreateView):
    """
    An file upload view.
    """
    model = Experiment
    template_name = "scxrd/upload.html"
    # success_url = reverse_lazy('scxrd:index')
    form_class = ExperimentForm

    def get_success_url(self):
        return reverse_lazy('scxrd:upload', kwargs=dict(pk=self.object.pk))


class Customers(ListView):
    """
    The customers list view.
    """
    model = Person
    template_name = 'scxrd/customers.html'


class MoleculeView(View):
    """
    View to get atom data as .mol file.
    """

    def post(self, request, *args, **kwargs):
        molfile = ''
        atoms = None
        cif_id = request.POST.get('cif_id')
        if cif_id:
            atoms = Atom.objects.all().filter(cif_id=cif_id)
        if atoms:
            grow = request.POST.get('grow')
            if grow:
                # Grow atoms here
                pass
            try:
                m = MolFile(atoms)
                molfile = m.make_mol()
            except(KeyError, TypeError) as e:
                print('Exception in jsmol_request: {}'.format(e))
        return HttpResponse(molfile)

    # alsways reload complete molecule:
    @never_cache
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OrderListJson(BaseDatatableView):
    """
    The view to show the datatabes table for the list of experiments.

    https://datatables.net/
    https://bitbucket.org/pigletto/django-datatables-view-example/
    """
    # The model we're going to show
    model = Experiment
    template_name = 'scxrd/experiment_table.html'

    # define the columns that will be returned
    columns = ['id', 'cif_id', 'number', 'experiment', 'measure_date', 'machine', 'operator', 'publishable']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', '', 'number', 'experiment', 'measure_date', 'machine', 'operator', 'publishable']

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
                return '<span class="badge badge-success ml-4">ok</span>'
            else:
                return '<span class="badge badge-warning ml-4">no</span>'
        else:
            return super(OrderListJson, self).render_column(row, column)

    '''
    def filter_queryset(self, qs):
        """ If search['value'] is provided then filter all searchable columns using filter_method (istartswith
            by default).

            Automatic filtering only works for Datatables 1.10+. For older versions override this method
        """
        columns = self._columns
        if not self.pre_camel_case_notation:
            # get global search value
            search = self._querydict.get('search[value]', None)
            q = Q()
            filter_method = self.get_filter_method()
            for col_no, col in enumerate(self.columns_data):
                print(col_no, col, '##')
                # apply global search to all searchable columns
                if search and col['searchable']:
                    q |= Q(**{'{0}__{1}'.format(columns[col_no].replace('.', '__'), filter_method): search})
                    print(search, '######')
                # column specific filter
                if col['search.value']:
                    qs = qs.filter(**{
                        '{0}__{1}'.format(columns[col_no].replace('.', '__'), filter_method): col['search.value']})
            qs = qs.filter(q)
        return qs
    '''
