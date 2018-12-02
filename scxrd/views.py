from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views import generic

from scxrd.models import Experiment


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
        # <view logic>
        return HttpResponse(Experiment.objects.get(pk=request.url.fragment))


def detail(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk)
    return render(request, 'scxrd/detail.html', {'experiment': experiment})
