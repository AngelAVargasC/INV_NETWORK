from django.contrib import admin
from .models import ProcesamientoAnalisis, LogProcesamiento

@admin.register(ProcesamientoAnalisis)
class ProcesamientoAnalisisAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'usuario', 'fecha_procesamiento', 'estado', 
        'total_registros_aging', 'tasa_exito_total', 'tiempo_procesamiento'
    ]
    list_filter = ['estado', 'fecha_procesamiento', 'usuario']
    search_fields = ['usuario__username', 'archivo_aging', 'archivo_pipeline', 'archivo_oracle']
    readonly_fields = [
        'fecha_procesamiento', 'tiempo_procesamiento', 'tasa_exito_pipeline', 
        'tasa_exito_oracle', 'tasa_exito_total'
    ]
    
    fieldsets = [
        ('Información General', {
            'fields': ('usuario', 'fecha_procesamiento', 'estado', 'tiempo_procesamiento')
        }),
        ('Archivos de Entrada', {
            'fields': ('archivo_aging', 'archivo_pipeline', 'archivo_oracle')
        }),
        ('Estadísticas de Procesamiento', {
            'fields': (
                'total_registros_aging', 'total_registros_pipeline', 'total_registros_oracle',
                'registros_actualizados_pipeline', 'registros_actualizados_oracle', 
                'registros_no_coincidentes'
            )
        }),
        ('Resultados', {
            'fields': ('archivo_resultado', 'archivo_no_coincidentes')
        }),
        ('Logs', {
            'fields': ('logs_procesamiento',),
            'classes': ('collapse',)
        }),
    ]
    
    def tasa_exito_total(self, obj):
        return f"{obj.tasa_exito_total}%"
    tasa_exito_total.short_description = 'Tasa de Éxito'

@admin.register(LogProcesamiento)
class LogProcesamientoAdmin(admin.ModelAdmin):
    list_display = ['procesamiento', 'timestamp', 'nivel', 'mensaje_corto']
    list_filter = ['nivel', 'timestamp', 'procesamiento__usuario']
    search_fields = ['mensaje', 'procesamiento__id']
    readonly_fields = ['timestamp']
    
    def mensaje_corto(self, obj):
        return obj.mensaje[:100] + "..." if len(obj.mensaje) > 100 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'
