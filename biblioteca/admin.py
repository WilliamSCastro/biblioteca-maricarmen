from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


# Admins per cada model
@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nom', 'parent']
    ordering = ['parent', 'nom']

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Llengua)
class LlenguaAdmin(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Cataleg)
class CatalegAdmin(admin.ModelAdmin):
    list_display = ['titol', 'autor', 'CDU', 'signatura']
    search_fields = ['titol', 'autor']


class ExemplarsInline(admin.TabularInline):
    model = Exemplar
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        # Hacer que el campo 'centre' sea de solo lectura solo para el grupo 'Bibliotecari'
        if request.user.groups.filter(name="Bibliotecari").exists():
            return ('centre',)
        return ()

    def get_queryset(self, request):
        # Obtenemos el queryset base
        qs = super().get_queryset(request)
        
        # Si el usuario es superuser, devolvemos todos los exemplars
        if request.user.is_superuser:
            return qs
        
        # Si el usuario pertenece al grupo 'Bibliotecari', filtramos por su centro
        if request.user.groups.filter(name="Bibliotecari").exists():
            return qs.filter(centre=request.user.centre)
        
        # Si no es superuser ni bibliotecari, devolvemos un queryset vacío
        return qs.none()

    def save_new_objects(self, request, form, change):
        # Esta función existe en versiones antiguas. Para modernizar, mejor usamos `save_formset` en el ModelAdmin
        return super().save_new_objects(request, form, change)
    
@admin.register(Llibre)
class LlibreAdmin(admin.ModelAdmin):
    inlines = [ExemplarsInline]
    list_display = ['titol', 'autor', 'editorial', 'ISBN']
    search_fields = ['titol', 'autor', 'ISBN']
    filter_horizontal = ('tags',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="Bibliotecari").exists():
            return qs.filter(exemplar__centre=request.user.centre).distinct()
        return qs
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if request.user.groups.filter(name="Bibliotecari").exists():
                obj.centre = request.user.centre
            obj.save()
        formset.save_m2m()


@admin.register(Revista)
class RevistaAdmin(admin.ModelAdmin):
    inlines = [ExemplarsInline]
    list_display = ['titol', 'ISSN', 'editorial']
    search_fields = ['titol', 'ISSN']
    filter_horizontal = ('tags',)

@admin.register(CD)
class CDAdmin(admin.ModelAdmin):
    inlines = [ExemplarsInline]
    list_display = ['titol', 'discografica', 'estil']
    filter_horizontal = ('tags',)

@admin.register(DVD)
class DVDAdmin(admin.ModelAdmin):
    inlines = [ExemplarsInline]
    list_display = ['titol', 'productora', 'duracio']
    filter_horizontal = ('tags',)

@admin.register(BR)
class BRAdmin(admin.ModelAdmin):
    inlines = [ExemplarsInline]
    list_display = ['titol', 'productora', 'duracio']
    filter_horizontal = ('tags',)

@admin.register(Dispositiu)
class DispositiuAdmin(admin.ModelAdmin):
    inlines = [ExemplarsInline]
    list_display = ['titol', 'marca', 'model']
    filter_horizontal = ('tags',)

@admin.register(Exemplar)
class ExemplarAdmin(admin.ModelAdmin):
    list_display = ['cataleg', 'registre', 'centre', 'exclos_prestec', 'baixa']
    search_fields = ['cataleg__titol', 'registre']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.groups.filter(name="Bibliotecari").exists():
            fields = [f for f in fields if f != 'centre']
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.groups.filter(name="Bibliotecari").exists():
            obj.centre = request.user.centre
        super().save_model(request, obj, form, change)

@admin.register(Imatge)
class ImatgeAdmin(admin.ModelAdmin):
    list_display = ['cataleg', 'imatge']

@admin.register(Cicle)
class CicleAdmin(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Usuari)
class UsuariAdmin(UserAdmin):
    model = Usuari
    fieldsets = UserAdmin.fieldsets + (
        ('Informació extra', {'fields': ('centre', 'cicle', 'telefon', 'imatge', 'auth_token')}),
    )
    list_display = ['username', 'first_name', 'last_name', 'email', 'centre', 'is_staff']

    def get_fieldsets(self, request, obj=None):
        # Campos a ocultar para los usuarios del grupo 'Bibliotecari'
        hidden_fields = {'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
                         'centre', 'cicle', 'imatge', 'auth_token'}

        # Obtener los fieldsets base
        fieldsets = super().get_fieldsets(request, obj)

        # Si el usuario pertenece al grupo 'Bibliotecari', ocultar los campos
        if request.user.groups.filter(name="Bibliotecari").exists():
            filtered_fieldsets = []
            for name, data in fieldsets:
                fields = data.get('fields', [])
                # Filtrar los campos que no están en hidden_fields
                filtered_fields = [field for field in fields if field not in hidden_fields]
                if filtered_fields:
                    filtered_fieldsets.append((name, {'fields': filtered_fields}))
            return filtered_fieldsets

        return fieldsets

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['usuari', 'exemplar', 'data']
    search_fields = ['usuari__username', 'exemplar__registre']

@admin.register(Prestec)
class PrestecAdmin(admin.ModelAdmin):
    list_display = ['usuari', 'exemplar', 'data_prestec', 'data_retorn']
    readonly_fields = ['data_prestec']
    search_fields = ['usuari__username', 'exemplar__registre']

@admin.register(Peticio)
class PeticioAdmin(admin.ModelAdmin):
    list_display = ['usuari', 'titol', 'data']
    search_fields = ['usuari__username', 'titol']

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['accio', 'tipus', 'usuari', 'data_accio']
    list_filter = ['tipus', 'data_accio']
    search_fields = ['accio', 'usuari']