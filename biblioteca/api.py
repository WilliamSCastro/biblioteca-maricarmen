from ninja import NinjaAPI, File, UploadedFile,Form, Schema
from ninja.security import HttpBasicAuth, HttpBearer
from typing import List, Optional, Union, Literal
from django.contrib.auth import authenticate
from ninja.responses import Response

from datetime import timedelta
from django.utils import timezone
from ninja.files import UploadedFile
from django.http import HttpRequest 
from django.db.models import Q
from ninja.responses import Response
from datetime import date
import requests
import jwt
from jwt import PyJWKClient
import secrets

from ninja import Schema
from .models import Usuari 
from .models import *

import secrets
import time
import csv
import io
import re

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
        "cicle_id": user.grup.id if user.grup else None,
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
    if user.is_superuser:
        role = "Bibliotecari"
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
        "cicle_id": user.grup.id if user.grup else None,
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
    if user:
        user_data = format_user_data(user)
        return user_data
    else:
        return api.create_response(request, {"detail": "Authentication failed"}, status=401)

class CatalegOut(Schema):
    id: int
    titol: Optional[str]                # Si puede venir None
    autor: Optional[str]
    disponibles: int
    prestats: int
    exclos_prestec: int

@api.get("/buscar/", response=List[CatalegOut])
def buscar_cataleg(request, q: str):
    try:
        from django.utils import timezone

        token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
        user = get_user_by_token(token) if token else None
        user_centre = user.centre if user and user.centre else None

        resultats = Cataleg.objects.filter(
            Q(titol__icontains=q) | Q(autor__icontains=q)
        )

        resposta = []

     for cat in resultats:
            exemplars_qs = Exemplar.objects.filter(cataleg=cat)
            if user_centre:
                exemplars_qs = exemplars_qs.filter(centre=user_centre)

            prestats_ids = Prestec.objects.filter(
                exemplar__in=exemplars_qs,
                data_retorn__gte=timezone.now().date()
            ).values_list("exemplar_id", flat=True)

            exclos_count = exemplars_qs.filter(exclos_prestec=True).count()
            prestats_count = exemplars_qs.filter(id__in=prestats_ids).count()
            disponibles_count = exemplars_qs.exclude(id__in=prestats_ids).filter(exclos_prestec=False).count()

            resposta.append(CatalegOut(
                id=cat.id,
                titol=cat.titol,
                autor=cat.autor or "No se coneix l'autor",
                disponibles=disponibles_count,
                prestats=prestats_count,
                exclos_prestec=exclos_count
            ))


        return resposta

    except Exception as e:
        print("❌ Error en buscar_cataleg:", str(e))
        return []
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
            print(e)
            return api.create_response(request, {"details": f"Error al intentar actualitzar el perfil. Torna a intentar-ho més tard"}, status=500)

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
            "pais": llibre.pais.nom if llibre.pais else None,
            "llengua": llibre.llengua.nom if llibre.llengua else None,
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
            "pais": revista.pais.nom if revista.pais else None,
            "llengua": revista.llengua.nom if revista.llengua else None,
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
    
    # Verifiquem que hi hagi un fitxer i que sigui CSV
    if not file:
        return Response({"error": "No s'ha proporcionat cap fitxer."}, status=400)
    if not file.name.endswith('.csv'):
        return Response({"error": "El fitxer ha de ser en format CSV."}, status=400)

    try:
        data_set = file.read().decode("UTF-8")
    except Exception as e:
        return Response({"error": f"Error en llegir el fitxer: {str(e)}"}, status=400)

    io_string = io.StringIO(data_set)
    reader = csv.DictReader(io_string)

    # Validem que les columnes siguin correctes
    required_fields = {"nom", "cognom1", "cognom2", "email", "telefon", "centre", "grup"}
    if not required_fields.issubset(set(reader.fieldnames or [])):
        return Response({
            "error": f"El fitxer CSV ha de contenir les següents columnes: {', '.join(required_fields)}"
        }, status=400)

    imported_count = 0
    errors = []

    for index, row in enumerate(reader, start=1):
        # Agafem les dades crues
        nom_raw = row.get("nom")
        cognom1_raw = row.get("cognom1")
        cognom2_raw = row.get("cognom2")
        email_raw = row.get("email")
        telefon_raw = row.get("telefon")
        centre_val_raw = row.get("centre")
        grup_val_raw = row.get("grup")

        # Comprovem que cap sigui None o buit
        if not all([nom_raw, cognom1_raw, cognom2_raw, email_raw, telefon_raw, centre_val_raw, grup_val_raw]):
            errors.append(
                f"Fila {index}: Tots els camps són obligatoris (nom, cognom1, cognom2, email, telefon, centre, grup)."
            )
            continue

        # Netegem els valors
        nom = nom_raw.strip()
        cognom1 = cognom1_raw.strip()
        cognom2 = cognom2_raw.strip()
        email = email_raw.strip()
        telefon = telefon_raw.strip()
        centre_val = centre_val_raw.strip()
        grup_val = grup_val_raw.strip()

        last_name = f"{cognom1} {cognom2}"

        try:
            centre_obj = Centre.objects.get(pk=centre_val)
        except Centre.DoesNotExist:
            errors.append(f"Fila {index}: Centre amb ID '{centre_val}' no trobat.")
            continue

        try:
            cicle_obj = Grup.objects.get(pk=grup_val)
        except Grup.DoesNotExist:
            errors.append(f"Fila {index}: Grup (grup) amb ID '{grup_val}' no trobat.")
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
                "grup": cicle_obj,
            }
        )

        if not created:
            errors.append(f"Fila {index}: L'usuari amb l'email '{email}' ja existeix.")
            continue

        imported_count += 1

    summary = {
        "imported": imported_count,
        "errors": errors,
        "message": f"Importació completada. Usuaris importats: {imported_count}. Errors: {len(errors)}"
    }

    return summary


class UserOut(Schema):
    id: int
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None
    username: str

class LoanIn(Schema):
    userId: int
    exemplarId: int

class LoanOut(Schema):
    id: int
    userId: int
    exemplarId: int
    data_prestec: date

# --------------------
# Endpoints
# --------------------

# 1) Buscar usuarios
@api.get("/users/", response=List[UserOut], auth=AuthBearer())
def search_users(request, query: str = None):
    user = request.auth
    # 401 si no está autenticado
    if not user:
        return api.create_response(request, {"detail": "Authentication required"}, status=401)
    # 403 si no es staff/bibliotecario
    if not user.is_staff:
        return api.create_response(request, {"detail": "No tens permís per accedir a aquest recurs."}, status=403)
    # Si no hay query devolvemos lista vacía
    if not query or not query.strip():
        return []
    qs = Usuari.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(telefon__icontains=query) |
        Q(username__icontains=query)
    )[:20]
    return [
        {
            "id": u.id,
            "firstName": u.first_name,
            "lastName": u.last_name,
            "email": u.email,
            "phone": u.telefon,
            "username": u.username,
        }
        for u in qs
    ]


# 2) Crear préstamo
@api.post("/loans/", response=LoanOut, auth=AuthBearer())
def create_loan(request, data: LoanIn):
    user = request.auth
    # 401 si no está autenticado
    if not user:
        return api.create_response(request, {"detail": "Authentication required"}, status=401)
    # 403 si no es staff/bibliotecario
    if not user.is_staff:
        return api.create_response(request, {"detail": "No tens permís per crear préstecs."}, status=403)

    # Validar usuario destino
    try:
        usuario_destino = Usuari.objects.get(pk=data.userId)
    except Usuari.DoesNotExist:
        return api.create_response(request, {"detail": "Usuario no encontrado"}, status=404)

    # Validar ejemplar
    try:
        exemplar = Exemplar.objects.get(pk=data.exemplarId)
    except Exemplar.DoesNotExist:
        return api.create_response(request, {"detail": "Ejemplar no encontrado"}, status=404)
    if exemplar.exclos_prestec:
        return api.create_response(request, {"detail": "El ejemplar ya está excluido de préstamo"}, status=400)

    # Crear préstamo
    
    fecha_devolver = timezone.now().date() + timedelta(days=7)
    prestec = Prestec.objects.create(
        usuari=usuario_destino,
        exemplar=exemplar,
        data_retorn=fecha_devolver
    )

    # 201 con los datos del préstamo
    return Response(
        {
            "id": prestec.id,
            "userId": usuario_destino.id,
            "exemplarId": exemplar.id,
            "data_prestec": prestec.data_prestec,
            "data_retorn": prestec.data_retorn,
        },
        status=201
    )
# Endpoint per a retornar l'historial de préstecs d'un usuari
@api.get("/prestecs/{id}", response=List[dict], auth=AuthBearer())
def get_prestecs(request, id: int):
    # Verificar que el usuario autenticado coincide con el ID solicitado
    user = request.auth  # Usuario autenticado a través del token
    if not user or user.id != id:
        return api.create_response(request, {"detail": "No tens permís per accedir a aquest recurs."}, status=403)

    try:
        usuari = Usuari.objects.get(id=id)
    except Usuari.DoesNotExist:
        return {"detail": "Usuari no trobat"}
    
    # Obtenim els préstecs associats a l'usuari
    prestecs = Prestec.objects.filter(usuari=usuari).order_by('-data_retorn')  # Ordenar de forma inversa
    
    # Preparem la resposta
    resultats = []
    for prestec in prestecs:
        resultats.append({
            "id": prestec.id,
            "data_prestec": prestec.data_prestec.isoformat() if prestec.data_prestec else None,
            "data_retorn": prestec.data_retorn.isoformat() if prestec.data_retorn else None,
            "exemplar_id": prestec.exemplar.id if prestec.exemplar else None,
            "cataleg_id": prestec.exemplar.cataleg.id if prestec.exemplar and prestec.exemplar.cataleg else None,
            "cataleg_titol": prestec.exemplar.cataleg.titol if prestec.exemplar and prestec.exemplar.cataleg else None,
            "exemplar_registre": prestec.exemplar.registre if prestec.exemplar else None,
            "anotacions": prestec.anotacions
        })
    
    return resultats


def verify_google_token(id_token: str):
    res = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}')
    if res.status_code != 200:
        raise ValueError("Token de Google inválido")
    return res.json()

# Configuración
MICROSOFT_JWKS_URL = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
CLIENT_ID = "80ce59e2-3a83-4650-b920-d1f2d194d3e7"


def verify_microsoft_token(id_token: str):
    
    jwk_client = PyJWKClient(MICROSOFT_JWKS_URL)
    signing_key = jwk_client.get_signing_key_from_jwt(id_token).key

    payload = jwt.decode(  # <--- aquí corregido
        id_token,
        signing_key,
        algorithms=["RS256"],
        audience=CLIENT_ID,
        options={"verify_iss": False}
    )
    return payload
class SocialLoginSchema(Schema):
    token: str
    provider: str  # "google" o "microsoft"


@api.post("/social-login/")
def social_login(request, data: SocialLoginSchema):
    print(data)
    try:
        if data.provider == "google":
            user_info = verify_google_token(data.token)
            email = user_info["email"]
            name = user_info.get("name", email.split("@")[0])

        elif data.provider == "microsoft":
            user_info = verify_microsoft_token(data.token)
            email = user_info["email"]
            name = user_info.get("name", email.split("@")[0])

        else:
            return api.create_response(request, {"error": "Proveïdor no suportat"}, status=400)

        # Buscar o crear usuario
        user, created = Usuari.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": name,
                "last_name": ""
            }
        )

        # Generar token propio
        token = secrets.token_hex(16)
        user.auth_token = token
        user.save()

        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }

    except Exception as e:
        return api.create_response(request, {"error": str(e)}, status=400)