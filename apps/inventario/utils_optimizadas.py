import logging
from django.db import models
from django.db.models import Count, Sum, Avg, Q, F, Max, Min
from decimal import Decimal
from .models import Articulo
from django.utils import timezone
import traceback
from django.core.cache import cache

# Configurar logger
logger = logging.getLogger(__name__)

def obtener_metricas_basicas_optimizadas():
    """Obtiene métricas básicas de forma optimizada"""
    cache_key = "dashboard_metricas_basicas"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    try:
        # Una sola consulta para obtener métricas básicas
        stats = Articulo.objects.aggregate(
            total_proyectos=Count('id'),
            total_valor=Sum('costo_unitario_distribucion'),
            total_embarcado=Sum('cantidad_embarcada'),
            total_existencia=Sum('existencia_actual'),
            promedio_costo=Avg('costo_unitario_distribucion'),
            # Agregar métricas de existencias
            existencias_mxn=Sum('costo_mxn_existencias'),
            existencias_usd=Sum('costo_usd_existencias'),
            costo_salida_total=Sum('costo_salida_mxn')
        )
        
        # Contar pendientes de forma optimizada
        pendientes = Articulo.objects.filter(
            Q(estatus_pmo_texto__icontains='pendiente') |
            Q(estatus_pmo_texto__icontains='Pendiente')
        ).count()
        
        # Calcular promedio embarcado por artículo
        total_articulos = stats['total_proyectos'] or 1  # Mantener variable interna
        promedio_embarcado = (stats['total_embarcado'] or 0) / total_articulos
        
        resultado = {
            'total_proyectos': stats['total_proyectos'] or 0,
            'valor_total_inventario': float(stats['total_valor'] or 0),
            'total_unidades_embarcadas': float(stats['total_embarcado'] or 0),
            'total_unidades_existencia': float(stats['total_existencia'] or 0),
            'costo_promedio_unitario': float(stats['promedio_costo'] or 0),
            'proyectos_pendientes': pendientes,
            'tasa_pendientes': round((pendientes / total_articulos * 100) if total_articulos > 0 else 0, 2),
            # Métricas financieras adicionales
            'valor_existencias_mxn': float(stats['existencias_mxn'] or 0),
            'valor_existencias_usd': float(stats['existencias_usd'] or 0),
            'valor_total_salidas': float(stats['costo_salida_total'] or 0),
            'promedio_embarcado_por_articulo': round(promedio_embarcado, 1)
        }
        
        # Cache por 5 minutos
        cache.set(cache_key, resultado, timeout=300)
        return resultado
        
    except Exception as e:
        logger.error(f"Error en métricas básicas: {e}")
        return {
            'total_proyectos': 0,
            'valor_total_inventario': 0,
            'total_unidades_embarcadas': 0,
            'total_unidades_existencia': 0,
            'costo_promedio_unitario': 0,
            'proyectos_pendientes': 0,
            'tasa_pendientes': 0,
            'valor_existencias_mxn': 0,
            'valor_existencias_usd': 0,
            'valor_total_salidas': 0,
            'promedio_embarcado_por_articulo': 0
        }

def obtener_metricas_ordenes_optimizadas():
    """Obtiene métricas de órdenes de forma optimizada"""
    cache_key = "dashboard_metricas_ordenes"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    try:
        # Obtener datos de órdenes con mejor cálculo
        ordenes_con_articulos = Articulo.objects.filter(
            orden_compra__isnull=False
        ).exclude(
            orden_compra=''
        ).values('orden_compra').annotate(
            articulos_count=Count('id')
        )
        
        # Calcular estadísticas de las órdenes
        ordenes_stats = ordenes_con_articulos.aggregate(
            total_ordenes=Count('orden_compra'),
            promedio_articulos=Avg('articulos_count'),
            max_articulos=Max('articulos_count'),
            min_articulos=Min('articulos_count')
        )
        
        # Calcular ratio correcto
        total_articulos = Articulo.objects.count()
        total_ordenes = ordenes_stats['total_ordenes'] or 1
        ratio_real = round(total_articulos / total_ordenes, 1)
        
        resultado = {
            'ordenes_unicas': ordenes_stats['total_ordenes'] or 0,
            'promedio_articulos_por_orden': round(float(ordenes_stats['promedio_articulos'] or 0), 1),
            'max_articulos_por_orden': ordenes_stats['max_articulos'] or 0,
            'min_articulos_por_orden': ordenes_stats['min_articulos'] or 0,
            'ratio_global_articulos_ordenes': ratio_real,
            'total_articulos_sistema': total_articulos
        }
        
        # Cache por 10 minutos
        cache.set(cache_key, resultado, timeout=600)
        return resultado
        
    except Exception as e:
        logger.error(f"Error en métricas de órdenes: {e}")
        return {
            'ordenes_unicas': 0,
            'promedio_articulos_por_orden': 0,
            'max_articulos_por_orden': 0,
            'min_articulos_por_orden': 0,
            'ratio_global_articulos_ordenes': 0,
            'total_articulos_sistema': 0
        }

def obtener_metricas_estatus_optimizadas():
    """Obtiene métricas de estatus de forma optimizada"""
    cache_key = "dashboard_metricas_estatus"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    try:
        total_articulos = Articulo.objects.count()
        
        # Top 5 estatus más comunes con porcentajes
        top_estatus = Articulo.objects.values('estatus_pmo_texto').annotate(
            count=Count('id'),
            porcentaje=Count('id') * 100.0 / total_articulos
        ).order_by('-count')[:5]
        
        # Conteos específicos por estatus
        instalados = Articulo.objects.filter(
            estatus_pmo_texto__icontains='instalado'
        ).count()
        
        pendientes_confirmar = Articulo.objects.filter(
            estatus_pmo_texto__icontains='pendiente'
        ).count()
        
        it_status = Articulo.objects.filter(
            estatus_pmo_texto__exact='IT'
        ).count()
        
        forecast_status = Articulo.objects.filter(
            estatus_pmo_texto__icontains='forecast'
        ).count()
        
        resultado = {
            'estatus_distribucion': list(top_estatus),
            'proyectos_instalados': instalados,
            'proyectos_pendientes_confirmar': pendientes_confirmar,
            'proyectos_it': it_status,
            'proyectos_forecast': forecast_status,
            'tasa_instalados': round((instalados / total_articulos * 100) if total_articulos > 0 else 0, 2),
            'tasa_pendientes_confirmar': round((pendientes_confirmar / total_articulos * 100) if total_articulos > 0 else 0, 2),
            'tasa_it': round((it_status / total_articulos * 100) if total_articulos > 0 else 0, 2),
            'tasa_forecast': round((forecast_status / total_articulos * 100) if total_articulos > 0 else 0, 2)
        }
        
        # Cache por 10 minutos
        cache.set(cache_key, resultado, timeout=600)
        return resultado
        
    except Exception as e:
        logger.error(f"Error en métricas de estatus: {e}")
        return {
            'estatus_distribucion': [],
            'proyectos_instalados': 0,
            'proyectos_pendientes_confirmar': 0,
            'proyectos_it': 0,
            'proyectos_forecast': 0,
            'tasa_instalados': 0,
            'tasa_pendientes_confirmar': 0,
            'tasa_it': 0,
            'tasa_forecast': 0
        }

def obtener_metricas_fabricas_optimizadas():
    """Obtiene métricas de fábricas de forma optimizada"""
    cache_key = "dashboard_metricas_fabricas"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    try:
        # Contar fábricas activas únicas
        fabricas_activas = Articulo.objects.values('fabrica_texto').distinct().count()
        
        # Top 3 fábricas por volumen
        top_fabricas = Articulo.objects.values('fabrica_texto').annotate(
            total_proyectos=Count('id'),
            valor_total=Sum('costo_unitario_distribucion')
        ).order_by('-total_proyectos')[:3]
        
        resultado = {
            'total_fabricas_activas': fabricas_activas,
            'top_fabricas': list(top_fabricas)
        }
        
        # Cache por 15 minutos
        cache.set(cache_key, resultado, timeout=900)
        return resultado
        
    except Exception as e:
        logger.error(f"Error en métricas de fábricas: {e}")
        return {
            'total_fabricas_activas': 0,
            'top_fabricas': []
        }

def obtener_dashboard_completo_optimizado():
    """Función principal optimizada para el dashboard"""
    
    try:
        # Obtener métricas en paralelo usando cache
        metricas_basicas = obtener_metricas_basicas_optimizadas()
        metricas_ordenes = obtener_metricas_ordenes_optimizadas()
        metricas_estatus = obtener_metricas_estatus_optimizadas()
        metricas_fabricas = obtener_metricas_fabricas_optimizadas()
        
        # Calcular métricas adicionales
        eficiencia_programa = 100 - metricas_basicas['tasa_pendientes']
        valor_promedio_proyecto = (metricas_basicas['valor_total_inventario'] / metricas_basicas['total_proyectos']) if metricas_basicas['total_proyectos'] > 0 else 0
        
        # Combinar todas las métricas
        resultado = {
            **metricas_basicas,
            **metricas_ordenes,
            **metricas_estatus,
            **metricas_fabricas,
            # Métricas calculadas adicionales
            'eficiencia_programa': round(eficiencia_programa, 1),
            'valor_promedio_proyecto': round(valor_promedio_proyecto, 2),
            'tasa_completados': metricas_estatus['tasa_instalados'],
            'año_analisis': timezone.now().year,
            'fecha_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M')
        }
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en dashboard completo: {e}")
        return {
            'total_proyectos': 0,
            'valor_total_inventario': 0,
            'proyectos_pendientes': 0,
            'tasa_pendientes': 0,
            'ordenes_unicas': 0,
            'promedio_articulos_por_orden': 0,
            'max_articulos_por_orden': 0,
            'ratio_global_articulos_ordenes': 0,
            'proyectos_instalados': 0,
            'tasa_instalados': 0,
            'valor_existencias_mxn': 0,
            'valor_existencias_usd': 0,
            'promedio_embarcado_por_articulo': 0,
            'total_fabricas_activas': 0,
            'eficiencia_programa': 0,
            'valor_promedio_proyecto': 0,
            'error': str(e),
            'fecha_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M')
        }

def obtener_metricas_dashboard_completas():
    """Función que obtiene todas las métricas para el nuevo dashboard AT&T"""
    cache_key = "dashboard_metricas_completas_v2"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    try:
        # Métricas principales
        total_articulos = Articulo.objects.count()
        articulos_pendientes = Articulo.objects.filter(
            Q(estatus_pmo_texto__icontains='pendiente') |
            Q(estatus_pmo_texto__icontains='proceso')
        ).count()
        
        # Valores financieros
        valor_total_mxn = Articulo.objects.aggregate(
            total=Sum('costo_unitario_distribucion')
        )['total'] or 0
        
        valor_total_usd = Articulo.objects.aggregate(
            total=Sum('precio_lista_usd')
        )['total'] or 0
        
        # Métricas de órdenes
        unidades_embarcadas = Articulo.objects.aggregate(
            total=Sum('cantidad_embarcada')
        )['total'] or 0
        
        existencia_actual = Articulo.objects.aggregate(
            total=Sum('existencia_actual')
        )['total'] or 0
        
        ordenes_pendientes = Articulo.objects.filter(
            estatus_pmo_texto__icontains='pendiente'
        ).count()
        
        ordenes_completadas = Articulo.objects.filter(
            estatus_pmo_texto__icontains='instalado'
        ).count()
        
        # Métricas financieras detalladas
        existencias_mxn = Articulo.objects.aggregate(
            total=Sum(F('existencia_actual') * F('costo_unitario_distribucion'))
        )['total'] or 0
        
        existencias_usd = Articulo.objects.aggregate(
            total=Sum(F('existencia_actual') * F('precio_lista_usd'))
        )['total'] or 0
        
        valor_promedio_articulo = valor_total_mxn / total_articulos if total_articulos > 0 else 0
        
        # Métricas de logística
        fabricas_activas = Articulo.objects.values('fabrica_texto').distinct().count()
        ubicaciones_unicas = Articulo.objects.exclude(
            ubicacion_geografica__isnull=True
        ).exclude(
            ubicacion_geografica__exact=''
        ).values('ubicacion_geografica').distinct().count()
        
        categorias_articulos = Articulo.objects.exclude(
            clasificacion__isnull=True
        ).exclude(
            clasificacion__exact=''
        ).values('clasificacion').distinct().count()
        
        # Métricas de eficiencia
        tasa_rotacion = 75.5  # Simulado
        dias_promedio_stock = 45  # Simulado
        eficiencia_general = 85.2  # Simulado
        
        resultado = {
            # Métricas principales
            'total_articulos': total_articulos,
            'articulos_pendientes': articulos_pendientes,
            'valor_total_mxn': valor_total_mxn,
            'valor_total_usd': valor_total_usd,
            
            # Análisis de órdenes
            'unidades_embarcadas': unidades_embarcadas,
            'existencia_actual': existencia_actual,
            'ordenes_pendientes': ordenes_pendientes,
            'ordenes_completadas': ordenes_completadas,
            
            # Análisis financiero
            'existencias_mxn': existencias_mxn,
            'existencias_usd': existencias_usd,
            'valor_promedio_articulo': valor_promedio_articulo,
            
            # Logística
            'fabricas_activas': fabricas_activas,
            'ubicaciones_unicas': ubicaciones_unicas,
            'categorias_articulos': categorias_articulos,
            
            # Eficiencia
            'tasa_rotacion': tasa_rotacion,
            'dias_promedio_stock': dias_promedio_stock,
            'eficiencia_general': eficiencia_general,
            
            # Metadata
            'fecha_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        }
        
        # Cache por 5 minutos
        cache.set(cache_key, resultado, timeout=300)
        return resultado
        
    except Exception as e:
        logger.error(f"Error en métricas dashboard completas: {e}")
        return {
            'total_articulos': 0,
            'articulos_pendientes': 0,
            'valor_total_mxn': 0,
            'valor_total_usd': 0,
            'unidades_embarcadas': 0,
            'existencia_actual': 0,
            'ordenes_pendientes': 0,
            'ordenes_completadas': 0,
            'existencias_mxn': 0,
            'existencias_usd': 0,
            'valor_promedio_articulo': 0,
            'fabricas_activas': 0,
            'ubicaciones_unicas': 0,
            'categorias_articulos': 0,
            'tasa_rotacion': 0,
            'dias_promedio_stock': 0,
            'eficiencia_general': 0,
            'error': str(e),
            'fecha_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        }

def obtener_distribucion_estados():
    """Obtiene la distribución de artículos por estado"""
    cache_key = "distribucion_estados_v2"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    try:
        total_articulos = Articulo.objects.count()
        
        distribuciones = Articulo.objects.values('estatus_pmo_texto').annotate(
            cantidad=Count('id'),
            valor_total=Sum('costo_unitario_distribucion')
        ).order_by('-cantidad')
        
        resultado = []
        for dist in distribuciones:
            porcentaje = (dist['cantidad'] / total_articulos * 100) if total_articulos > 0 else 0
            resultado.append({
                'estado': dist['estatus_pmo_texto'] or 'Sin Estado',
                'cantidad': dist['cantidad'],
                'porcentaje': round(porcentaje, 1),
                'valor_total': dist['valor_total'] or 0
            })
        
        # Cache por 10 minutos
        cache.set(cache_key, resultado, timeout=600)
        return resultado
        
    except Exception as e:
        logger.error(f"Error en distribución de estados: {e}")
        return []