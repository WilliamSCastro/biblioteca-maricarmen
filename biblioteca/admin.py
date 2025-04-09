from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import escape, mark_safe
from .models import *

# Classe base per fer models visibles per staff
class VisibleToStaffAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

# Admins específics per als models
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nom', 'parent')
    ordering = ('parent', 'nom')

class ExemplarAdmin(admin.ModelAdmin):
    readonly_fields = ('centre',)

    def staff_permission(self, request):
        return request.user.is_staff

    def has_module_permission(self, request):
        return self.staff_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.staff_permission(request)

    def has_view_permission(self, request, obj=None):
        return self.staff_permission(request)

    def has_add_permission(self, request):
        return self.staff_permission(request)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.centre = request.user.centre
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

class UsuariAdmin(admin.ModelAdmin):
    search_fields = ['username__icontains', 'first_name__icontains', 'last_name__icontains']

    def staff_permission(self, request):
        return request.user.is_staff

    def has_module_permission(self, request):
        return self.staff_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.staff_permission(request)

    def has_view_permission(self, request, obj=None):
        return self.staff_permission(request)

    SENSITIVE_FIELDS = [
        'is_superuser', 'groups', 'user_permissions'
    ]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_staff and not request.user.is_superuser:
            return self.SENSITIVE_FIELDS
        return []

    def get_fields(self, request, obj=None):
        return [
            'username', 'first_name', 'last_name', 'email',
            'groups', 'user_permissions', 'date_joined', 'last_login', 'telefon'
        ]

class ExemplarsInline(admin.TabularInline):
    model = Exemplar
    extra = 1
    readonly_fields = ('pk', 'centre')
    fields = ('pk', 'registre', 'exclos_prestec', 'baixa', 'centre')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superuser ve todos los Exemplars
        if request.user.has_perm("biblioteca.view_exemplar"):
            return qs.filter(centre=request.user.centre)  # Staff ve solo los de su centro
        return qs.none()  # Sin permisos, no ve nada
    

class LlibreAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)
    inlines = [ExemplarsInline,]
    search_fields = ('titol', 'autor', 'CDU', 'signatura', 'ISBN', 'editorial', 'colleccio')
    list_display = ('titol', 'autor', 'editorial', 'num_exemplars')
    readonly_fields = ('thumb',)

    def num_exemplars(self, obj):
        return obj.exemplar_set.count()

    def thumb(self, obj):
        return mark_safe("<img src='{}' />".format(escape(obj.thumbnail_url)))

    thumb.allow_tags = True

# Admins per als models
class PaisAdmin(VisibleToStaffAdmin): pass
class LlenguaAdmin(VisibleToStaffAdmin): pass
class RevistaAdmin(VisibleToStaffAdmin): pass
class CDAdmin(VisibleToStaffAdmin): pass
class DVDAdmin(VisibleToStaffAdmin): pass
class BRAdmin(VisibleToStaffAdmin): pass
class DispositiuAdmin(VisibleToStaffAdmin): pass
class CicleAdmin(VisibleToStaffAdmin): pass
class ReservaAdmin(VisibleToStaffAdmin): pass
class PeticioAdmin(VisibleToStaffAdmin): pass

admin.site.register(Exemplar, ExemplarAdmin)
admin.site.register(Usuari, UsuariAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Pais, PaisAdmin)
admin.site.register(Llengua, LlenguaAdmin)
admin.site.register(Llibre, LlibreAdmin)
admin.site.register(Revista, RevistaAdmin)
admin.site.register(CD, CDAdmin)
admin.site.register(DVD, DVDAdmin)
admin.site.register(BR, BRAdmin)
admin.site.register(Dispositiu, DispositiuAdmin)
admin.site.register(Cicle, CicleAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Peticio, PeticioAdmin)

class PrestecAdmin(admin.ModelAdmin):
    readonly_fields = ('data_prestec',)
    fields = ('exemplar', 'usuari', 'data_prestec', 'data_retorn', 'anotacions')
    list_display = ('exemplar', 'usuari', 'data_prestec', 'data_retorn')

admin.site.register(Centre)
admin.site.register(Cataleg)
admin.site.register(Log)
admin.site.register(Prestec, PrestecAdmin)
admin.site.register(Imatge)
