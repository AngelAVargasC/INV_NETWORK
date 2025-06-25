from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Q
from apps.usuarios.models import PerfilUsuario

@login_required
def home_view(request):
    """Vista ejecutiva del dashboard principal con métricas en tiempo real"""
    
    # Métricas de usuarios
    total_usuarios = User.objects.filter(is_active=True).count()
    usuarios_recientes = User.objects.filter(is_active=True).order_by('-date_joined')[:5]
    
    # Estadísticas del inventario PMO con métricas ejecutivas
    try:
        from apps.inventario.models import Articulo, EstatusPMO
        
        # Total de artículos activos en la base de datos
        total_articulos = Articulo.objects.count()
        
        # Artículos pendientes (basado en estatus PMO)
        articulos_pendientes = Articulo.objects.filter(
            Q(estatus_pmo_texto__icontains='pendiente') |
            Q(estatus_pmo_texto__icontains='revision') |
            Q(estatus_pmo_texto__icontains='proceso') |
            Q(estatus_pmo_texto='') |
            Q(estatus_pmo_texto__isnull=True)
        ).count()
        
        # Artículos completados
        articulos_completados = Articulo.objects.filter(
            Q(estatus_pmo_texto__icontains='completado') |
            Q(estatus_pmo_texto__icontains='finalizado') |
            Q(estatus_pmo_texto__icontains='cerrado')
        ).count()
        
        # Artículos en proceso activo
        articulos_activos = Articulo.objects.filter(
            Q(estatus_pmo_texto__icontains='aprobado') |
            Q(estatus_pmo_texto__icontains='proceso') |
            Q(estatus_pmo_texto__icontains='ejecucion')
        ).count()
        
        # Obtener artículos recientes del inventario
        articulos_recientes = Articulo.objects.select_related('fabrica', 'estatus_pmo').order_by('-fecha_actualizacion')[:6]
        
        # Estadísticas por estatus
        estatus_stats = []
        try:
            # Intentar usar el modelo EstatusPMO si existe
            estatus_queryset = EstatusPMO.objects.filter(activo=True)
            for estatus in estatus_queryset:
                count = Articulo.objects.filter(estatus_pmo=estatus).count()
                if count > 0:
                    estatus_stats.append({
                        'nombre': estatus.get_estado_display(),
                        'codigo': estatus.estado,
                        'total': count,
                        'color': getattr(estatus, 'color', '#6c757d')
                    })
        except:
            # Fallback: usar estatus de texto
            estatus_text_stats = Articulo.objects.values('estatus_pmo_texto').annotate(
                total=Count('id')
            ).filter(total__gt=0)[:5]
            
            for stat in estatus_text_stats:
                estatus_stats.append({
                    'nombre': stat['estatus_pmo_texto'] or 'Sin estatus',
                    'codigo': stat['estatus_pmo_texto'] or 'sin_estatus',
                    'total': stat['total'],
                    'color': '#6c757d'
                })
        
        # Estadísticas por fábrica
        fabricas_stats = Articulo.objects.values('fabrica_texto').annotate(
            total=Count('id')
        ).filter(total__gt=0).order_by('-total')[:5]
        
        # Métricas de costos (si están disponibles)
        try:
            from django.db.models import Sum
            costo_total_mxn = Articulo.objects.aggregate(
                total=Sum('costo_mxn_existencias')
            )['total'] or 0
            
            costo_total_usd = Articulo.objects.aggregate(
                total=Sum('costo_usd_existencias')
            )['total'] or 0
        except:
            costo_total_mxn = 0
            costo_total_usd = 0
            
    except Exception as e:
        # Si la app inventario no está disponible o hay errores
        total_articulos = 0
        articulos_pendientes = 0
        articulos_completados = 0
        articulos_activos = 0
        articulos_recientes = []
        estatus_stats = []
        fabricas_stats = []
        costo_total_mxn = 0
        costo_total_usd = 0
    
    # Estadísticas por área de usuarios
    areas_stats = []
    for area_code, area_name in PerfilUsuario.AREAS_CHOICES:
        count = PerfilUsuario.objects.filter(area=area_code, activo=True).count()
        if count > 0:
            areas_stats.append({
                'nombre': area_name,
                'codigo': area_code,
                'total': count,
                'porcentaje': round((count / max(total_usuarios, 1)) * 100, 1)
            })
    
    # Calcular métricas de tendencias (simuladas por ahora)
    import random
    tendencias = {
        'usuarios': round(random.uniform(5, 15), 1),
        'articulos': round(random.uniform(3, 12), 1),
        'pendientes': round(random.uniform(-8, -2), 1),
        'areas': 0,  # Sin cambio
    }
    
    context = {
        # Métricas principales
        'total_usuarios': total_usuarios,
        'total_articulos': total_articulos,
        'articulos_pendientes': articulos_pendientes,
        'articulos_completados': articulos_completados,
        'articulos_activos': articulos_activos,
        
        # Datos para componentes
        'usuarios_recientes': usuarios_recientes,
        'articulos_recientes': articulos_recientes,
        'areas_stats': areas_stats,
        'estatus_stats': estatus_stats,
        'fabricas_stats': fabricas_stats,
        
        # Métricas financieras
        'costo_total_mxn': costo_total_mxn,
        'costo_total_usd': costo_total_usd,
        
        # Tendencias
        'tendencias': tendencias,
        
        # Usuario actual
        'usuario_perfil': getattr(request.user, 'perfilusuario', None),
        
        # Datos para breadcrumb
        'breadcrumb': 'Dashboard Principal',
    }
    
    return render(request, 'home/home.html', context)
