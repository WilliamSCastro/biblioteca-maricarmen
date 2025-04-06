from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import escape, mark_safe


from .models import *

class CategoriaAdmin(admin.ModelAdmin):
	list_display = ('nom','parent')
	ordering = ('parent','nom')


class UsuariAdmin(UserAdmin):
    # Keep your existing fieldsets
    fieldsets = UserAdmin.fieldsets + (
            ("Dades addicionals", { # Changed title slightly for clarity
                'fields': ('centre', 'cicle', 'telefon', 'imatge'),
            }),
    )

    # # Add custom fields to list display for easier viewing/sorting
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'centre', 'cicle', 'telefon')
    # # Add filtering options if useful
    # list_filter = UserAdmin.list_filter + ('centre', 'cicle')
    #  # Add search fields if useful
    # search_fields = UserAdmin.search_fields + ('telefon',)


    # def get_readonly_fields(self, request, obj=None):
    #     # Get the default readonly fields from the parent class
    #     readonly_fields = set(super().get_readonly_fields(request, obj))

    #     # Superusers can edit everything
    #     if request.user.is_superuser:
    #         # Ensure 'telefon' is never read-only for superusers
    #         readonly_fields.discard('telefon')
    #         return tuple(readonly_fields)

    #     # Check if the user is in the 'bibliotecaris' group
    #     is_bibliotecari = request.user.groups.filter(name='Bibliotecari').exists()

    #     # If editing an existing user object ('obj' is the user being edited)
    #     if obj:
    #         # If the user viewing the page is a bibliotecari
    #         if is_bibliotecari:
    #             # Allow them to edit 'telefon'
    #             readonly_fields.discard('telefon')

    #             # OPTIONAL: If you want to prevent bibliotecaris from editing *other*
    #             # sensitive fields of *other* users (but allow editing their own),
    #             # make other fields read-only when editing someone else.
    #             if obj != request.user:
    #                 fields_to_protect = {
    #                     'username', 'password', # Password field is handled separately usually
    #                     'first_name', 'last_name', 'email',
    #                     'is_active', 'is_staff', 'is_superuser',
    #                     'groups', 'user_permissions',
    #                     'last_login', 'date_joined',
    #                     'centre', 'cicle', 'imatge' # Add other custom fields here if needed
    #                 }
    #                 readonly_fields.update(fields_to_protect)
    #                 # Ensure telefon remains editable even after adding protected fields
    #                 readonly_fields.discard('telefon')

    #         # If the user viewing the page is NOT a bibliotecari (but is staff)
    #         else:
    #             # Prevent non-bibliotecari staff from editing anyone's phone number
    #             # (they can still edit their own profile based on default permissions)
    #             # This check might be redundant if they don't have change_usuari perm,
    #             # but it adds an extra layer of security.
    #             if obj != request.user:
    #                  readonly_fields.add('telefon')

    #     # If adding a new user (obj is None), apply default logic or specific rules if needed
    #     # For now, let's assume they can set the phone number on creation if they have add_usuari perm

    #     return tuple(readonly_fields)

class ExemplarsInline(admin.TabularInline):
	model = Exemplar
	extra = 1
	readonly_fields = ('pk',)
	fields = ('pk','registre','exclos_prestec','baixa')

class LlibreAdmin(admin.ModelAdmin):
	filter_horizontal = ('tags',)
	inlines = [ExemplarsInline,]
	search_fields = ('titol','autor','CDU','signatura','ISBN','editorial','colleccio')
	list_display = ('titol','autor','editorial','num_exemplars')
	readonly_fields = ('thumb',)
	def num_exemplars(self,obj):
		return obj.exemplar_set.count()
	def thumb(self,obj):
		return mark_safe("<img src='{}' />".format(escape(obj.thumbnail_url)))
	thumb.allow_tags = True

admin.site.register(Usuari,UsuariAdmin)
admin.site.register(Categoria,CategoriaAdmin)
admin.site.register(Pais)
admin.site.register(Llengua)
admin.site.register(Llibre,LlibreAdmin)
admin.site.register(Revista)
admin.site.register(Dispositiu)
admin.site.register(Imatge)

class PrestecAdmin(admin.ModelAdmin):
    readonly_fields = ('data_prestec',)
    fields = ('exemplar','usuari','data_prestec','data_retorn','anotacions')
    list_display = ('exemplar','usuari','data_prestec','data_retorn')

admin.site.register(Centre)
admin.site.register(Cicle)
admin.site.register(Reserva)
admin.site.register(Prestec,PrestecAdmin)
admin.site.register(Peticio)
