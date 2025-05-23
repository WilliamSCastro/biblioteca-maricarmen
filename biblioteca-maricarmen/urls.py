"""
URL configuration for biblio_maricarmen project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path
from biblioteca import views
from ninja import NinjaAPI
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from biblioteca.api import api

urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    path("api/", api.urls),
    path('autocomplete/autor/', views.autocomplete_autor, name='autocomplete_autor'),
    path('autocomplete/editorial/', views.autocomplete_editorial, name='autocomplete_editorial'),
    # path('probar403/', views.test_403),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += [re_path(r'^.*$', views.custom_404_view)]


handler403 = 'biblioteca.views.custom_403_view'
handler404 = 'biblioteca.views.custom_404_view'