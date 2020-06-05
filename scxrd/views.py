from datetime import datetime
from pathlib import Path
from pprint import pprint

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
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
from scxrd.cif_model import CifFileModel
from scxrd.forms import ExperimentEditForm, ExperimentNewForm, CifForm
from scxrd.models import Experiment
from scxrd.models import Person


class CifUploadView(LoginRequiredMixin, CreateView):
    model = Experiment
    form_class = CifForm
    template_name = 'scxrd/cif_file_upload.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        #self.success_url = reverse_lazy('scxrd:edit', self.kwargs['pk'])
        exp_id = self.kwargs['pk']
        exp = Experiment.objects.get(pk=exp_id)
        context['ciffile'] = exp.cif
        context['experiment'] = exp
        context['pk'] = exp_id
        return context

    def get_success_url(self, **kwargs):
        # obj = form.instance or self.object
        return reverse_lazy("scxrd:upload_cif_file", kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        form = CifForm(self.request.POST, self.request.FILES)
        pprint(self.request.POST)
        pprint(self.request.FILES)
        pprint(args)
        pprint(kwargs)

        if form.is_valid():
            #ciffile = form.save()
            #self.model.cif.cif_file_on_disk = ciffile
            cifdoc = CifFileModel(cif_file_on_disk=request.FILES['cif_file_on_disk'])
            cifdoc.save()
            exp = Experiment.objects.get(pk=self.kwargs['pk'])
            exp.cif = cifdoc
            exp.save(update_fields=['cif'])
            if not exp.cif.pk:
                messages.warning(request, 'That cif file was invalid.')
                # try:
                #    ciffile.delete()
                # except Exception as e:
                #    print('can not delete file:', e)
            # data = {'is_valid': True, 'name': ciffile.cif_file_on_disk.name, 'url': ciffile.cif_file_on_disk.url}
        else:
            # data = {'is_valid': False}
            messages.warning(request, 'That cif file was invalid.')
        # return JsonResponse(data)  # for js upload
        return super(CifUploadView, self).post(request, *args, **kwargs)


class FormActionMixin(LoginRequiredMixin, FormMixin):

    def post(self, request, *args, **kwargs):
        """Add 'Cancel' button redirect."""
        print('The post request:')
        pprint(request.POST)
        print('end request ----------------')
        if "cancel" in request.POST:
            url = reverse_lazy('scxrd:index')  # or e.g. reverse(self.get_success_url())
            return HttpResponseRedirect(url)
        if 'upload_cif' in request.POST:
            return HttpResponseRedirect(reverse_lazy('scxrd:upload_cif_file', ))
        if 'submit' in request.POST:
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                print('The form is valid!!')
                return HttpResponseRedirect(reverse_lazy('scxrd:index'))
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


class ExperimentEditView(FormActionMixin, LoginRequiredMixin, UpdateView):
    """
    Edit an experiment
    """
    model = Experiment
    form_class = ExperimentEditForm
    template_name = 'scxrd/experiment_edit.html'
    success_url = reverse_lazy('scxrd:index')

    # def get_success_url(self):
    #    return reverse_lazy('scxrd:index')

    """def get_context_data(self, **kwargs):
        #exp = Experiment.objects.get(pk=self.kwargs['pk'])
        #cifid = exp.cif_id
        context = super().get_context_data(**kwargs)
        exp_id = self.kwargs['pk']
        # print('#edit#', exp_id, '###')
        context['expid'] = exp_id
        #context['ciffile'] = exp.cif_file_on_disk
        #state = exp.save(update_fields=["cif"])
        #print('state:', state, cifid)
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        file = request.FILES.get('upload_cif')
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)"""


class ExperimentDetailView(LoginRequiredMixin, DetailView):
    """
    Show details of an experiment
    """
    model = Experiment
    template_name = 'scxrd/unused/experiment_detail.html'


class DetailsTable(DetailView):
    """
    Show rediduals of the in-table selected experiment by ajax request.
    """
    model = Experiment
    template_name = 'scxrd/residuals_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


'''
class DeleteView(LoginRequiredMixin, CreateView):
    """
    A file upload view.
    """
    model = Experiment
    # template_name = "scxrd/upload.html"
    # success_url = reverse_lazy('scxrd:index')
    # form_class = ExperimentEditForm

    """def delete_file(self, pk):
        document = self.model.objects.get(pk)
        document.delete()
        os.remove(os.path.join(settings.MEDIA_ROOT, self.docfile.name))"""

    def get_success_url(self):
        return reverse_lazy('scxrd:upload', kwargs=dict(pk=self.object.pk))
'''


class DragAndDropUploadView(DetailView):
    model = Experiment
    template_name = 'scxrd/unused/drag_drop_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # exp_id = self.kwargs['pk']
        # context['ciffile'] = CifFileModel.objects.get(pk=exp_id)
        return context

    def post(self, request, *args, **kwargs):
        form = CifForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            ciffile = form.save()
            data = {'is_valid': True, 'name': ciffile.cif_file_on_disk.name, 'url': ciffile.cif_file_on_disk.url}
        else:
            data = {'is_valid': False}
            # messages.warning(request, 'Please correct the error below.')
        return JsonResponse(data)


class FilesUploadedView(ListView):
    """
    creates a list of the uploaded files fore the respective experiment.
    """
    model = Experiment
    template_name = 'scxrd/uploaded_files.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exp_id = self.kwargs['pk']
        print(exp_id, '###')
        exp = Experiment.objects.get(pk=exp_id)
        context['ciffile'] = exp.cif_file_on_disk
        return context


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
    columns = ['id', 'number', 'experiment', 'measure_date', 'machine', 'operator', 'publishable', 'cif_file_on_disk', 'edit']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', 'number', 'experiment', 'measure_date', 'machine', 'operator', 'publishable', 'cif_file_on_disk', '']

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
