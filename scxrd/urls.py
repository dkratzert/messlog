from django.urls import path, reverse_lazy

from . import views


app_name = 'scxrd'

urlpatterns = [
    path('', views.ExperimentView.as_view(), name='index'),
    path('new/', views.ExperimentCreateView.as_view(), name='new'),
    path('edit/<int:pk>/', views.ExperimentEditView.as_view(), name='edit'),
    path('view/<int:pk>/', views.ExperimentShowView.as_view(), name='view'),
    path('order_list_json/', views.OrderListJson.as_view(), name='order_list_json'),
]
