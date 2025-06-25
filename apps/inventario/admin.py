from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Fabrica, EstatusPMO, Categoria, Articulo, SeguimientoPMO, ImportacionDatos

@admin.register(Fabrica)
class FabricaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'ubicacion', 'activa', 'fecha_creacion']
    list_filter = ['activa', 'fecha_creacion']
    search_fields = ['nombre', 'codigo', 'ubicacion']
    readonly_fields = ['fecha_creacion']

@admin.register(EstatusPMO)
class EstatusPMOAdmin(admin.ModelAdmin):
    list_display = ['estado', 'descripcion', 'color', 'orden', 'activo']
    list_filter = ['activo', 'estado']
    list_editable = ['orden', 'color', 'activo']
    search_fields = ['estado', 'descripcion']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'codigo']

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = [
        'id_pmo', 'nombre_proyecto', 'articulo', 'estatus_pmo_texto', 
        'año', 'program_manager', 'fabrica_texto', 'costo_unitario_distribucion'
    ]
    list_filter = [
        'año', 'estatus_pmo_texto', 'fabrica_texto', 'tipo', 'fecha_creacion'
    ]
    search_fields = [
        'id_pmo', 'nombre_proyecto', 'articulo', 'program_manager', 
        'proveedor', 'descripcion'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('año', 'id_pmo', 'articulo', 'descripcion')
        }),
        ('Proyecto', {
            'fields': ('nombre_proyecto', 'nombre_proyecto_recibo', 'program_manager', 'estatus_pmo_texto')
        }),
        ('Proveedores y Órdenes', {
            'fields': ('proveedor', 'orden_compra', 'fabrica_texto', 'tipo')
        }),
        ('Costos y Cantidades', {
            'fields': (
                'costo_unitario_distribucion', 'cantidad_embarcada', 'costo_salida_mxn',
                'existencia_actual', 'costo_mxn_existencias', 'costo_usd_existencias'
            )
        }),
        ('Seguimiento', {
            'fields': ('fecha_implementacion', 'historial', 'observaciones', 'retrasos_salida', 'avp')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )

@admin.register(SeguimientoPMO)
class SeguimientoPMOAdmin(admin.ModelAdmin):
    list_display = ['articulo', 'estatus_anterior', 'estatus_nuevo', 'fecha_cambio', 'usuario']
    list_filter = ['fecha_cambio', 'estatus_anterior', 'estatus_nuevo']
    search_fields = ['articulo__id_pmo', 'comentarios']
    readonly_fields = ['fecha_cambio']

@admin.register(ImportacionDatos)
class ImportacionDatosAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'archivo_original', 'fecha_importacion', 'usuario',
        'total_registros', 'registros_exitosos', 'registros_fallidos', 'tasa_exito'
    ]
    list_filter = ['fecha_importacion', 'usuario']
    search_fields = ['archivo_original', 'notas']
    readonly_fields = ['fecha_importacion', 'tasa_exito']
    
    def tasa_exito(self, obj):
        if obj.total_registros > 0:
            return f"{obj.tasa_exito:.1f}%"
        return "0%"
    tasa_exito.short_description = 'Tasa de Éxito'

admin.site.site_header = "Administración Inventario PMO"
admin.site.site_title = "Inventario PMO"
admin.site.index_title = "Panel de Control - Sistema de Inventario PMO"
