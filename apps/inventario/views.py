from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.utils import timezone
import pandas as pd
import os
import tempfile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import time

from .models import Articulo, Fabrica, EstatusPMO, Categoria, SeguimientoPMO, ImportacionDatos
from .forms import ImportacionArchivosForm, FiltroArticulosForm, ArticuloForm, CambioEstatusForm
from .utils import (
    obtener_estadisticas_dashboard_completas, 
    obtener_resumen_ejecutivo,
    obtener_metricas_financieras,
    obtener_metricas_estatus,
    obtener_metricas_ordenes_completas
)
from .utils_optimizadas import obtener_dashboard_completo_optimizado

@login_required
def dashboard(request):
    """Vista principal del dashboard con métricas optimizadas básicas"""
    try:
        # Métricas básicas optimizadas (una sola consulta cada una)
        total_proyectos = Articulo.objects.count()
        
        # Usar agregaciones simples para evitar cuelgues
        from django.db.models import Sum, Count, Avg
        
        # Métricas financieras básicas
        valor_total = Articulo.objects.filter(
            costo_unitario_distribucion__isnull=False
        ).aggregate(total=Sum('costo_unitario_distribucion'))['total'] or 0
        
        # Métricas de inventario básicas
        total_embarcado = Articulo.objects.filter(
            cantidad_embarcada__isnull=False
        ).aggregate(total=Sum('cantidad_embarcada'))['total'] or 0
        
        total_existencia = Articulo.objects.filter(
            existencia_actual__isnull=False
        ).aggregate(total=Sum('existencia_actual'))['total'] or 0
        
        promedio_embarcado = Articulo.objects.filter(
            cantidad_embarcada__isnull=False
        ).aggregate(avg=Avg('cantidad_embarcada'))['avg'] or 0
        
        # Métricas de estatus básicas
        proyectos_pendientes = Articulo.objects.filter(
            estatus_pmo_texto__icontains='Pendiente'
        ).count()
        
        proyectos_instalados = Articulo.objects.filter(
            estatus_pmo_texto='Instalado'
        ).count()
        
        # Métricas de órdenes básicas (optimizadas)
        ordenes_unicas = Articulo.objects.values('orden_compra').distinct().count()
        
        # Promedio simple de artículos por orden
        if ordenes_unicas > 0:
            promedio_articulos_por_orden = round(total_proyectos / ordenes_unicas, 1)
            ratio_global_articulos_ordenes = round(total_proyectos / ordenes_unicas, 1)
        else:
            promedio_articulos_por_orden = 0
            ratio_global_articulos_ordenes = 0
        
        # Max artículos por orden (consulta simple)
        max_articulos_por_orden = Articulo.objects.values('orden_compra').annotate(
            count=Count('id')
        ).aggregate(max_count=Max('count'))['max_count'] or 0
        
        # Calcular tasas
        tasa_pendientes = (proyectos_pendientes / total_proyectos * 100) if total_proyectos > 0 else 0
        tasa_instalados = (proyectos_instalados / total_proyectos * 100) if total_proyectos > 0 else 0
        
        # Existencias financieras básicas
        valor_existencias_mxn = Articulo.objects.filter(
            costo_mxn_existencias__isnull=False
        ).aggregate(total=Sum('costo_mxn_existencias'))['total'] or 0
        
        valor_existencias_usd = Articulo.objects.filter(
            costo_usd_existencias__isnull=False
        ).aggregate(total=Sum('costo_usd_existencias'))['total'] or 0
        
        costo_promedio_unitario = Articulo.objects.filter(
            costo_unitario_distribucion__isnull=False
        ).aggregate(avg=Avg('costo_unitario_distribucion'))['avg'] or 0
        
        # Métricas adicionales para el resumen ejecutivo
        total_fabricas_activas = Articulo.objects.values('fabrica_texto').distinct().count()
        proyectos_por_confirmar = Articulo.objects.filter(
            estatus_pmo_texto__icontains='confirmar'
        ).count()
        
        contexto = {
            # Métricas principales
            'total_proyectos': total_proyectos,
            'valor_total_inventario': float(valor_total),
            'proyectos_pendientes': proyectos_pendientes,
            'tasa_pendientes': round(tasa_pendientes, 1),
            
            # Métricas de órdenes
            'ordenes_unicas': ordenes_unicas,
            'promedio_articulos_por_orden': promedio_articulos_por_orden,
            'max_articulos_por_orden': max_articulos_por_orden,
            'ratio_global_articulos_ordenes': ratio_global_articulos_ordenes,
            
            # Métricas de inventario
            'total_unidades_embarcadas': float(total_embarcado),
            'total_unidades_existencia': float(total_existencia),
            'promedio_embarcado_por_articulo': float(promedio_embarcado),
            
            # Métricas financieras
            'valor_existencias_mxn': float(valor_existencias_mxn),
            'valor_existencias_usd': float(valor_existencias_usd),
            'costo_promedio_unitario': float(costo_promedio_unitario),
            
            # Otras métricas
            'proyectos_instalados': proyectos_instalados,
            'tasa_instalados': round(tasa_instalados, 1),
            'total_fabricas_activas': total_fabricas_activas,
            'proyectos_por_confirmar': proyectos_por_confirmar,
            'fecha_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        }
        
        return render(request, 'inventario/dashboard_att.html', contexto)
        
    except Exception as e:
        messages.error(request, f'Error al cargar el dashboard: {str(e)}')
        # Fallback con métricas mínimas
        contexto_basico = {
            'total_proyectos': Articulo.objects.count(),
            'valor_total_inventario': 0,
            'proyectos_pendientes': 0,
            'tasa_pendientes': 0,
            'ordenes_unicas': 0,
            'promedio_articulos_por_orden': 0,
            'max_articulos_por_orden': 0,
            'ratio_global_articulos_ordenes': 0,
            'total_unidades_embarcadas': 0,
            'total_unidades_existencia': 0,
            'promedio_embarcado_por_articulo': 0,
            'valor_existencias_mxn': 0,
            'valor_existencias_usd': 0,
            'costo_promedio_unitario': 0,
            'proyectos_instalados': 0,
            'tasa_instalados': 0,
            'error': str(e),
            'fecha_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        }
        return render(request, 'inventario/dashboard_att.html', contexto_basico)

@login_required
def dashboard_debug(request):
    """Vista de debug para identificar qué métrica está causando problemas"""
    debug_info = []
    
    try:
        # Test cada métrica individualmente con tiempo
        start_time = time.time()
        total_proyectos = Articulo.objects.count()
        debug_info.append(f"✅ Total proyectos: {total_proyectos} ({time.time() - start_time:.2f}s)")
        
        start_time = time.time()
        valor_total = Articulo.objects.filter(
            costo_unitario_distribucion__isnull=False
        ).aggregate(total=Sum('costo_unitario_distribucion'))['total'] or 0
        debug_info.append(f"✅ Valor total: {valor_total} ({time.time() - start_time:.2f}s)")
        
        start_time = time.time()
        ordenes_unicas = Articulo.objects.values('orden_compra').distinct().count()
        debug_info.append(f"✅ Órdenes únicas: {ordenes_unicas} ({time.time() - start_time:.2f}s)")
        
        start_time = time.time()
        max_articulos = Articulo.objects.values('orden_compra').annotate(
            count=Count('id')
        ).aggregate(max_count=Max('count'))['max_count'] or 0
        debug_info.append(f"✅ Max artículos por orden: {max_articulos} ({time.time() - start_time:.2f}s)")
        
        # Test métricas más complejas
        start_time = time.time()
        from .utils import obtener_metricas_financieras
        metricas_fin = obtener_metricas_financieras()
        debug_info.append(f"✅ Métricas financieras: OK ({time.time() - start_time:.2f}s)")
        
        start_time = time.time()
        from .utils import obtener_metricas_ordenes_compra
        metricas_ord = obtener_metricas_ordenes_compra()
        debug_info.append(f"✅ Métricas órdenes: OK ({time.time() - start_time:.2f}s)")
        
        start_time = time.time()
        from .utils import obtener_analisis_ordenes_por_fabrica
        analisis_fab = obtener_analisis_ordenes_por_fabrica()
        debug_info.append(f"❓ Análisis fábricas: {len(analisis_fab)} fábricas ({time.time() - start_time:.2f}s)")
        
    except Exception as e:
        debug_info.append(f"❌ ERROR: {str(e)}")
    
    return HttpResponse(f"<h2>Debug Dashboard</h2><pre>" + "\n".join(debug_info) + "</pre>")

class ArticuloFilterMixin:
    """Mixin para compartir lógica de filtrado entre vistas"""
    
    def apply_filters(self, queryset):
        """Aplica todos los filtros a un queryset de artículos"""
        # Búsqueda global optimizada
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(id_pmo__icontains=q) |
                Q(nombre_proyecto__icontains=q) |
                Q(articulo__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(proveedor__icontains=q) |
                Q(nombre_proyecto_recibo__icontains=q) |
                Q(orden_compra__icontains=q) |
                Q(program_manager__icontains=q) |
                Q(estatus_pmo_texto__icontains=q) |
                Q(avp__icontains=q) |
                Q(tipo__icontains=q) |
                Q(fabrica_texto__icontains=q)
            )
        
        # Filtros específicos por columna - Optimizado
        filtros_config = {
            'año': ('año', int),
            'articulo': ('articulo__icontains', str),
            'descripcion': ('descripcion__icontains', str),
            'proveedor': ('proveedor__icontains', str),
            'proyecto_recibo': ('nombre_proyecto_recibo__icontains', str),
            'orden_compra': ('orden_compra__icontains', str),
            'id_pmo': ('id_pmo__icontains', str),
            'nombre_proyecto': ('nombre_proyecto__icontains', str),
            'manager': ('program_manager__icontains', str),
            'estatus': ('estatus_pmo_texto__icontains', str),
            'avp': ('avp__icontains', str),
            'tipo': ('tipo__icontains', str),
            'fabrica': ('fabrica_texto__icontains', str),
        }
        
        # Aplicar filtros de texto con validación
        for param, (lookup, tipo) in filtros_config.items():
            value = self.request.GET.get(param, '').strip()
            if value:
                try:
                    if tipo == int:
                        value = int(value)
                    queryset = queryset.filter(**{lookup: value})
                except (ValueError, TypeError):
                    continue  # Ignorar valores inválidos silenciosamente
        
        # Filtros de rango numérico optimizados
        filtros_numericos = [
            ('costo_min', 'costo_unitario_distribucion__gte', float),
            ('costo_max', 'costo_unitario_distribucion__lte', float),
            ('existencia_min', 'existencia_actual__gte', int),
        ]
        
        for param, lookup, tipo in filtros_numericos:
            value = self.request.GET.get(param, '').strip()
            if value:
                try:
                    queryset = queryset.filter(**{lookup: tipo(value)})
                except (ValueError, TypeError):
                    continue  # Ignorar valores inválidos silenciosamente
        
        return queryset

class ArticuloListView(LoginRequiredMixin, ArticuloFilterMixin, ListView):
    """Vista de lista de artículos con filtros avanzados"""
    model = Articulo
    template_name = 'inventario/articulo_list.html'
    context_object_name = 'articulos'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Articulo.objects.select_related('fabrica', 'estatus_pmo').all()
        return self.apply_filters(queryset).order_by('-fecha_actualizacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información de filtros activos para métricas
        context['total_sin_filtros'] = Articulo.objects.count()
        context['filtros_aplicados'] = bool(self.request.GET)
        return context

class ArticuloListFullscreenView(LoginRequiredMixin, ArticuloFilterMixin, ListView):
    """Vista de lista de artículos en pantalla completa con filtros avanzados"""
    model = Articulo
    template_name = 'inventario/articulo_list_fullscreen.html'
    context_object_name = 'articulos'
    paginate_by = 50  # Más registros por página en fullscreen
    
    def get_queryset(self):
        # Optimización: select_related para evitar consultas adicionales
        queryset = Articulo.objects.select_related('fabrica', 'estatus_pmo').all()
        return self.apply_filters(queryset).order_by('-fecha_actualizacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_fullscreen'] = True
        context['total_sin_filtros'] = Articulo.objects.count()
        context['filtros_aplicados'] = bool(self.request.GET)
        return context

class ArticuloDetailView(LoginRequiredMixin, DetailView):
    """Vista detallada de un artículo"""
    model = Articulo
    template_name = 'inventario/articulo_detail.html'
    context_object_name = 'articulo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seguimientos'] = self.object.seguimientos.all()[:10] if hasattr(self.object, 'seguimientos') else []
        context['cambio_estatus_form'] = CambioEstatusForm()
        return context

class ArticuloCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo artículo"""
    model = Articulo
    form_class = ArticuloForm
    template_name = 'inventario/articulo_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Artículo {form.instance.id_pmo} creado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return f'/inventario/articulos/{self.object.pk}/'

class ArticuloUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar un artículo"""
    model = Articulo
    form_class = ArticuloForm
    template_name = 'inventario/articulo_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Artículo {form.instance.id_pmo} actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return f'/inventario/articulos/{self.object.pk}/'

@login_required
def cambiar_estatus_articulo(request, pk):
    """Vista para cambiar el estatus de un artículo"""
    articulo = get_object_or_404(Articulo, pk=pk)
    
    if request.method == 'POST':
        form = CambioEstatusForm(request.POST, request.FILES)
        if form.is_valid():
            estatus_anterior = articulo.estatus_pmo
            nuevo_estatus = form.cleaned_data['nuevo_estatus']
            
            # Crear seguimiento
            seguimiento = SeguimientoPMO.objects.create(
                articulo=articulo,
                estatus_anterior=estatus_anterior,
                estatus_nuevo=nuevo_estatus,
                comentarios=form.cleaned_data['comentarios'],
                adjuntos=form.cleaned_data.get('adjuntos'),
                usuario=request.user
            )
            
            # Actualizar artículo
            articulo.estatus_pmo = nuevo_estatus
            articulo.save()
            
            messages.success(
                request, 
                f'Estatus del artículo {articulo.id_pmo} cambiado de '
                f'{estatus_anterior.get_estado_display()} a {nuevo_estatus.get_estado_display()}'
            )
            
            return redirect('inventario:articulo_detail', pk=articulo.pk)
    
    return redirect('inventario:articulo_detail', pk=pk)

@login_required
def importar_datos(request):
    """Vista ejecutiva para importar datos desde Excel con todas las 23 columnas"""
    if request.method == 'POST':
        try:
            # Validar que se haya enviado un archivo
            if 'archivo' not in request.FILES:
                messages.error(request, 'Por favor seleccione un archivo para importar.')
                return redirect('inventario:importar_datos')
            
            archivo = request.FILES['archivo']
            sobrescribir = request.POST.get('sobrescribir_duplicados', False)
            descripcion = request.POST.get('descripcion', '')
            
            # Validar tipo de archivo
            allowed_extensions = ['.xlsx', '.xls', '.csv']
            file_extension = os.path.splitext(archivo.name)[1].lower()
            if file_extension not in allowed_extensions:
                messages.error(request, 'Tipo de archivo no válido. Use Excel (.xlsx, .xls) o CSV (.csv).')
                return redirect('inventario:importar_datos')
            
            # Validar tamaño (100MB)
            if archivo.size > 100 * 1024 * 1024:
                messages.error(request, 'El archivo es demasiado grande. Máximo 100MB permitido.')
                return redirect('inventario:importar_datos')
            
            # Crear registro de importación
            importacion = ImportacionDatos.objects.create(
                usuario=request.user,
                archivo_original=archivo.name,
                notas=descripcion,
                total_registros=0
            )
            
            # PROCESAR ARCHIVO - IMPORTACIÓN REAL DE 23 COLUMNAS
            articulos_procesados = 0
            try:
                # Leer archivo Excel/CSV
                if file_extension in ['.xlsx', '.xls']:
                    df = pd.read_excel(archivo)
                else:
                    df = pd.read_csv(archivo)
                
                print(f"🚀 Iniciando importación OPTIMIZADA de {len(df)} registros con {len(df.columns)} columnas...")
                
                # ELIMINAR TODOS LOS DATOS EXISTENTES si está marcado sobrescribir
                if sobrescribir:
                    deleted_count = Articulo.objects.all().count()
                    Articulo.objects.all().delete()
                    print(f"🗑️ Eliminados {deleted_count} registros existentes")
                
                # OPTIMIZACIÓN: Usar bulk operations para máxima velocidad
                import re
                from django.db import transaction
                from django.conf import settings
                
                articulos_batch = []
                # Optimizar batch_size según la base de datos
                db_engine = settings.DATABASES['default']['ENGINE']
                if 'mysql' in db_engine:
                    batch_size = 2000  # MySQL maneja lotes más grandes eficientemente
                elif 'postgresql' in db_engine:
                    batch_size = 5000  # PostgreSQL es muy eficiente con lotes grandes
                else:
                    batch_size = getattr(settings, 'BULK_BATCH_SIZE', 1000)  # SQLite
                articulos_procesados = 0
                errores = 0
                
                # Función helper para procesar valores de forma segura y rápida
                def safe_float(value):
                    try:
                        if pd.notna(value) and str(value).strip() != '':
                            return float(value)
                    except (ValueError, TypeError):
                        pass
                    return 0.0
                
                def safe_int(value):
                    try:
                        if pd.notna(value) and str(value).strip() != '':
                            return int(float(value))
                    except (ValueError, TypeError):
                        pass
                    return 0
                
                def safe_str(value):
                    try:
                        if pd.notna(value):
                            return str(value).strip()
                    except:
                        pass
                    return ''
                
                # PROCESAMIENTO MASIVO con transacción optimizada
                # Configuraciones específicas para MySQL
                if 'mysql' in db_engine:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SET autocommit = 0")
                        cursor.execute("SET unique_checks = 0") 
                        cursor.execute("SET foreign_key_checks = 0")
                
                with transaction.atomic():
                    for index, row in df.iterrows():
                        try:
                            # Extraer año numérico de forma optimizada
                            año_texto = safe_str(row.get('Año'))
                            año_numero = 2025  # Valor por defecto
                            if año_texto:
                                match = re.search(r'\b(20\d{2})\b', año_texto)
                                if match:
                                    año_numero = int(match.group(1))
                                elif año_texto.isdigit() and len(año_texto) == 4:
                                    año_numero = int(año_texto)
                            
                            # Crear objeto Articulo sin guardarlo (más rápido)
                            articulo = Articulo(
                                año=año_numero,
                                articulo=safe_str(row.get('Articulo')),
                                descripcion=safe_str(row.get('Descripción')),
                                proveedor=safe_str(row.get('Proveedor')),
                                nombre_proyecto_recibo=safe_str(row.get('Nombre de proyecto recibo')),
                                id_pmo=safe_str(row.get('ID de PMO')) or f'PMO-{index+1}',
                                nombre_proyecto=safe_str(row.get('Nombre de Proyecto')),
                                program_manager=safe_str(row.get('Program Manager')),
                                estatus_pmo_texto=safe_str(row.get('Estatus PMO')),
                                fecha_implementacion=safe_str(row.get('Fecha de Implementación Si/No')),
                                historial=safe_str(row.get('Historial')),
                                observaciones=safe_str(row.get('Observaciones')),
                                retrasos_salida=safe_str(row.get('Retrasos en salida')),
                                avp=safe_str(row.get('AVP')),
                                tipo=safe_str(row.get('Tipo')),
                                fabrica_texto=safe_str(row.get('Fabrica')),
                                orden_compra=safe_str(row.get('Orden de Compra')),
                                costo_unitario_distribucion=safe_float(row.get('COSTO UNITARIO DISTRIBUCION')),
                                cantidad_embarcada=safe_float(row.get('Cantidad Embarcada')),
                                costo_salida_mxn=safe_float(row.get('Costo Salida $MXN')),
                                existencia_actual=safe_int(row.get('Existencia Actual')),
                                costo_mxn_existencias=safe_float(row.get('Costo $MXN Existencias')),
                                costo_usd_existencias=safe_float(row.get('Costo $USD Existencias')),
                            )
                            
                            articulos_batch.append(articulo)
                            
                            # BULK CREATE cada batch_size registros
                            if len(articulos_batch) >= batch_size:
                                created_objects = Articulo.objects.bulk_create(articulos_batch, ignore_conflicts=True)
                                articulos_procesados += len(created_objects)
                                print(f"⚡ Procesados {articulos_procesados} artículos (lote de {len(articulos_batch)})...")
                                articulos_batch = []  # Limpiar batch
                                
                        except Exception as e:
                            errores += 1
                            if errores <= 10:  # Solo mostrar primeros 10 errores
                                print(f"❌ Error en fila {index + 1}: {str(e)}")
                            if errores > 100:
                                print("🛑 Demasiados errores, deteniendo importación")
                                break
                    
                    # Procesar el último lote si quedan registros
                    if articulos_batch:
                        created_objects = Articulo.objects.bulk_create(articulos_batch, ignore_conflicts=True)
                        articulos_procesados += len(created_objects)
                        print(f"🏁 Procesado lote final de {len(articulos_batch)} artículos")
                
                # Restaurar configuraciones de MySQL
                if 'mysql' in db_engine:
                    with connection.cursor() as cursor:
                        cursor.execute("SET unique_checks = 1")
                        cursor.execute("SET foreign_key_checks = 1") 
                        cursor.execute("SET autocommit = 1")
                
                print(f"✅ Importación completada: {articulos_procesados} artículos procesados, {errores} errores")
                
                # Actualizar registro de importación
                importacion.total_registros = len(df)
                importacion.registros_exitosos = articulos_procesados
                importacion.registros_fallidos = errores
                importacion.log_errores = f"Errores: {errores}" if errores > 0 else ""
                importacion.save()
                
                messages.success(
                    request, 
                    f'¡Importación exitosa! Se procesaron {articulos_procesados} artículos del archivo "{archivo.name}". Errores: {errores}'
                )
                
            except Exception as e:
                importacion.log_errores = str(e)
                importacion.registros_fallidos = importacion.total_registros
                importacion.registros_exitosos = 0
                importacion.save()
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
            
            return redirect('inventario:importar_datos')
            
        except Exception as e:
            messages.error(request, f'Error general en la importación: {str(e)}')
            return redirect('inventario:importar_datos')
    
    # GET request - mostrar formulario con historial
    # Obtener importaciones recientes del usuario
    importaciones_recientes = ImportacionDatos.objects.filter(
        usuario=request.user
    ).order_by('-fecha_importacion')[:5]  # Últimas 5 importaciones
    
    # Estadísticas de importación
    total_importaciones = ImportacionDatos.objects.filter(usuario=request.user).count()
    importaciones_exitosas = ImportacionDatos.objects.filter(
        usuario=request.user, 
        registros_fallidos=0
    ).count()
    
    context = {
        'importaciones_recientes': importaciones_recientes,
        'total_importaciones': total_importaciones,
        'importaciones_exitosas': importaciones_exitosas,
        'tasa_exito': round((importaciones_exitosas / total_importaciones * 100) if total_importaciones > 0 else 0, 1),
        'user_profile': getattr(request.user, 'perfilusuario', None),
    }
    
    return render(request, 'inventario/importar_datos.html', context)

@login_required
def estadisticas_api(request):
    """API para estadísticas del dashboard"""
    data = {
        'total_articulos': Articulo.objects.count(),
        'por_año': list(Articulo.objects.values('año').annotate(count=Count('id')).order_by('año')),
        'por_estatus': list(Articulo.objects.values('estatus_pmo_texto').annotate(count=Count('id'))),
        'por_fabrica': list(Articulo.objects.values('fabrica_texto').annotate(count=Count('id'))),
    }
    return JsonResponse(data)

@login_required
def exportar_articulos(request):
    """Exportar artículos a Excel"""
    # Obtener artículos filtrados (reutilizar lógica de filtros)
    view = ArticuloListView()
    view.request = request
    articulos = view.get_queryset()
    
    # Crear DataFrame
    data = []
    for articulo in articulos:
        data.append({
            'Código': articulo.id_pmo,
            'Denominación': articulo.articulo,
            'Fábrica': articulo.fabrica_texto,
            'Categoría': articulo.categoria.nombre if hasattr(articulo, 'categoria') else '',
            'Estatus PMO': articulo.estatus_pmo_texto,
            'Año': articulo.año,
            'Progreso %': articulo.progreso_porcentaje if hasattr(articulo, 'progreso_porcentaje') else '',
            'Prioridad': articulo.prioridad if hasattr(articulo, 'prioridad') else '',
            'Costo Estimado': articulo.costo_estimado if hasattr(articulo, 'costo_estimado') else '',
            'Costo Real': articulo.costo_real if hasattr(articulo, 'costo_real') else '',
            'Moneda': articulo.moneda if hasattr(articulo, 'moneda') else '',
            'Fecha Inicio': articulo.fecha_inicio if hasattr(articulo, 'fecha_inicio') else '',
            'Fecha Estimada Fin': articulo.fecha_estimada_fin if hasattr(articulo, 'fecha_estimada_fin') else '',
            'Fecha Real Fin': articulo.fecha_real_fin if hasattr(articulo, 'fecha_real_fin') else '',
            'Responsable': articulo.responsable.get_full_name() if hasattr(articulo, 'responsable') else '',
            'Área': articulo.area_responsable if hasattr(articulo, 'area_responsable') else '',
            'Retrasado': 'Sí' if hasattr(articulo, 'esta_retrasado') and articulo.esta_retrasado else 'No',
            'Última Actualización': articulo.fecha_actualizacion if hasattr(articulo, 'fecha_actualizacion') else '',
        })
    
    df = pd.DataFrame(data)
    
    # Crear respuesta Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="inventario_pmo_{timezone.now().strftime("%Y%m%d_%H%M")}.xlsx"'
    
    df.to_excel(response, index=False, sheet_name='Inventario PMO')
    
    return response

@login_required
def reporte_fabricas(request):
    """Reporte detallado por fábricas"""
    fabricas_stats = Fabrica.objects.filter(activa=True).annotate(
        total_articulos=Count('articulos'),
        articulos_completados=Count('articulos', filter=Q(
            articulos__estatus_pmo_texto__icontains='completado'
        )),
        costo_total=Sum('articulos__costo_unitario_distribucion')
    ).order_by('-total_articulos')
    
    context = {
        'fabricas_stats': fabricas_stats,
    }
    
    return render(request, 'inventario/reporte_fabricas.html', context)

@csrf_exempt
@require_http_methods(["GET"])
def api_metricas_dashboard(request):
    """API endpoint para obtener métricas del dashboard en JSON"""
    try:
        metricas = obtener_estadisticas_dashboard_completas()
        return JsonResponse(metricas, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_resumen_ejecutivo(request):
    """API endpoint para obtener resumen ejecutivo en JSON"""
    try:
        resumen = obtener_resumen_ejecutivo()
        return JsonResponse(resumen, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_metricas_financieras(request):
    """API endpoint para métricas financieras detalladas"""
    try:
        metricas = obtener_metricas_financieras()
        return JsonResponse(metricas, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_analisis_estatus(request):
    """API endpoint para análisis de estatus"""
    try:
        metricas = obtener_metricas_estatus()
        return JsonResponse(metricas, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def articulo_list(request):
    """Lista paginada de artículos con filtros"""
    # Obtener todos los artículos
    articulos = Articulo.objects.all().order_by('-id')
    
    # Aplicar filtros si se proporcionan
    busqueda = request.GET.get('busqueda', '')
    estatus = request.GET.get('estatus', '')
    fabrica = request.GET.get('fabrica', '')
    año = request.GET.get('año', '')
    
    if busqueda:
        articulos = articulos.filter(
            Q(articulo__icontains=busqueda) |
            Q(id_pmo__icontains=busqueda) |
            Q(nombre_proyecto__icontains=busqueda) |
            Q(proveedor__icontains=busqueda)
        )
    
    if estatus:
        articulos = articulos.filter(estatus_pmo_texto__icontains=estatus)
    
    if fabrica:
        articulos = articulos.filter(fabrica_texto__icontains=fabrica)
    
    if año:
        articulos = articulos.filter(año=año)
    
    # Paginación
    paginator = Paginator(articulos, 25)  # 25 por página como solicitaste
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcular rango de elementos mostrados
    start_index = (page_obj.number - 1) * paginator.per_page + 1
    end_index = min(start_index + paginator.per_page - 1, paginator.count)
    
    # Obtener opciones para filtros
    fabricas_disponibles = Articulo.objects.values_list('fabrica_texto', flat=True).distinct().order_by('fabrica_texto')
    estatus_disponibles = Articulo.objects.values_list('estatus_pmo_texto', flat=True).distinct().order_by('estatus_pmo_texto')
    años_disponibles = Articulo.objects.values_list('año', flat=True).distinct().order_by('-año')
    
    contexto = {
        'page_obj': page_obj,
        'total_articulos': paginator.count,
        'start_index': start_index,
        'end_index': end_index,
        'busqueda': busqueda,
        'estatus_filtro': estatus,
        'fabrica_filtro': fabrica,
        'año_filtro': año,
        'fabricas_disponibles': fabricas_disponibles,
        'estatus_disponibles': estatus_disponibles,
        'años_disponibles': años_disponibles,
    }
    
    return render(request, 'inventario/articulo_list.html', contexto)

def articulo_detail(request, pk):
    """Detalle de un artículo específico"""
    articulo = get_object_or_404(Articulo, pk=pk)
    return render(request, 'inventario/articulo_detail.html', {'articulo': articulo})

def articulo_create(request):
    """Crear un nuevo artículo"""
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artículo creado exitosamente.')
            return redirect('inventario:articulo_list')
    else:
        form = ArticuloForm()
    
    return render(request, 'inventario/articulo_form.html', {
        'form': form,
        'titulo': 'Crear Artículo'
    })

def articulo_edit(request, pk):
    """Editar un artículo existente"""
    articulo = get_object_or_404(Articulo, pk=pk)
    
    if request.method == 'POST':
        form = ArticuloForm(request.POST, instance=articulo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artículo actualizado exitosamente.')
            return redirect('inventario:articulo_detail', pk=pk)
    else:
        form = ArticuloForm(instance=articulo)
    
    return render(request, 'inventario/articulo_form.html', {
        'form': form,
        'titulo': 'Editar Artículo',
        'articulo': articulo
    })
