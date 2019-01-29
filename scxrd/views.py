import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView
from django_datatables_view.base_datatable_view import BaseDatatableView

from scxrd.cif.mol_file_writer import MolFile
from scxrd.cif_model import SumFormula, Atom
from scxrd.forms import ExperimentEditForm, ExperimentNewForm, FinalizeCifForm
from scxrd.models import Experiment
from scxrd.models import Person
from scxrd.utils import minimal_cif_items


class FormActionMixin():

    def post(self, request, *args, **kwargs):
        """Add 'Cancel' button redirect."""
        if "cancel" in request.POST:
            url = reverse_lazy('scxrd:index')  # or e.g. reverse(self.get_success_url())
            return HttpResponseRedirect(url)
        if 'submit' in request.POST:
            form = self.form_class(request.POST)
            print(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse_lazy('scxrd:index'))
            else:
                print('#### Form is not valid. Use "self.helper.render_unmentioned_fields = True" to see all.')
                return super().post(request, *args, **kwargs)
        else:
            return super().post(request, *args, **kwargs)


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
    # fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'operator')
    success_url = reverse_lazy('scxrd:index')


class ExperimentEditView(LoginRequiredMixin, UpdateView):
    """
    Edit an experiment
    """
    model = Experiment
    form_class = ExperimentEditForm
    template_name = 'scxrd/experiment_edit.html'
    success_url = reverse_lazy('scxrd:index')

    # def get_success_url(self):
    #    return reverse_lazy('scxrd:index')

    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['solvents'] = MyCheckBoxForm()
        except Solvent.DoesNotExist as e:
            print(e, '#')
            pass
        return context"""


class ReportView(LoginRequiredMixin, FormActionMixin, CreateView):
    """
    Generate a report anf finalize the cif.
    """
    model = Experiment
    form_class = FinalizeCifForm
    template_name = 'scxrd/finalize_cif.html'
    success_url = reverse_lazy('scxrd:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            exp_id = self.kwargs['pk']
            cifpath = Experiment.objects.get(pk=exp_id).cif.cif_file_on_disk.path
            context['cifname'] = cifpath
            context['cifdata'] = self.get_cif_data(cifpath)
        except SumFormula.DoesNotExist as e:
            print(e, '#!#')
            pass
        return context

    def get_cif_data(self, cifpath):
        print('foo bar cif')
        import gemmi
        doc = gemmi.cif.read_file(cifpath)
        print(doc.sole_block().name, '#r#r')
        #d = json.loads(doc.as_json())
        #d = d[doc.sole_block().name]
        tocheck = {}
        for x in minimal_cif_items:
            item = doc.sole_block().find_pair(x)
            print('item:', item)
            if item and item[1] in ['?', '.', '']:
                tocheck[x] = item[1]
        # go through all items and check if they are in the minimal items list.
        # This list should be configurable.
        # Display a page where missing items could be resolved. e.g. by uploading more files or
        # by typing informations in forms.
        #for x in d:
        #    print(x)
        #d = doc.sole_block().find_pair('_cell_length_a')
        #print(tocheck)
        return tocheck

    def _diffrn_ambient_temperature(self, value):
        pass
        # Do some stuff to return the appropriate form value


class ExperimentDetailView(LoginRequiredMixin, DetailView):
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
            print(e, '#-#')
            pass
        return context


class UploadView(LoginRequiredMixin, CreateView):
    """
    A file upload view.
    """
    model = Experiment
    template_name = "scxrd/upload.html"
    # success_url = reverse_lazy('scxrd:index')
    form_class = ExperimentEditForm

    def get_success_url(self):
        return reverse_lazy('scxrd:upload', kwargs=dict(pk=self.object.pk))


class DragAndDropUploadView(View):

    def get(self, request):
        photos_list = Photo.objects.all()
        return render(request, 'photos/drag_and_drop_upload/index.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


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


class ExperimentListJson(BaseDatatableView):
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
            return super(ExperimentListJson, self).render_column(row, column)

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
