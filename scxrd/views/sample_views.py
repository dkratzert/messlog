from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, DetailView, DeleteView

from scxrd.forms.new_cust_sample import SubmitNewSampleForm
from scxrd.sample_model import Sample
from scxrd.utils import randstring


class NewSampleByCustomer(LoginRequiredMixin, CreateView):
    """
    Add a new Sample in order to submit it to the X-ray facility.
    """
    model = Sample
    form_class = SubmitNewSampleForm
    template_name = 'scxrd/new_sample_by_customer.html'
    success_url = reverse_lazy('scxrd:index')

    def post(self, request: WSGIRequest, *args, **kwargs) -> WSGIRequest:
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        super().post(request, *args, **kwargs)
        # print('Request from new sample:')
        # pprint(request.POST)
        form = self.get_form()
        if form.is_valid():
            print('NewSample form is valid')
            sample: Sample = form.save(commit=False)
            # Assigns the currently logged in user to the submetted sample:
            sample.customer_samp = request.user
            # Assigns the current date to the sample submission date field
            sample.submit_date = timezone.now()
            sample.save()
            return self.form_valid(form)
        else:
            print('NewSample form is invalid!')
            pprint(form.errors)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # This is for robohash:
        context['randstring'] = randstring()
        return context


class SampleDeleteView(SuccessMessageMixin, DeleteView):
    model = Sample
    template_name = 'scxrd/delete_sample.html'
    success_url = reverse_lazy('scxrd:my_samples_page')
    success_message = 'Your Sample has been deleted successfully.'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(customer_samp=self.request.user)


class MySamplesList(LoginRequiredMixin, ListView):
    """
    The view for the samples list of a customer submitted for measurement by an operator.
    """
    model = Sample
    template_name = 'scxrd/submitted_samples_list_by_customer.html'
    ordering = '-submit_date_samp'

    def get_queryset(self):
        super(MySamplesList, self).get_queryset()
        # Filter by samples owned by the current user:
        return Sample.objects.filter(customer_samp_id=self.request.user)


class OperatorSamplesList(LoginRequiredMixin, ListView):
    """
    The list of all samples submitted by customers.
    """
    model = Sample
    # queryset = Sample.objects.filter(was_measured=False)
    template_name = 'scxrd/submitted_samples_list_operator.html'


class OperatorSampleDetail(LoginRequiredMixin, DetailView):
    model = Sample
    template_name = 'scxrd/sample_details_operator.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['sample'] = Sample.objects.get(pk=pk)
        return context
