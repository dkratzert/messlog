from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView
from django_datatables_view.base_datatable_view import BaseDatatableView

from scxrd.cif.mol_file_writer import MolFile
from scxrd.cif_model import SumFormula, Atom
from scxrd.datafiles.sadabs_model import SadabsModel
from scxrd.forms import ExperimentEditForm, ExperimentNewForm, SadabsForm, CifForm
from scxrd.models import Experiment
from scxrd.models import Person


class CifUploadView(LoginRequiredMixin, CreateView):
    model = Experiment
    form_class = CifForm
    # success_url = reverse_lazy('scxrd:edit', self.kwargs['pk'])
    template_name = 'scxrd/file_upload.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        exp_id = self.kwargs['pk']
        print(exp_id, '###')
        exp = Experiment.objects.get(pk=exp_id)
        context['absfile'] = exp.absfile
        context['ciffile'] = exp.cif
        context['experiment'] = exp
        context['pk'] = exp_id
        return context

    def get_success_url(self, **kwargs):
        # obj = form.instance or self.object
        return reverse_lazy("scxrd:upload_cif_file", kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        form = CifForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            ciffile = form.save()
            # self.model.cif.cif_file_on_disk = ciffile
            print('exp pk is:', self.kwargs['pk'])
            print('cif pk is:', ciffile.pk, ciffile.cif_file_on_disk.url)
            #exp = Experiment.objects.get(pk=self.kwargs['pk'])
            #exp.cif_id = ciffile.pk
            #state = exp.save(update_fields=['cif_id'])
            #print('cif worked?', state)
            if not ciffile.pk:
                messages.warning(request, 'That cif file was invalid.')
                try:
                    ciffile.delete()
                except Exception:
                    pass
            # data = {'is_valid': True, 'name': ciffile.cif_file_on_disk.name, 'url': ciffile.cif_file_on_disk.url}
        else:
            # data = {'is_valid': False}
            messages.warning(request, 'That cif file was invalid.')
        # return JsonResponse(data)  # for js upload
        return super(CifUploadView, self).post(request, *args, **kwargs)


'''
class FormActionMixin(LoginRequiredMixin, FormMixin):

    def post(self, request, *args, **kwargs):
        """Add 'Cancel' button redirect."""
        print('The post request:')
        pprint(request.POST)
        print('end request ----------------')
        if "cancel" in request.POST:
            url = reverse_lazy('scxrd:index')  # or e.g. reverse(self.get_success_url())
            return HttpResponseRedirect(url)
        if 'submit' in request.POST:
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                print('The form is valid!!')
                return HttpResponseRedirect(reverse_lazy('scxrd:index'))
            else:
                print('#### Form is not valid. Use "self.helper.render_unmentioned_fields = True" to see all.')
                return super().post(request, *args, **kwargs)
        else:
            print('else reached')
            return super().post(request, *args, **kwargs)
'''


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

    def get_context_data(self, **kwargs):
        exp = Experiment.objects.get(pk=self.kwargs['pk'])
        cifid = exp.cif_id
        context = super().get_context_data(**kwargs)
        exp_id = self.kwargs['pk']
        print('#edit#', exp_id, '###')
        context['expid'] = exp_id
        context['absfile'] = exp.absfile
        context['ciffile'] = exp.cif
        # This tries to preserve the cif id, but somewhere it gets deleted during save()
        state = exp.save(update_fields=["cif"])
        print('state:', state, cifid)
        return context


'''
class ReportView(LoginRequiredMixin, FormActionMixin, UpdateView):
    """
    Generate a report anf finalize the cif.

    - Informationsfluss muss sein: Die Datenbank wird editiert und mit dem cif abgegelichen, d.h das Formular
      von Experiment entscheidet was im cif steht. d.h. auch beim cif upload wird die Information die schon
      im Experiment ist in das cif geschrieben! z.B. Kristallgröße
    - Später kommt villeicht noch eine Abfrage bei Konflikten.
    - Also brauche ich: für jedes item in Experiment.ciffile: schreibe value in cif.
    - Übersetzungsfunktion von cifnahmen in Datenbankfeldnahmen. Also doch alle Felder in die Datenbank!

    """
    model = Experiment
    form_class = FinalizeCifForm
    template_name = 'scxrd/finalize_cif.html'
    success_url = reverse_lazy('scxrd:index')

    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            exp_id = self.kwargs['pk']
            cifpath = Experiment.objects.get(number=exp_id).cif.cif_file_on_disk.path
            context['cifname'] = cifpath
            context['cifdata'] = self.get_cif_data(cifpath)
        except SumFormula.DoesNotExist as e:
            print(e, '#!#')
            pass
        return context"""

    def get_cif_data(self, cifpath):
        print('get_cif_data():')
        import gemmi
        doc = gemmi.cif.read_file(cifpath)
        # print(doc.sole_block().name, '#r#r')
        # d = json.loads(doc.as_json())
        # d = d[doc.sole_block().name]
        tocheck = {}
        print('minimal_cif_items: -----')
        for x in minimal_cif_items:
            item = doc.sole_block().find_pair(x)
            print('item:', item)
            if item and item[1] in ['?', '.', '']:
                tocheck[x.lstrip('_')] = item[1]
        print('tocheck:', tocheck)
        # go through all items and check if they are in the minimal items list.
        # This list should be configurable.
        # Display a page where missing items could be resolved. e.g. by uploading more files or
        # by typing informations in forms.
        # for x in d:
        #    print(x)
        # d = doc.sole_block().find_pair('_cell_length_a')
        # print(tocheck)
        return tocheck

    def _diffrn_ambient_temperature(self, value):
        pass
        # Do some stuff to return the appropriate form value
'''


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
            print(e, '#-DetailsTable view #')
            pass
        return context


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


class DragAndDropUploadView(DetailView):
    model = Experiment
    template_name = 'scxrd/drag_drop_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exp_id = self.kwargs['pk']
        context['absfiles'] = SadabsModel.objects.get(pk=exp_id)
        return context

    def post(self, request, *args, **kwargs):
        form = SadabsForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            absfile = form.save()
            data = {'is_valid': True, 'name': absfile.abs_file.name, 'url': absfile.abs_file.url}
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
        context['absfile'] = exp.absfile
        context['ciffile'] = exp.cif
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
