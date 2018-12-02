from django.shortcuts import render

# Create your views here.
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'scxrd/index.html'
    context_object_name = 'experiment_list'
