from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

class ProcesamientoAnalisis(models.Model):
    """
    Modelo para registrar los procesamientos de análisis de inventario
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    fecha_procesamiento = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Procesamiento")
    
    # Archivos de entrada
    archivo_aging = models.CharField(max_length=255, verbose_name="Archivo Aging")
    archivo_pipeline = models.CharField(max_length=255, verbose_name="Archivo Pipeline")
    archivo_oracle = models.CharField(max_length=255, verbose_name="Archivo Oracle")
    
    # Resultados del procesamiento
    total_registros_aging = models.IntegerField(default=0, verbose_name="Total Registros Aging")
    total_registros_pipeline = models.IntegerField(default=0, verbose_name="Total Registros Pipeline")
    total_registros_oracle = models.IntegerField(default=0, verbose_name="Total Registros Oracle")
    
    registros_actualizados_pipeline = models.IntegerField(default=0, verbose_name="Actualizados con Pipeline")
    registros_actualizados_oracle = models.IntegerField(default=0, verbose_name="Actualizados con Oracle")
    registros_no_coincidentes = models.IntegerField(default=0, verbose_name="Sin Coincidencias")
    
    # Archivos de salida
    archivo_resultado = models.CharField(max_length=255, blank=True, verbose_name="Archivo Resultado")
    archivo_no_coincidentes = models.CharField(max_length=255, blank=True, verbose_name="Archivo No Coincidentes")
    
    # Logs del procesamiento
    logs_procesamiento = models.TextField(blank=True, verbose_name="Logs del Procesamiento")
    
    # Estado
    ESTADOS = [
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='procesando', verbose_name="Estado")
    
    # Tiempo de procesamiento
    tiempo_procesamiento = models.FloatField(null=True, blank=True, verbose_name="Tiempo (segundos)")
    
    class Meta:
        verbose_name = "Procesamiento de Análisis"
        verbose_name_plural = "Procesamientos de Análisis"
        ordering = ['-fecha_procesamiento']
    
    def __str__(self):
        return f"Procesamiento {self.id} - {self.usuario.username} - {self.fecha_procesamiento.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def tasa_exito_pipeline(self):
        """Calcula la tasa de éxito con pipeline"""
        if self.total_registros_aging > 0:
            return round((self.registros_actualizados_pipeline / self.total_registros_aging) * 100, 2)
        return 0
    
    @property
    def tasa_exito_oracle(self):
        """Calcula la tasa de éxito con oracle"""
        if self.total_registros_aging > 0:
            return round((self.registros_actualizados_oracle / self.total_registros_aging) * 100, 2)
        return 0
    
    @property
    def tasa_exito_total(self):
        """Calcula la tasa de éxito total"""
        if self.total_registros_aging > 0:
            actualizados_total = self.registros_actualizados_pipeline + self.registros_actualizados_oracle
            return round((actualizados_total / self.total_registros_aging) * 100, 2)
        return 0

class LogProcesamiento(models.Model):
    """
    Modelo para registrar logs detallados de cada procesamiento
    """
    procesamiento = models.ForeignKey(
        ProcesamientoAnalisis, 
        on_delete=models.CASCADE, 
        related_name='logs_detallados',
        verbose_name="Procesamiento"
    )
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Timestamp")
    nivel = models.CharField(
        max_length=10, 
        choices=[
            ('INFO', 'Info'),
            ('WARNING', 'Warning'),
            ('ERROR', 'Error'),
            ('SUCCESS', 'Success')
        ],
        default='INFO',
        verbose_name="Nivel"
    )
    mensaje = models.TextField(verbose_name="Mensaje")
    
    class Meta:
        verbose_name = "Log de Procesamiento"
        verbose_name_plural = "Logs de Procesamiento"
        ordering = ['timestamp']
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.nivel}: {self.mensaje[:50]}"
