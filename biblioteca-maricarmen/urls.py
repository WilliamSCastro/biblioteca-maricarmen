from django.contrib import admin
from django.urls import path, re_path
from biblioteca import views
from ninja import NinjaAPI
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from biblioteca.api import api

from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
    path('autocomplete/autor/', views.autocomplete_autor, name='autocomplete_autor'),
    path('autocomplete/editorial/', views.autocomplete_editorial, name='autocomplete_editorial'),

    # Este path solo se usa si quieres servir index.html desde templates
    path('', views.index),
]

# Este patrón captura TODAS las rutas no coincidentes (excepto /api/) y devuelve el index.html
urlpatterns += [
    re_path(r'^(?!api/).*$', TemplateView.as_view(template_name="index.html")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'biblioteca.views.custom_403_view'
handler404 = 'biblioteca.views.custom_404_view'