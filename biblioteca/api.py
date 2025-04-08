from django.contrib.auth import authenticate
from ninja import NinjaAPI, Schema, File, Form
from ninja.security import HttpBasicAuth, HttpBearer
from .models import *
from typing import List, Optional, Union, Literal
import secrets
from django.db.models import Q
import re
from ninja.files import UploadedFile
from django.http import HttpRequest  # Import HttpRequest for type hinting
from django.shortcuts import get_object_or_404
from .models import Cataleg, Llibre, Revista, CD, DVD, BR, Dispositiu

import time

import csv
import io
from ninja import NinjaAPI, File, UploadedFile
from ninja.responses import Response
from .models import Usuari, Centre, Cicle  # Ajusta la ruta según tu estructura de proyecto

api = NinjaAPI();


# Autenticació bàsica
class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user:
            # Genera un token simple
            token = secrets.token_hex(16)
            user.auth_token = token
            user.save()
            return token
        return None

# Autenticació per Token Bearer
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            user = Usuari.objects.get(auth_token=token)
            return user
        except Usuari.DoesNotExist:
            return None
        
def get_user_by_token(token: str) -> Optional[Usuari]:
    try:
        user = Usuari.objects.get(auth_token=token)
        return user
    except Usuari.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error fetching user by token: {e}")
        return None

# Function to format user data (reusable)
def format_user_data(user: Usuari):
    if user.is_superuser:
        role = "Administrador"
    elif user.groups.filter(name='Bibliotecari').exists():
        role = "Bibliotecari"
    else:
        role = "Usuari"

    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "centre_id": user.centre.id if user.centre else None,
        "cicle_id": user.cicle.id if user.cicle else None,
        "telefon": user.telefon,
        "imatge_url": user.imatge.url if user.imatge else None,
        "role": role,
        # "is_active": user.is_active,
        # "is_staff": user.is_staff,
        # "is_superuser": user.is_superuser,
        # "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        # "last_login": user.last_login.isoformat() if user.last_login else None,
    }
    return data

def is_valid_email(email_string: str) -> bool:
    if not isinstance(email_string, str):
        return False
    if email_string != email_string.strip():
        return False
    if not email_string:
        return False
    pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@" \
              r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+" \
              r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
    if re.match(pattern, email_string, re.IGNORECASE):
        return True
    else:
        return False

# Endpoint per obtenir un token
@api.get("/token", auth=BasicAuth())
@api.get("/token/", auth=BasicAuth())
def obtenir_token(request):
    
    token = request.auth 
    user = get_user_by_token(token)
    time.sleep(3)
    if user.is_superuser:
        role = "Administrador"
    elif user.groups.filter(name='Bibliotecari').exists():
        role = "Bibliotecari"
    else:
        role = "Usuari"

    user_data = {
        "token": token,
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "centre_id": user.centre.id if user.centre else None,
        "cicle_id": user.cicle.id if user.cicle else None,
        "telefon": user.telefon,
        "imatge_url": user.imatge.url if user.imatge else None, 
        "role": role,
        # "is_active": user.is_active,
        # "is_staff": user.is_staff, 
        # "is_superuser": user.is_superuser,
        # "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        # "last_login": user.last_login.isoformat() if user.last_login else None,
    }

    return user_data

@api.get("/me", auth=AuthBearer()) # Use AuthBearer for authentication
@api.get("/me/", auth=AuthBearer())
def get_current_user(request):
    user = request.auth
    time.sleep(3)
    if user:
        user_data = format_user_data(user)
        return user_data
    else:
        return api.create_response(request, {"detail": "Authentication failed"}, status=401)
class CatalegOut(Schema):
    id: int
    titol: str
    autor: str

@api.get("/buscar/", response=List[CatalegOut])
def buscar_cataleg(request, q: str):
    resultats = Cataleg.objects.filter(
        Q(titol__icontains=q) | Q(autor__icontains=q)
    ).values("id", "titol", "autor")
    return list(resultats)

class ProfileUpdatePayload(Schema):
    email: str 
    telefon: str = None # Ensure names match frontend 'name' attributes

@api.post("/update-profile/", auth=AuthBearer())
def update_profile(request: HttpRequest,                  # Access request for auth user
    payload: ProfileUpdatePayload = Form(...), # Use Form(...) to get form fields
    avatar: Optional[UploadedFile] = File(None) # Use File(...) to get the uploaded file, make it optional
):
    user = request.auth  # Get authenticated user from token


    if not user:
        return api.create_response(request, {"detail": "Authentication required"}, status=401)
    
    time.sleep(2)
    errors = {}
    updated = False # Flag to check if any changes were made

    if payload.email:
        if not is_valid_email(payload.email):
            errors["email"] = "Email no té un format válid."
        elif payload.email != user.email:
            user.email = payload.email
            updated = True

    if payload.telefon:
        if len(payload.telefon) != 9 or not payload.telefon.isdigit():
            errors["telefon"] = "El teléfon ha de tenir 9 dígits."
        elif payload.telefon != user.telefon:
            user.telefon = payload.telefon
            updated = True

    if avatar:
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if avatar.content_type not in allowed_types:
            errors["avatar"] = "Format de imatge invàlid. Només poden ser JPG, JPEG i PNG."
        else:
            user.imatge = avatar
            updated = True

    if errors:
        return api.create_response(request, {"formErrors": errors}, status=400)

    if updated:
        try:
            user.save()
            return api.create_response(request, {"type": "success_modify", "userData": format_user_data(user)}, status=200)
        except Exception as e:
            return api.create_response(request, {"details": "Error al intentar actualitzar el perfil. Torna a intentar-ho més tard"}, status=500)

    return api.create_response(request, {"type": "no_change", "detail": "No changes made."}, status=200)

@api.get("/cataleg/{id}", response=dict)
def get_cataleg(request, id: int):
    try:
        cataleg = Cataleg.objects.get(id=id)
    except Cataleg.DoesNotExist:
        return {"detail": "Catàleg no trobat"}
    
    # Datos comunes a todos los Cataleg
    data = {
        "id": cataleg.id,
        "titol": cataleg.titol,
        "titol_original": cataleg.titol_original,
        "autor": cataleg.autor,
        "CDU": cataleg.CDU,
        "signatura": cataleg.signatura,
        "data_edicio": cataleg.data_edicio.isoformat() if cataleg.data_edicio else None,
        "resum": cataleg.resum,
        "anotacions": cataleg.anotacions,
        "mides": cataleg.mides,
        "tags": [tag.nom for tag in cataleg.tags.all()]  # Se asume que Categoria tiene el campo 'nom'
    }
    
    # Datos de la subclase específica, si aplica
    subclass_data = {}
    
    if hasattr(cataleg, 'llibre'):
        llibre = cataleg.llibre
        subclass_data = {
            "type": "Llibre",
            "ISBN": llibre.ISBN,
            "editorial": llibre.editorial,
            "colleccio": llibre.colleccio,
            "lloc": llibre.lloc,
            "pais": llibre.pais.id if llibre.pais else None,
            "llengua": llibre.llengua.id if llibre.llengua else None,
            "numero": llibre.numero,
            "volums": llibre.volums,
            "pagines": llibre.pagines,
            "info_url": llibre.info_url,
            "preview_url": llibre.preview_url,
            "thumbnail_url": llibre.thumbnail_url
        }
    elif hasattr(cataleg, 'revista'):
        revista = cataleg.revista
        subclass_data = {
            "type": "Revista",
            "ISSN": revista.ISSN,
            "editorial": revista.editorial,
            "lloc": revista.lloc,
            "pais": revista.pais.id if revista.pais else None,
            "llengua": revista.llengua.id if revista.llengua else None,
            "numero": revista.numero,
            "volums": revista.volums,
            "pagines": revista.pagines
        }
    elif hasattr(cataleg, 'cd'):
        cd = cataleg.cd
        subclass_data = {
            "type": "CD",
            "discografica": cd.discografica,
            "estil": cd.estil,
            "duracio": str(cd.duracio)
        }
    elif hasattr(cataleg, 'dvd'):
        dvd = cataleg.dvd
        subclass_data = {
            "type": "DVD",
            "productora": dvd.productora,
            "duracio": str(dvd.duracio)
        }
    elif hasattr(cataleg, 'br'):
        br = cataleg.br
        subclass_data = {
            "type": "BR",
            "productora": br.productora,
            "duracio": str(br.duracio)
        }
    elif hasattr(cataleg, 'dispositiu'):
        dispositiu = cataleg.dispositiu
        subclass_data = {
            "type": "Dispositiu",
            "marca": dispositiu.marca,
            "model": dispositiu.model
        }
    else:
        subclass_data = {"type": "Cataleg"}
    
    data["subclass"] = subclass_data

    # Incluir todos los ejemplares asociados a este Cataleg
    exemplars = cataleg.exemplar_set.all()
    exemplar_list = []
    for exemplar in exemplars:
        exemplar_list.append({
            "id": exemplar.id,
            "registre": exemplar.registre,
            "exclos_prestec": exemplar.exclos_prestec,
            "baixa": exemplar.baixa,
            # Puedes ampliar la información del centre según necesites
            "centre": {
                "id": exemplar.centre.id,
                "nom": str(exemplar.centre)  # Suponiendo que Centre tenga un __str__ representativo
            }
        })
    
    data["exemplars"] = exemplar_list

    return data



@api.post("/import-users/")
def import_users(request, file: UploadedFile = File(...)):
    # Verificamos que haya un archivo y que sea CSV
    if not file:
        return Response({"error": "No se proporcionó ningún archivo."}, status=400)
    if not file.name.endswith('.csv'):
        return Response({"error": "El archivo debe ser CSV."}, status=400)
    
    try:
        data_set = file.read().decode("UTF-8")
    except Exception as e:
        return Response({"error": f"Error al leer el archivo: {str(e)}"}, status=400)
    
    io_string = io.StringIO(data_set)
    reader = csv.DictReader(io_string)
    
    imported_count = 0
    errors = []

    # Documentación del formato CSV esperado:
    #   nom, cognom1, cognom2, email, telefon, centre, grup
    #
    # Ejemplo:
    #   nom,cognom1,cognom2,email,telefon,centre,grup
    #   Albert,López,Soler,alopez@example.com,666111222,1,2
    #
    # donde "centre" y "grup" son IDs válidos en tus modelos Centre y Cicle.
    
    for index, row in enumerate(reader, start=1):
        nom = row.get("nom", "").strip()
        cognom1 = row.get("cognom1", "").strip()
        cognom2 = row.get("cognom2", "").strip()
        email = row.get("email", "").strip()
        telefon = row.get("telefon", "").strip()
        centre_val = row.get("centre", "").strip()
        grup_val = row.get("grup", "").strip()

        # Validar que todos los campos estén presentes
        if not all([nom, cognom1, cognom2, email, telefon, centre_val, grup_val]):
            errors.append(
                f"Fila {index}: Todos los campos son obligatorios (nom, cognom1, cognom2, email, telefon, centre, grup)."
            )
            continue

        last_name = f"{cognom1} {cognom2}".strip()

        centre_obj = None
        try:
            centre_obj = Centre.objects.get(pk=centre_val)
        except Centre.DoesNotExist:
            errors.append(f"Fila {index}: Centre con ID '{centre_val}' no encontrado.")
            continue

        cicle_obj = None
        try:
            cicle_obj = Cicle.objects.get(pk=grup_val)
        except Cicle.DoesNotExist:
            errors.append(f"Fila {index}: Cicle (grup) con ID '{grup_val}' no encontrado.")
            continue

        username = email

        user, created = Usuari.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": nom,
                "last_name": last_name,
                "telefon": telefon,
                "centre": centre_obj,
                "cicle": cicle_obj,
            }
        )

        if not created:
            errors.append(f"Fila {index}: Usuario con email '{email}' ya existe.")
            continue

        imported_count += 1

    summary = {
        "imported": imported_count,
        "errors": errors,
        "message": f"Importación completada. Usuarios importados: {imported_count}. Errores: {len(errors)}"
    }
    return summary

