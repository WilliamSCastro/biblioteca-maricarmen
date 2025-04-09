from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from django.core.exceptions import PermissionDenied

def index(response):
    try:
        tpl = get_template("index.html")
        return render(response,"index.html")
    except TemplateDoesNotExist:
        return HttpResponse("Backend OK. Posa en marxa el frontend seguint el README.")

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)

# def custom_403_view(request, exception=None):
#     return render(request, '403.html', status=403)

# def test_403(request):
#     raise PermissionDenied()