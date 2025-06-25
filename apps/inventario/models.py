from django.db import models
from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario
from django.core.validators import MinValueValidator
from decimal import Decimal

class Fabrica(models.Model):
    """Modelo para gestionar las diferentes fábricas/ubicaciones"""
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    ubicacion = models.CharField(max_length=200)
    activa = models.BooleanField(default=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fábrica'
        verbose_name_plural = 'Fábricas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class EstatusPMO(models.Model):
    """Estados del ciclo de vida PMO"""
    ESTADOS_CHOICES = [
        ('PLANIFICACION', 'Planificación'),
        ('APROBADO', 'Aprobado'),
        ('EN_PROCESO', 'En Proceso'),
        ('PENDIENTE', 'Pendiente'),
        ('REVISION', 'En Revisión'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, unique=True)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text='Color hexadecimal para UI')
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Estatus PMO'
        verbose_name_plural = 'Estados PMO'
        ordering = ['orden', 'estado']
    
    def __str__(self):
        return self.get_estado_display()

class Categoria(models.Model):
    """Categorías de artículos"""
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Articulo(models.Model):
    """Modelo principal para artículos del inventario - Mapeo directo de las 23 columnas Excel"""
    
    # Mapeo directo de las 23 columnas del Excel
    año = models.PositiveIntegerField()                                      # 1. Año
    articulo = models.CharField(max_length=100, blank=True)                  # 2. Articulo
    descripcion = models.TextField(blank=True)                               # 3. Descripción
    proveedor = models.CharField(max_length=200, blank=True)                 # 4. Proveedor
    nombre_proyecto_recibo = models.CharField(max_length=300, blank=True)    # 5. Nombre de proyecto recibo
    orden_compra = models.CharField(max_length=100, blank=True)              # 6. Orden de Compra
    id_pmo = models.CharField(max_length=100, db_index=True, default='PMO-TEMP')  # 7. ID de PMO
    nombre_proyecto = models.CharField(max_length=300, blank=True)           # 8. Nombre de Proyecto
    program_manager = models.CharField(max_length=200, blank=True)           # 9. Program Manager
    estatus_pmo_texto = models.CharField(max_length=100, blank=True)         # 10. Estatus PMO
    fecha_implementacion = models.CharField(max_length=100, blank=True)      # 11. Fecha de Implementación Si/No
    historial = models.TextField(blank=True)                                 # 12. Historial
    observaciones = models.TextField(blank=True)                             # 13. Observaciones
    retrasos_salida = models.TextField(blank=True)                           # 14. Retrasos en salida
    avp = models.CharField(max_length=200, blank=True)                       # 15. AVP
    tipo = models.CharField(max_length=100, blank=True)                      # 16. Tipo
    fabrica_texto = models.CharField(max_length=100, blank=True)             # 17. Fabrica
    costo_unitario_distribucion = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # 18. COSTO UNITARIO DISTRIBUCION
    cantidad_embarcada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)          # 19. Cantidad Embarcada
    costo_salida_mxn = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)            # 20. Costo Salida $MXN
    existencia_actual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)           # 21. Existencia Actual
    costo_mxn_existencias = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)       # 22. Costo $MXN Existencias
    costo_usd_existencias = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)       # 23. Costo $USD Existencias
    
    # Relaciones simplificadas (opcionales)
    fabrica = models.ForeignKey(Fabrica, on_delete=models.SET_NULL, null=True, blank=True, related_name='articulos')
    estatus_pmo = models.ForeignKey(EstatusPMO, on_delete=models.SET_NULL, null=True, blank=True, related_name='articulos')
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        ordering = ['-fecha_actualizacion']
        indexes = [
            models.Index(fields=['id_pmo']),
            models.Index(fields=['año']),
        ]
    
    def __str__(self):
        return f"{self.id_pmo} - {self.nombre_proyecto or self.articulo}"

class SeguimientoPMO(models.Model):
    """Historial de seguimiento de cada artículo"""
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='seguimientos')
    estatus_anterior = models.ForeignKey(EstatusPMO, on_delete=models.CASCADE, related_name='seguimientos_desde')
    estatus_nuevo = models.ForeignKey(EstatusPMO, on_delete=models.CASCADE, related_name='seguimientos_hacia')
    
    comentarios = models.TextField(blank=True)
    adjuntos = models.FileField(upload_to='seguimientos/', blank=True, null=True)
    
    # Metadatos
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Seguimiento PMO'
        verbose_name_plural = 'Seguimientos PMO'
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.articulo.codigo_articulo}: {self.estatus_anterior} → {self.estatus_nuevo}"

class ImportacionDatos(models.Model):
    """Registro de importaciones masivas de datos"""
    archivo_original = models.CharField(max_length=255)
    fecha_importacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Estadísticas de importación
    total_registros = models.PositiveIntegerField(default=0)
    registros_exitosos = models.PositiveIntegerField(default=0)
    registros_fallidos = models.PositiveIntegerField(default=0)
    
    # Detalles
    log_errores = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Importación de Datos'
        verbose_name_plural = 'Importaciones de Datos'
        ordering = ['-fecha_importacion']
    
    def __str__(self):
        return f"Importación {self.id} - {self.fecha_importacion.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def tasa_exito(self):
        """Calcula el porcentaje de éxito de la importación"""
        if self.total_registros > 0:
            return (self.registros_exitosos / self.total_registros) * 100
        return 0
