"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.views.i18n import JavaScriptCatalog

from mysite import settings
from mysite.core import views
from mysite.mysite.views import HomePageView

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('scxrd/', include('scxrd.urls')),
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('i18n/', include('django_translation_flags.urls')),
    path('favicon.ico', favicon_view),
    path('signup/', views.SignUp.as_view(), name='signup'),
    #path('options/', views.OptionsView.as_view(), name='options'),
    path('useredit/<str:username>/', views.UserEdit.as_view(), name='useredit'),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('password_change/',
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += path('__debug__/', include(debug_toolbar.urls)),
