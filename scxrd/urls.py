from django.urls import path

from . import views

app_name = 'scxrd'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new/', views.ExperimentCreateView.as_view(), name='new'),
    path('edit/<int:pk>/', views.ExperimentUpdateView.as_view(), name='edit'),
    path('<int:pk>/', views.detail, name='detail'),
]
