from django.conf.urls.static import static
from django.urls import path, reverse_lazy
from uploadman.views import uploads

from mysite import settings
from . import views


app_name = 'scxrd'

urlpatterns = [
    path('', views.ExperimentView.as_view(), name='index'),
    path('new/', views.ExperimentCreateView.as_view(), name='new'),
    path('edit/<int:pk>/', views.ExperimentEditView.as_view(), name='edit'),
    path('view/<int:pk>/', views.ExperimentDetailView.as_view(), name='view'),
    path('table/<int:pk>/', views.experiment_test, name='table'),
    path('order_list_json/', views.OrderListJson.as_view(), name='order_list_json'),
    path('edit/<int:pk>/upload_cif', uploads, name='cif_upload'),
]


