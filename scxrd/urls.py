from django.urls import path

from . import views

app_name = 'scxrd'

urlpatterns = [
    path('scxrd/', views.IndexView.as_view(), name='index'),
    #path('<int:pk>/', views.DetailView.as_view(), name='detail'),
]
