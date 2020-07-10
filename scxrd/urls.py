from django.urls import path
from django.views.generic import TemplateView

from mysite.mysite.views import HomePageView
from scxrd.views.experiment_views import ExperimentIndexView, ExperimentCreateView, ExperimentFromSampleCreateView, \
    ExperimentEditView, ExperimentListJson, ExperimentsListJsonUser
from scxrd.views.sample_views import MySamplesList, NewSampleByCustomer, OperatorSamplesList, SampleDeleteView, \
    OperatorSampleDetail
from scxrd.views.views import ResidualsTable, MoleculeView

app_name = 'scxrd'

urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('experiments/', ExperimentIndexView.as_view(), name='all_experiments'),
    path('newexp/', ExperimentCreateView.as_view(), name='new_exp'),
    path('newexp/<int:pk>/', ExperimentFromSampleCreateView.as_view(), name='new_exp_from_sample'),
    path('experiments/edit/<int:pk>/', ExperimentEditView.as_view(), name='edit-exp'),

    path('submit/mysamples/', MySamplesList.as_view(), name='my_samples_page'),
    path('operator/allsamples/', OperatorSamplesList.as_view(), name='op_samples_page'),
    path('sample/submit/', NewSampleByCustomer.as_view(), name='submit_sample'),
    path('sample/delete/<int:pk>', SampleDeleteView.as_view(), name='delete_sample'),
    path('sample/submit/ketcher.html', TemplateView.as_view(template_name="scxrd/ketcher/ketcher.html")),
    path('operator/sample_detail/<int:pk>/', OperatorSampleDetail.as_view(), name='op_samples_detail'),

    path('experiments/table/<int:pk>/', ResidualsTable.as_view(), name='details_table'),
    path('experiments_list/', ExperimentListJson.as_view(), name='experiments_list'),
    path('experiments_list_user/', ExperimentsListJsonUser.as_view(), name='experiments_list_from_user'),
    path('experiments/molecule/', MoleculeView.as_view(), name='molecule'),
    path('sample/submit/library.sdf', TemplateView.as_view(template_name="scxrd/ketcher/library.sdf")),
    path('sample/submit/library.svg', TemplateView.as_view(template_name="scxrd/ketcher/library.svg")),
    path('sample/submit/ketcher.svg', TemplateView.as_view(template_name="scxrd/ketcher/ketcher.svg")),
    # path('uploadcif/<int:pk>/', views.CifUploadView.as_view(), name='upload_cif_file'),

]
