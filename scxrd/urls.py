from django.conf.urls.static import static
from django.urls import path, reverse_lazy, include

from mysite import settings
from . import views


app_name = 'scxrd'

urlpatterns = [
    path('', views.ExperimentView.as_view(), name='index'),
    path('new/', views.ExperimentCreateView.as_view(), name='new'),
    path('edit/<int:pk>/', views.ExperimentEditView.as_view(), name='edit'),
    path('view/<int:pk>/', views.ExperimentDetailView.as_view(), name='view'),
    path('table/<int:pk>/', views.DetailsTable.as_view(), name='details_table'),
    path('order_list_json/', views.OrderListJson.as_view(), name='order_list_json'),
    path('customers/', views.Customers.as_view(), name='customers'),
    path('upload/<int:pk>/', views.UploadView.as_view(), name="upload"),
]


