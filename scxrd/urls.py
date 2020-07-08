from django.urls import path
from django.views.generic import TemplateView

from mysite.mysite.views import HomePageView
from . import views

app_name = 'scxrd'

urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('submit/mysamples/', views.MySamplesList.as_view(), name='my_samples_page'),
    path('experiments/', views.ExperimentIndexView.as_view(), name='all_experiments'),
    path('newexp/', views.ExperimentCreateView.as_view(), name='new_exp'),
    path('newexp/<int:pk>/', views.ExperimentFromSampleCreateView.as_view(), name='new_exp_from_sample'),
    path('experiments/edit/<int:pk>/', views.ExperimentEditView.as_view(), name='edit-exp'),
    path('submit/', views.NewSampleByCustomer.as_view(), name='submit_sample'),
    path('submit/ketcher.html', TemplateView.as_view(template_name="scxrd/ketcher/ketcher.html")),
    path('operator/allsamples/', views.OperatorSamplesList.as_view(), name='op_samples_page'),
    path('operator/sample_detail/<int:pk>/', views.OperatorSampleDetail.as_view(), name='op_samples_detail'),
    path('experiments/table/<int:pk>/', views.ResidualsTable.as_view(), name='details_table'),
    path('experiments_list/', views.ExperimentListJson.as_view(), name='experiments_list'),
    path('experiments_list_user/', views.ExperimentsListJsonUser.as_view(), name='experiments_list_from_user'),
    path('experiments/molecule/', views.MoleculeView.as_view(), name='molecule'),
    path('submit/library.sdf', TemplateView.as_view(template_name="scxrd/ketcher/library.sdf")),
    path('submit/library.svg', TemplateView.as_view(template_name="scxrd/ketcher/library.svg")),
    path('submit/ketcher.svg', TemplateView.as_view(template_name="scxrd/ketcher/ketcher.svg")),
    # path('uploadcif/<int:pk>/', views.CifUploadView.as_view(), name='upload_cif_file'),

]
