
from django.urls import path, re_path

from marcador import views

urlpatterns = [
    re_path(r'^user/(?P<username>[-\w]+)/$', views.bookmark_user, name='marcador_bookmark_user'),
    path('', views.bookmark_list, name='marcador_bookmark_list'),
]