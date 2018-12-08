from django.urls import path

from . import views

urlpatterns = [
    path('uploads/', views.uploads, name='file_uploads'),
    path('image-uploads/', views.image_uploads, name='upman-image-uploads'),
]
