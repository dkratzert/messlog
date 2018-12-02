from django.shortcuts import render

# Create your views here.
from django.views import generic

from scxrd.models import Experiment


class IndexView(generic.ListView):
    template_name = 'scxrd/index.html'
    context_object_name = 'experiment_list'

    def get_queryset(self):
        """Return the experiments"""
        return [x for x in Experiment.objects.all()]


