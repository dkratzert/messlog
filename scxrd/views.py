from django.http import HttpResponse
from django.views.generic import CreateView, UpdateView, DetailView
from django.shortcuts import render, get_object_or_404
from scxrd.forms import ExperimentForm
from django.urls import reverse_lazy

# Create your views here.
from django.views import generic

from scxrd.models import Experiment


class ExperimentCreateView(CreateView):
    model = Experiment
    fields = ('experiment', 'number', 'measure_date', 'machine', 'sum_formula', 'owner')
    success_url = reverse_lazy('scxrd:index')


class ExperimentEditView(UpdateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = 'scxrd/experiment_edit_form.html'
    success_url = reverse_lazy('scxrd:index')


class ExperimentShowView(DetailView):
    model = Experiment
    template_name = 'scxrd/experiment_detail.html'


class IndexView(generic.ListView):
    template_name = 'scxrd/index.html'
    context_object_name = 'experiment_list'
    queryset = Experiment.objects.all()

