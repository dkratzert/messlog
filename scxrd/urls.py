from django.conf.urls.static import static
from django.urls import path, reverse_lazy, include

from mysite import settings
from . import views


app_name = 'scxrd'

urlpatterns = [
    path('', views.ExperimentIndexView.as_view(), name='index'),
    path('new/', views.ExperimentCreateView.as_view(), name='new'),
    path('edit/<int:pk>/', views.ExperimentEditView.as_view(), name='edit'),
    path('view/<int:pk>/', views.ExperimentDetailView.as_view(), name='view'),
    path('table/<int:pk>/', views.DetailsTable.as_view(), name='details_table'),
    path('experiments_list/', views.ExperimentListJson.as_view(), name='experiments_list'),
    path('customers/', views.Customers.as_view(), name='customers'),
    path('molecule/', views.MoleculeView.as_view(), name='molecule'),
    #path('upload/<int:pk>/', views.UploadView.as_view(), name='upload'),
    path('report/<int:pk>/', views.ReportView.as_view(), name='report'),
    path('upload/<int:pk>/', views.DragAndDropUploadView.as_view(), name='upload_files'),
]


