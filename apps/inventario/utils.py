import logging
from django.db import models
from django.db.models import Count, Sum, Avg, Q, F, Max, Min
from decimal import Decimal
from .models import Articulo
from django.utils import timezone
import traceback

# Configurar logger
logger = logging.getLogger(__name__)

def obtener_metricas_financieras():
    """Calcula métricas financieras basadas en datos reales"""
    
    # Costos totales
    costo_unitario_total = Articulo.objects.filter(
        costo_unitario_distribucion__isnull=False
    ).aggregate(total=Sum('costo_unitario_distribucion'))['total'] or 0
    
    costo_salida_total = Articulo.objects.filter(
        costo_salida_mxn__isnull=False
    ).aggregate(total=Sum('costo_salida_mxn'))['total'] or 0
    
    existencias_mxn_total = Articulo.objects.filter(
        costo_mxn_existencias__isnull=False
    ).aggregate(total=Sum('costo_mxn_existencias'))['total'] or 0
    
    existencias_usd_total = Articulo.objects.filter(
        costo_usd_existencias__isnull=False
    ).aggregate(total=Sum('costo_usd_existencias'))['total'] or 0
    
    # Promedio de costo unitario
    costo_promedio = Articulo.objects.filter(
        costo_unitario_distribucion__isnull=False
    ).aggregate(avg=Avg('costo_unitario_distribucion'))['avg'] or 0
    
    return {
        'valor_total_inventario': float(costo_unitario_total),
        'valor_total_salidas': float(costo_salida_total),
        'valor_existencias_mxn': float(existencias_mxn_total),
        'valor_existencias_usd': float(existencias_usd_total),
        'costo_promedio_unitario': float(costo_promedio),
        'total_proyectos_con_costo': Articulo.objects.filter(costo_unitario_distribucion__isnull=False).count()
    }

def obtener_metricas_inventario():
    """Calcula métricas de inventario y cantidades"""
    
    total_embarcado = Articulo.objects.filter(
        cantidad_embarcada__isnull=False
    ).aggregate(total=Sum('cantidad_embarcada'))['total'] or 0
    
    total_existencia = Articulo.objects.filter(
        existencia_actual__isnull=False
    ).aggregate(total=Sum('existencia_actual'))['total'] or 0
    
    promedio_embarcado = Articulo.objects.filter(
        cantidad_embarcada__isnull=False
    ).aggregate(avg=Avg('cantidad_embarcada'))['avg'] or 0
    
    return {
        'total_unidades_embarcadas': float(total_embarcado),
        'total_unidades_existencia': float(total_existencia),
        'promedio_embarcado': float(promedio_embarcado),
        'proyectos_con_cantidades': Articulo.objects.filter(cantidad_embarcada__isnull=False).count()
    }

def obtener_metricas_estatus():
    """Analiza distribución por estatus PMO"""
    
    # Top estatus
    estatus_distribucion = Articulo.objects.values('estatus_pmo_texto').annotate(
        count=Count('id'),
        porcentaje=Count('id') * 100.0 / Articulo.objects.count()
    ).order_by('-count')
    
    # Proyectos con patrones de retraso
    proyectos_pendientes = Articulo.objects.filter(
        Q(estatus_pmo_texto__icontains='pendiente') |
        Q(historial__icontains='pendiente') |
        Q(observaciones__icontains='pendiente') |
        Q(retrasos_salida__icontains='pendiente')
    ).count()
    
    # Proyectos instalados vs pendientes
    instalados = Articulo.objects.filter(estatus_pmo_texto='Instalado').count()
    pendientes = Articulo.objects.filter(estatus_pmo_texto='Pendiente por confirmar').count()
    
    return {
        'estatus_distribucion': list(estatus_distribucion[:5]),
        'proyectos_pendientes': proyectos_pendientes,
        'proyectos_instalados': instalados,
        'proyectos_por_confirmar': pendientes,
        'tasa_pendientes': (proyectos_pendientes / Articulo.objects.count() * 100) if Articulo.objects.count() > 0 else 0
    }

def obtener_metricas_fabricas():
    """Analiza distribución por fábricas"""
    
    fabricas_distribucion = Articulo.objects.values('fabrica_texto').annotate(
        count=Count('id'),
        valor_total=Sum('costo_unitario_distribucion'),
        unidades_total=Sum('cantidad_embarcada')
    ).order_by('-count')
    
    return {
        'fabricas_distribucion': list(fabricas_distribucion[:5]),
        'total_fabricas_activas': fabricas_distribucion.count(),
        'fabrica_principal': fabricas_distribucion.first() if fabricas_distribucion.exists() else None
    }

def obtener_metricas_proveedores():
    """Analiza distribución por proveedores"""
    
    proveedores_top = Articulo.objects.filter(
        proveedor__isnull=False
    ).exclude(proveedor='').values('proveedor').annotate(
        count=Count('id'),
        valor_total=Sum('costo_unitario_distribucion')
    ).order_by('-count')
    
    return {
        'proveedores_top': list(proveedores_top[:5]),
        'total_proveedores': proveedores_top.count(),
        'proveedor_principal': proveedores_top.first() if proveedores_top.exists() else None
    }

def obtener_metricas_program_managers():
    """Analiza distribución por Program Managers"""
    
    managers_top = Articulo.objects.filter(
        program_manager__isnull=False
    ).exclude(program_manager='').values('program_manager').annotate(
        count=Count('id'),
        valor_gestionado=Sum('costo_unitario_distribucion')
    ).order_by('-count')
    
    return {
        'managers_top': list(managers_top[:5]),
        'total_managers': managers_top.count(),
        'manager_principal': managers_top.first() if managers_top.exists() else None
    }

def obtener_metricas_tipos():
    """Analiza distribución por tipos de proyecto"""
    
    tipos_distribucion = Articulo.objects.values('tipo').annotate(
        count=Count('id'),
        valor_promedio=Avg('costo_unitario_distribucion')
    ).order_by('-count')
    
    return {
        'tipos_distribucion': list(tipos_distribucion[:8]),
        'total_tipos': tipos_distribucion.count(),
        'tipo_principal': tipos_distribucion.first() if tipos_distribucion.exists() else None
    }

def obtener_estadisticas_dashboard_completas():
    """Obtiene todas las métricas para el dashboard principal"""
    
    total_proyectos = Articulo.objects.count()
    año_actual = timezone.now().year
    
    metricas = {
        # Métricas básicas
        'total_proyectos': total_proyectos,
        'proyectos_este_año': Articulo.objects.filter(año=año_actual).count(),
        
        # Métricas financieras
        **obtener_metricas_financieras(),
        
        # Métricas de inventario
        **obtener_metricas_inventario(),
        
        # Métricas de estatus
        **obtener_metricas_estatus(),
        
        # Métricas de fábricas
        **obtener_metricas_fabricas(),
        
        # Métricas de proveedores
        **obtener_metricas_proveedores(),
        
        # Métricas de Program Managers
        **obtener_metricas_program_managers(),
        
        # Métricas de tipos
        **obtener_metricas_tipos(),
        
        # Métricas de órdenes de compra
        **obtener_metricas_ordenes_completas(),
        
        # Métricas adicionales calculadas
        'promedio_embarcado_por_articulo': obtener_metricas_inventario()['promedio_embarcado'],
        'tasa_instalados': (obtener_metricas_estatus()['proyectos_instalados'] / total_proyectos * 100) if total_proyectos > 0 else 0,
        
        # Año de análisis
        'año_analisis': año_actual
    }
    
    return metricas

def obtener_resumen_ejecutivo():
    """Genera un resumen ejecutivo con las métricas más importantes"""
    
    metricas = obtener_estadisticas_dashboard_completas()
    
    return {
        'total_proyectos': metricas['total_proyectos'],
        'valor_total_inventario': metricas['valor_total_inventario'],
        'proyectos_pendientes': metricas['proyectos_pendientes'],
        'tasa_pendientes': round(metricas['tasa_pendientes'], 1),
        'total_proveedores': metricas['total_proveedores'],
        'total_managers': metricas['total_managers'],
        'valor_existencias_total': metricas['valor_existencias_mxn'] + (metricas['valor_existencias_usd'] * 20),  # Aproximación USD a MXN
        'unidades_totales': metricas['total_unidades_existencia']
    }

def obtener_estadisticas_dashboard():
    """Función de compatibilidad - devuelve métricas completas"""
    return obtener_estadisticas_dashboard_completas()

def obtener_metricas_ordenes_compra():
    """
    Obtiene métricas relacionadas con órdenes de compra únicas y artículos por orden
    """
    try:
        from .models import Articulo
        from django.db.models import Count, Avg, Sum, Q
        from decimal import Decimal
        
        # Órdenes de compra únicas
        ordenes_unicas = Articulo.objects.values('orden_compra').distinct().count()
        
        # Artículos por orden de compra (promedio)
        articulos_por_orden = Articulo.objects.values('orden_compra').annotate(
            total_articulos=Count('id')
        ).aggregate(
            promedio=Avg('total_articulos'),
            maximo=Max('total_articulos'),
            minimo=Min('total_articulos')
        )
        
        # Top 10 órdenes con más artículos
        top_ordenes = Articulo.objects.values('orden_compra', 'proveedor').annotate(
            total_articulos=Count('id'),
            valor_total=Sum('costo_unitario_distribucion')
        ).order_by('-total_articulos')[:10]
        
        # Distribución por fábrica
        distribicion_fabricas = Articulo.objects.values('fabrica_texto').annotate(
            ordenes_unicas=Count('orden_compra', distinct=True),
            total_articulos=Count('id'),
            valor_total=Sum('costo_unitario_distribucion')
        ).order_by('-ordenes_unicas')
        
        return {
            'ordenes_unicas': ordenes_unicas,
            'promedio_articulos_por_orden': articulos_por_orden.get('promedio', 0) or 0,
            'max_articulos_por_orden': articulos_por_orden.get('maximo', 0) or 0,
            'min_articulos_por_orden': articulos_por_orden.get('minimo', 0) or 0,
            'top_ordenes': list(top_ordenes),
            'distribicion_fabricas': list(distribicion_fabricas),
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de órdenes: {e}")
        return {
            'ordenes_unicas': 0,
            'promedio_articulos_por_orden': 0,
            'max_articulos_por_orden': 0,
            'min_articulos_por_orden': 0,
            'top_ordenes': [],
            'distribicion_fabricas': [],
        }

def obtener_analisis_ordenes_por_fabrica():
    """
    Análisis detallado de órdenes de compra segmentado por fábrica
    """
    try:
        from .models import Articulo
        from django.db.models import Count, Sum, Avg
        
        analisis_fabricas = []
        
        # Obtener todas las fábricas únicas
        fabricas = Articulo.objects.values_list('fabrica_texto', flat=True).distinct()
        
        for fabrica in fabricas:
            if fabrica:  # Excluir valores nulos
                articulos_fabrica = Articulo.objects.filter(fabrica_texto=fabrica)
                
                # Métricas por fábrica
                ordenes_unicas = articulos_fabrica.values('orden_compra').distinct().count()
                total_articulos = articulos_fabrica.count()
                
                # Estadísticas de artículos por orden en esta fábrica
                articulos_por_orden = articulos_fabrica.values('orden_compra').annotate(
                    count=Count('id')
                ).aggregate(
                    promedio=Avg('count'),
                    maximo=Max('count')
                )
                
                # Valor total por fábrica
                valor_total = articulos_fabrica.aggregate(
                    total=Sum('costo_unitario_distribucion')
                )['total'] or 0
                
                # Proveedores únicos por fábrica
                proveedores_unicos = articulos_fabrica.values('proveedor').distinct().count()
                
                analisis_fabricas.append({
                    'fabrica': fabrica,
                    'ordenes_unicas': ordenes_unicas,
                    'total_articulos': total_articulos,
                    'promedio_articulos_por_orden': round(articulos_por_orden.get('promedio', 0) or 0, 1),
                    'max_articulos_por_orden': articulos_por_orden.get('maximo', 0) or 0,
                    'valor_total': float(valor_total),
                    'proveedores_unicos': proveedores_unicos,
                    'ratio_articulos_ordenes': round(total_articulos / ordenes_unicas if ordenes_unicas > 0 else 0, 2)
                })
        
        # Ordenar por número de órdenes únicas
        analisis_fabricas.sort(key=lambda x: x['ordenes_unicas'], reverse=True)
        
        return analisis_fabricas
        
    except Exception as e:
        logger.error(f"Error en análisis por fábrica: {e}")
        return []

def obtener_metricas_ordenes_completas():
    """
    Combina todas las métricas de órdenes de compra para el dashboard
    """
    try:
        metricas_ordenes = obtener_metricas_ordenes_compra()
        analisis_fabricas = obtener_analisis_ordenes_por_fabrica()
        
        # Calcular totales globales
        total_ordenes = metricas_ordenes['ordenes_unicas']
        total_articulos = Articulo.objects.count()
        ratio_global = round(total_articulos / total_ordenes if total_ordenes > 0 else 0, 2)
        
        return {
            **metricas_ordenes,
            'analisis_fabricas': analisis_fabricas,
            'total_articulos_sistema': total_articulos,
            'ratio_global_articulos_ordenes': ratio_global,
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas completas de órdenes: {e}")
        return {
            'ordenes_unicas': 0,
            'promedio_articulos_por_orden': 0,
            'analisis_fabricas': [],
            'total_articulos_sistema': 0,
            'ratio_global_articulos_ordenes': 0,
        } 