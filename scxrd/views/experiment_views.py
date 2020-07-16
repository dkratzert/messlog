from datetime import datetime
from pprint import pprint

import pytz
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_naive
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, ListView
from django_datatables_view.base_datatable_view import BaseDatatableView

from scxrd.cif.cif_file_io import CifContainer
from scxrd.forms.edit_experiment import ExperimentEditForm
from scxrd.forms.new_exp_from_sample import ExperimentFromSampleForm
from scxrd.forms.new_experiment import ExperimentNewForm
from scxrd.models.cif_model import CifFileModel
from scxrd.models.experiment_model import Measurement
from scxrd.models.models import CheckCifModel, ReportModel
from scxrd.models.sample_model import Sample
from scxrd.utils import generate_sha256


class ExperimentIndexView(LoginRequiredMixin, ListView):
    """
    The view for the main scxrd page.
    """
    model = Measurement
    template_name = 'scxrd/scxrd_index.html'

    def get_context_data(self, **kwargs):
        """Get a list of currently running experiments to the context"""
        exp: Measurement
        utc = pytz.UTC
        mess = []
        for exp in self.object_list:
            if exp.end_time > utc.localize(datetime.now()) > exp.measure_date:
                mess.append(exp)
        kwargs.update({'current_measures': mess})
        return super().get_context_data(**kwargs)


class ExperimentCreateView(LoginRequiredMixin, CreateView):
    """
    Start a new experiment
    """
    model = Measurement
    form_class = ExperimentNewForm
    template_name = 'scxrd/experiment_new.html'
    success_url = reverse_lazy('scxrd:index')

    def form_valid(self, form):
        """Save the current user from the request into the experiment"""
        pprint(form.errors) if form.errors else None
        self.object: Measurement = form.save(commit=False)
        self.object.operator = self.request.user
        if Measurement.objects.first():
            self.object.number = Measurement.objects.first().number + 1
        else:
            self.object.number = 1
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
    model = Sample
    form_class = ExperimentFromSampleForm
    template_name = 'scxrd/experiment_new.html'
    success_url = reverse_lazy('scxrd:index')

    def get_initial(self) -> dict:
        """
        Initial data for the form.
        """
        initial = super().get_initial()
        pk = self.kwargs.get('pk')
        try:
            expnum = Measurement.objects.first().number + 1
        except AttributeError as e:
            expnum = 1
        initial.update({
            'experiment_name'      : Sample.objects.get(pk=pk).sample_name,
            'customer'             : Sample.objects.get(pk=pk).customer_samp_id,
            'number'               : expnum,
            'sum_formula'          : Sample.objects.get(pk=pk).sum_formula,
            'submit_date'          : Sample.objects.get(pk=pk).submit_date,
            'exptl_special_details': Sample.objects.get(pk=pk).special_remarks,
        })
        return initial

    def post(self, request: WSGIRequest, *args, **kwargs) -> WSGIRequest:
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        # print('ExperimentFromSampleCreateView:')
        # pprint(request.POST)
        # self.object is a Sample because of the views model class:
        self.object: Sample = self.get_object()
        if form.instance.final:
            messages.warning(request, 'This Measurement can not be changed anymore!')
            return self.form_invalid(form)
        if form.is_valid():
            # form.instance is Measurement, because of the form class:
            exp: Measurement = form.instance
            # exp.number = form.cleaned_data['number']
            if Measurement.objects.first():
                exp.number = Measurement.objects.first().number + 1
            else:
                exp.number = 1
            exp.experiment_name = form.cleaned_data.get('experiment_name')
            exp.exptl_special_details = form.cleaned_data.get('exptl_special_details')
            exp.customer = self.object.customer_samp
            exp.submit_date = self.object.submit_date
            exp.sum_formula = form.cleaned_data.get('sum_formula')
            exp.crystal_colour = form.cleaned_data.get('crystal_colour')
            exp.measure_date = timezone.now()
            exp.was_measured = not form.cleaned_data.get('was_measured')
            exp.not_measured_cause = form.cleaned_data.get('not_measured_cause')
            exp.conditions = self.object.crystallization_conditions
            # Assigns the currently logged in user to the submitted sample:
            exp.operator = request.user
            # Not needed:
            # self.object.save()
            exp.sample = self.object
            exp.save()
            messages.success(request, _('Saved successfully.'))
            return self.form_valid(form)
        else:
            print('ExperimentFromSampleCreateView is invalid!')
            pprint(request.POST)
            pprint(form.errors)
            messages.warning(request, _('Please correct the errors below.'))
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
    model = Measurement
    form_class = ExperimentEditForm
    template_name = 'scxrd/experiment_edit.html'
    success_url = reverse_lazy('scxrd:all_experiments')

    def get_initial(self) -> dict:
        """
        Initial data for the form.
        """
        pk = self.kwargs.get('pk')
        exp = Measurement.objects.get(pk=pk)
        cif = None
        chk = None
        report = None
        if hasattr(exp, 'ciffilemodel'):
            # noinspection PyUnresolvedReferences
            cif = exp.ciffilemodel.cif_file_on_disk
        if hasattr(exp, 'checkcifmodel'):
            # noinspection PyUnresolvedReferences
            chk = exp.checkcifmodel.checkcif_on_disk
        if hasattr(exp, 'reportmodel'):
            # noinspection PyUnresolvedReferences
            report = exp.reportmodel.reportdoc_on_disk
        return {
            'cif_file_on_disk' : cif,
            'checkcif_on_disk' : chk,
            'reportdoc_on_disk': report,
            'number'           : exp.number,
        }

    def post(self, request: WSGIRequest, *args, **kwargs) -> WSGIRequest:
        # print('request from new measurement:')
        # pprint(request.POST)
        self.object: Measurement = self.get_object()
        # This is here, because I dont want the number field to be rendered:
        request.POST._mutable = True
        request.POST['number'] = self.object.number
        request.POST._mutable = False
        sample = self.object.sample
        final = self.object.final
        form: ExperimentEditForm = self.get_form()
        if final:
            messages.warning(request, _('This Measurement can not be changed anymore!'))
            print('This Measurement can not be changed anymore!')
            return self.form_invalid(form)
        if form.is_valid():
            print('Form is valid')
            exp: Measurement = form.save(commit=False)
            # Otherwise sample id gets lost: why?
            exp.sample = sample
            if form.cleaned_data.get('final'):
                if self.all_files_there(form):
                    exp.final = form.cleaned_data.get('final')
                else:
                    messages.warning(request,
                                     _('You can only finalize an experiment with a CIF, report and checkcif file!'))
                    return self.form_invalid(form)
            exp.operator = request.user
            if request.POST.get('cif_file_on_disk-clear'):
                exp.ciffilemodel.delete()
            if request.POST.get('checkcif_on_disk-clear'):
                exp.checkcifmodel.delete()
            if request.POST.get('reportdoc_on_disk-clear'):
                exp.reportmodel.delete()
            if form.files.get('cif_file_on_disk'):
                self.prepare_cif_file_model(exp, form)
            if form.files.get('checkcif_on_disk'):
                self.handle_checkcif_file(exp, form)
            if form.files.get('reportdoc_on_disk'):
                self.handle_report_file(exp, form)
            exp.save()
            messages.success(request, _('Saved successfully.'))
            print('Measurement {} saved.'.format(exp.experiment_name))
            return self.form_valid(form)
        else:
            print('Form is invalid! Invalid forms:')
            pprint(form.errors)
            messages.warning(request, _('Please correct the errors below.'))
            return self.form_invalid(form)

    def handle_checkcif_file(self, exp, form):
        if hasattr(exp, 'checkcifmodel') and exp.checkcifmodel.chkcif_exists:
            exp.checkcifmodel.delete()
        chk = CheckCifModel()
        chk.checkcif_on_disk = form.files.get('checkcif_on_disk')
        exp.checkcifmodel = chk
        chk.save()

    def handle_report_file(self, exp, form):
        if hasattr(exp, 'reportmodel') and exp.reportmodel.report_exists:
            exp.reportmodel.delete()
        rep = ReportModel()
        rep.reportdoc_on_disk = form.files.get('reportdoc_on_disk')
        exp.reportmodel = rep
        rep.save()

    def prepare_cif_file_model(self, exp, form):
        if hasattr(exp, 'ciffilemodel') and exp.ciffilemodel.cif_exists:
            exp.ciffilemodel.delete()
        cif_file = form.files['cif_file_on_disk']
        cif_model = CifFileModel()
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
        cif_model.save()

    def all_files_there(self, form: ExperimentEditForm) -> bool:
        if form.cleaned_data.get('cif_file_on_disk') \
                and form.cleaned_data.get('checkcif_on_disk') \
                and form.cleaned_data.get('reportdoc_on_disk'):
            return True
        else:
            return False



class ExperimentListJson(LoginRequiredMixin, BaseDatatableView):
    """
    The view to show the datatabes table for the list of experiments.

    https://datatables.net/
    https://bitbucket.org/pigletto/django-datatables-view-example/
    This implementation is also promising: https://github.com/pivotal-energy-solutions/django-datatable-view
    """
    # The model we're going to show
    model = Measurement
    template_name = 'scxrd/experiment_all_table.html'
    title = _('Experiments')

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
            return '<a class="btn-outline-danger m-0 p-1" href=edit/{}>{}</a>'.format(row.id, _('Edit'))
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
        qs = super().filter_queryset(qs)
        return qs.filter(Q(operator=User.objects.get(username=self.user)))
