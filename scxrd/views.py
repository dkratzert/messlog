from django.http import HttpResponse
from django.views.generic import CreateView, UpdateView
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


class ExperimentUpdateView(UpdateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = 'scxrd/experiment_update_form.html'
    success_url = reverse_lazy('scxrd:index')


class IndexView(generic.ListView):
    template_name = 'scxrd/index.html'
    context_object_name = 'experiment_list'

    queryset = Experiment.objects.all()
    #def get_queryset(self):
    #    """Return the experiments"""
    #    return [x for x in Experiment.objects.all()]


class ExpDetailView(generic.View):
    template_name = 'scxrd/detail.html'
    context_object_name = 'experiment'
    model = Experiment

    def get(self, request):
        return HttpResponse(Experiment.objects.get(pk=request.url.fragment))


def detail(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk)
    return render(request, 'scxrd/detail.html', {'experiment': experiment})
