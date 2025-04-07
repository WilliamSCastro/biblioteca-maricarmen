from django.contrib.auth import authenticate
from ninja import NinjaAPI, Schema
from ninja.security import HttpBasicAuth, HttpBearer
from .models import *
from typing import List, Optional, Union, Literal
import secrets
from django.db.models import Q
from .models import Cataleg, Llibre, Revista, CD, DVD, BR, Dispositiu
api = NinjaAPI()


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
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }
    return data

# Endpoint per obtenir un token
@api.get("/token", auth=BasicAuth())
@api.get("/token/", auth=BasicAuth())
def obtenir_token(request):
    
    token = request.auth 
    user = get_user_by_token(token)

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
        "is_active": user.is_active,
        "is_staff": user.is_staff, 
        "is_superuser": user.is_superuser,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }

    return user_data

@api.get("/me", auth=AuthBearer()) # Use AuthBearer for authentication
@api.get("/me/", auth=AuthBearer())
def get_current_user(request):
    user = request.auth
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


import csv
import io
from ninja import NinjaAPI, File, UploadedFile
from ninja.responses import Response
from .models import Usuari, Centre, Cicle  # Ajusta la ruta según tu estructura de proyecto

api = NinjaAPI()

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

        # Validación mínima: "nom" y "email" son obligatorios (o ajusta a tus necesidades)
        if not nom or not email:
            errors.append(f"Fila {index}: 'nom' y 'email' son obligatorios.")
            continue

        # Combinamos cognom1 y cognom2 en el last_name
        last_name = f"{cognom1} {cognom2}".strip()

        # Obtenemos el objeto Centre (si se proporciona un ID)
        centre_obj = None
        if centre_val:
            try:
                centre_obj = Centre.objects.get(pk=centre_val)
            except Centre.DoesNotExist:
                errors.append(f"Fila {index}: Centre con ID '{centre_val}' no encontrado.")
        
        # Obtenemos el objeto Cicle (interpretado como 'grup')
        cicle_obj = None
        if grup_val:
            try:
                cicle_obj = Cicle.objects.get(pk=grup_val)
            except Cicle.DoesNotExist:
                errors.append(f"Fila {index}: Cicle (grup) con ID '{grup_val}' no encontrado.")
        
        # Asignamos el username igual al email (o la lógica que prefieras)
        username = email

        # Creamos o actualizamos el usuario
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
            # Si el usuario ya existía, actualizamos datos
            user.email = email
            user.first_name = nom
            user.last_name = last_name
            user.telefon = telefon
            user.centre = centre_obj
            user.cicle = cicle_obj
            user.save()
        
        imported_count += 1

    summary = {
        "imported": imported_count,
        "errors": errors,
        "message": f"Importación completada. Usuarios importados: {imported_count}. Errores: {len(errors)}"
    }
    return summary