from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Llibre

def index(response):
    try:
        tpl = get_template("index.html")
        return render(response,"index.html")
    except TemplateDoesNotExist:
        return HttpResponse("Backend OK. Posa en marxa el frontend seguint el README.")

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)

def custom_403_view(request, exception=None):
    return render(request, '403.html', status=403)

def autocomplete_autor(request):
    """
    Devuelve una lista de autores únicos que coincidan con el término de búsqueda.
    """
    if 'q' in request.GET:  # Cambiar 'term' por 'q'
        term = request.GET.get('q')  # Obtener el término de búsqueda desde 'q'
        autores = (
            Llibre.objects.filter(autor__icontains=term)
            .values_list('autor', flat=True)
            .distinct()[:5]  # Limitar a 5 resultados
        )
        return JsonResponse(list(autores), safe=False)
    return JsonResponse([], safe=False)

def autocomplete_editorial(request):
    """
    Devuelve una lista de editoriales únicas que coincidan con el término de búsqueda.
    """
    if 'q' in request.GET:  # Cambiar 'term' por 'q'
        term = request.GET.get('q')  # Obtener el término de búsqueda desde 'q'
        editoriales = (
            Llibre.objects.filter(editorial__icontains=term)
            .values_list('editorial', flat=True)
            .distinct()[:5]  # Limitar a 5 resultados
        )
        return JsonResponse(list(editoriales), safe=False)
    return JsonResponse([], safe=False)