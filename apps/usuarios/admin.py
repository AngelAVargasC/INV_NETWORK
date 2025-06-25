from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    fields = ['foto_perfil', 'telefono', 'area', 'puesto', 'fecha_ingreso', 'activo']

class CustomUserAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'area', 'puesto', 'telefono', 'activo', 'fecha_creacion']
    list_filter = ['area', 'activo', 'fecha_creacion']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'telefono']
    list_editable = ['activo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario',)
        }),
        ('Información Personal', {
            'fields': ('foto_perfil', 'telefono')
        }),
        ('Información Laboral', {
            'fields': ('area', 'puesto', 'fecha_ingreso')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
