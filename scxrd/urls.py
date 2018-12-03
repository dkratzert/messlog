from django.urls import path

from . import views

app_name = 'scxrd'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new/', views.ExperimentCreateView.as_view(), name='new'),
    path('edit/<int:pk>/', views.ExperimentEditView.as_view(), name='edit'),
    path('view/<int:pk>/', views.ExperimentShowView.as_view(), name='view'),

]
