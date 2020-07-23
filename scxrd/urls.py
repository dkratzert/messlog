from django.urls import path
from django.views.generic import TemplateView

from mysite.mysite.views import HomePageView
from scxrd.views.measurement_views import MeasurementIndexView, MeasurementCreateView, MeasurementFromSampleCreateView, \
    MeasurementEditView, MeasurementListJson, MeasurementsListJsonUser
from scxrd.views.sample_views import MySamplesList, NewSampleByCustomer, OperatorSamplesList, SampleDeleteView, \
    OperatorSampleDetail, NewSampleOKView
from scxrd.views.views import ResidualsTable, MoleculeView

app_name = 'scxrd'

urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    # Samples:
    path('submit/mysamples/', MySamplesList.as_view(), name='my_samples_page'),
    path('operator/allsamples/', OperatorSamplesList.as_view(), name='op_samples_page'),
    path('sample/submit/', NewSampleByCustomer.as_view(), name='submit_sample'),
    path('sample/submit_ok/', NewSampleOKView.as_view(), name='submit_sample_ok'),
    path('sample/delete/<int:pk>', SampleDeleteView.as_view(), name='delete_sample'),
    path('sample/submit/ketcher.html', TemplateView.as_view(template_name="scxrd/ketcher/ketcher.html")),
    path('operator/sample_detail/<int:pk>/', OperatorSampleDetail.as_view(), name='op_samples_detail'),
    # Measurements
    path('measurements/', MeasurementIndexView.as_view(), name='all_measurements'),
    path('new_measurement/', MeasurementCreateView.as_view(), name='new_exp'),
    path('new_measurement/<int:pk>/', MeasurementFromSampleCreateView.as_view(), name='new_exp_from_sample'),
    path('measurements/edit/<int:number>/', MeasurementEditView.as_view(), name='edit-measurement'),
    path('measurements/table/<int:pk>/', ResidualsTable.as_view(), name='details_table'),
    path('measurements_list/', MeasurementListJson.as_view(), name='measurements_list'),
    path('measurements_list_user/', MeasurementsListJsonUser.as_view(), name='measurements_list_from_user'),
    # Others
    path('measurements/molecule/', MoleculeView.as_view(), name='molecule'),
    path('sample/submit/library.sdf', TemplateView.as_view(template_name="scxrd/ketcher/library.sdf")),
    path('sample/submit/library.svg', TemplateView.as_view(template_name="scxrd/ketcher/library.svg")),
    path('sample/submit/ketcher.svg', TemplateView.as_view(template_name="scxrd/ketcher/ketcher.svg")),

]
