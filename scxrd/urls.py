from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'scxrd'

urlpatterns = [
    path('', views.ExperimentIndexView.as_view(), name='index'),
    path('new/', views.ExperimentCreateView.as_view(), name='new'),
    path('edit/<int:pk>/', views.ExperimentEditView.as_view(), name='edit'),
    path('submit/', views.NewExperimentByCustomer.as_view(), name='submit_experiment'),
    # path('submit/ketcher.html', TemplateView.as_view(template_name="scxrd/ketcher.html")),
    path('submit/ketcher.html', TemplateView.as_view(template_name="scxrd/ketcher/ketcher.html")),
    path('submit/library.sdf', TemplateView.as_view(template_name="scxrd/ketcher/library.sdf")),
    path('submit/ketcher.svg', TemplateView.as_view(template_name="scxrd/ketcher/ketcher.svg")),
    path('table/<int:pk>/', views.ResidualsTable.as_view(), name='details_table'),
    path('experiments_list/', views.ExperimentListJson.as_view(), name='experiments_list'),
    path('customers/', views.Customers.as_view(), name='customers'),
    path('molecule/', views.MoleculeView.as_view(), name='molecule'),
    # path('uploadcif/<int:pk>/', views.CifUploadView.as_view(), name='upload_cif_file'),

]
