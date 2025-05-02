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