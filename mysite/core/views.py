from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import CreateView
from django.views.generic.edit import BaseFormView

from scxrd.models import Experiment


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/new_user.html', {'form': form})


class OptionsView(BaseFormView):
    """
    Show details of an experiment

    TODO: Make real options page
    """
    #model = Foo
    template_name = 'registration/options.html'

