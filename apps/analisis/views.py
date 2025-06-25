from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
import os
import json
import tempfile
import threading

from .models import ProcesamientoAnalisis, LogProcesamiento
from .forms import AnalisisArchivosForm
from .utils import InventoryProcessor, save_uploaded_file_to_temp
from .diccionario import ARCHIVO_CONFIGS

@login_required
def dashboard_analisis(request):
    """
    Vista principal del dashboard de análisis
    """
    # Obtener estadísticas del usuario
    procesamientos_usuario = ProcesamientoAnalisis.objects.filter(usuario=request.user)
    
    # Estadísticas generales
    total_procesamientos = procesamientos_usuario.count()
    procesamientos_exitosos = procesamientos_usuario.filter(estado='completado').count()
    procesamientos_error = procesamientos_usuario.filter(estado='error').count()
    procesamientos_en_proceso = procesamientos_usuario.filter(estado='procesando').count()
    
    # Últimos procesamientos
    ultimos_procesamientos = procesamientos_usuario.order_by('-fecha_procesamiento')[:5]
    
    # Calcular tasa de éxito
    tasa_exito = 0
    if total_procesamientos > 0:
        tasa_exito = round((procesamientos_exitosos / total_procesamientos) * 100, 1)
    
    # Estadísticas de registros procesados
    total_registros_procesados = sum([p.total_registros_aging for p in procesamientos_usuario if p.total_registros_aging])
    
    context = {
        'total_procesamientos': total_procesamientos,
        'procesamientos_exitosos': procesamientos_exitosos,
        'procesamientos_error': procesamientos_error,
        'procesamientos_en_proceso': procesamientos_en_proceso,
        'tasa_exito': tasa_exito,
        'total_registros_procesados': total_registros_procesados,
        'ultimos_procesamientos': ultimos_procesamientos,
        'archivo_configs': ARCHIVO_CONFIGS,
    }
    
    return render(request, 'analisis/dashboard.html', context)

@login_required
def procesar_archivos(request):
    """
    Vista para procesar archivos de análisis
    """
    if request.method == 'POST':
        form = AnalisisArchivosForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Crear registro de procesamiento
                procesamiento = ProcesamientoAnalisis.objects.create(
                    usuario=request.user,
                    archivo_aging=form.cleaned_data['archivo_aging'].name,
                    archivo_pipeline=form.cleaned_data['archivo_pipeline'].name,
                    archivo_oracle=form.cleaned_data['archivo_oracle'].name,
                    estado='procesando'
                )
                
                # Guardar archivos temporalmente
                aging_temp_path = save_uploaded_file_to_temp(form.cleaned_data['archivo_aging'])
                pipeline_temp_path = save_uploaded_file_to_temp(form.cleaned_data['archivo_pipeline'])
                oracle_temp_path = save_uploaded_file_to_temp(form.cleaned_data['archivo_oracle'])
                
                # Crear procesador
                processor = InventoryProcessor(
                    user=request.user,
                    procesamiento_id=procesamiento.id
                )
                
                # Configurar rutas de archivos
                processor.set_file_paths(
                    aging_temp_path,
                    pipeline_temp_path,
                    oracle_temp_path
                )
                
                # Iniciar procesamiento en un hilo separado (para archivos grandes)
                def procesar_en_background():
                    try:
                        resultado = processor.process_files()
                        
                        # Limpiar archivos temporales
                        for temp_path in [aging_temp_path, pipeline_temp_path, oracle_temp_path]:
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                        
                    except Exception as e:
                        # Manejar errores en background
                        procesamiento.estado = 'error'
                        procesamiento.logs_procesamiento = f"Error en procesamiento: {str(e)}"
                        procesamiento.save()
                
                # Decidir si procesar en background o inmediatamente
                archivo_sizes = [
                    form.cleaned_data['archivo_aging'].size,
                    form.cleaned_data['archivo_pipeline'].size,
                    form.cleaned_data['archivo_oracle'].size
                ]
                total_size = sum(archivo_sizes)
                
                if total_size > 10 * 1024 * 1024:  # 10MB
                    # Procesar en background para archivos grandes
                    thread = threading.Thread(target=procesar_en_background)
                    thread.daemon = True
                    thread.start()
                    
                    messages.info(
                        request,
                        f"📊 Procesamiento iniciado en segundo plano. "
                        f"Puedes seguir el progreso en la página de detalles."
                    )
                    return redirect('analisis:detalle_procesamiento', pk=procesamiento.id)
                else:
                    # Procesar inmediatamente para archivos pequeños
                    resultado = processor.process_files()
                    
                    # Limpiar archivos temporales
                    for temp_path in [aging_temp_path, pipeline_temp_path, oracle_temp_path]:
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    
                    if resultado['success']:
                        messages.success(
                            request,
                            f"🎉 Procesamiento completado exitosamente en {resultado['processing_time']:.2f} segundos."
                        )
                        return redirect('analisis:detalle_procesamiento', pk=procesamiento.id)
                    else:
                        messages.error(
                            request,
                            f"❌ Error en el procesamiento: {resultado['error']}"
                        )
                        return redirect('analisis:procesar_archivos')
                        
            except Exception as e:
                messages.error(
                    request,
                    f"❌ Error al iniciar el procesamiento: {str(e)}"
                )
                return redirect('analisis:procesar_archivos')
    else:
        form = AnalisisArchivosForm()
    
    context = {
        'form': form,
        'archivo_configs': ARCHIVO_CONFIGS,
    }
    
    return render(request, 'analisis/procesar_archivos.html', context)

class HistorialProcesamientosView(LoginRequiredMixin, ListView):
    """
    Vista de lista para el historial de procesamientos
    """
    model = ProcesamientoAnalisis
    template_name = 'analisis/historial.html'
    context_object_name = 'procesamientos'
    paginate_by = 20
    
    def get_queryset(self):
        return ProcesamientoAnalisis.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_procesamiento')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtros
        estado_filtro = self.request.GET.get('estado', '')
        fecha_desde = self.request.GET.get('fecha_desde', '')
        fecha_hasta = self.request.GET.get('fecha_hasta', '')
        
        queryset = self.get_queryset()
        
        if estado_filtro:
            queryset = queryset.filter(estado=estado_filtro)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_procesamiento__date__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_procesamiento__date__lte=fecha_hasta)
        
        # Paginación con filtros aplicados
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'page_obj': page_obj,
            'procesamientos': page_obj,
            'estado_filtro': estado_filtro,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'estados_choices': ProcesamientoAnalisis.ESTADOS,
        })
        
        return context

class DetalleProcesamientoView(LoginRequiredMixin, DetailView):
    """
    Vista de detalle para un procesamiento específico
    """
    model = ProcesamientoAnalisis
    template_name = 'analisis/detalle_procesamiento.html'
    context_object_name = 'procesamiento'
    
    def get_queryset(self):
        return ProcesamientoAnalisis.objects.filter(usuario=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener logs detallados
        logs_detallados = LogProcesamiento.objects.filter(
            procesamiento=self.object
        ).order_by('timestamp')
        
        context.update({
            'logs_detallados': logs_detallados,
            'puede_descargar': self.object.estado == 'completado',
        })
        
        return context

@login_required
def descargar_archivo(request, pk, tipo):
    """
    Vista para descargar archivos generados
    """
    procesamiento = get_object_or_404(
        ProcesamientoAnalisis,
        pk=pk,
        usuario=request.user,
        estado='completado'
    )
    
    # Determinar qué archivo descargar
    if tipo == 'resultado':
        archivo_path = procesamiento.archivo_resultado
        nombre_descarga = f"Updated_Agin_{procesamiento.fecha_procesamiento.strftime('%Y%m%d_%H%M%S')}.xlsx"
    elif tipo == 'no_coincidentes':
        archivo_path = procesamiento.archivo_no_coincidentes
        nombre_descarga = f"Final_Unmatched_Agin_{procesamiento.fecha_procesamiento.strftime('%Y%m%d_%H%M%S')}.xlsx"
    else:
        raise Http404("Tipo de archivo no válido")
    
    if not archivo_path:
        messages.error(request, "❌ El archivo solicitado no está disponible.")
        return redirect('analisis:detalle_procesamiento', pk=pk)
    
    # Ruta completa del archivo
    archivo_completo = os.path.join(settings.MEDIA_ROOT, archivo_path)
    
    if not os.path.exists(archivo_completo):
        messages.error(request, "❌ El archivo no se encuentra en el servidor.")
        return redirect('analisis:detalle_procesamiento', pk=pk)
    
    # Servir el archivo
    try:
        with open(archivo_completo, 'rb') as file:
            response = HttpResponse(
                file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{nombre_descarga}"'
            return response
    except Exception as e:
        messages.error(request, f"❌ Error al descargar el archivo: {str(e)}")
        return redirect('analisis:detalle_procesamiento', pk=pk)

@login_required
def estado_procesamiento_ajax(request, pk):
    """
    Vista AJAX para obtener el estado actual de un procesamiento
    """
    try:
        procesamiento = ProcesamientoAnalisis.objects.get(
            pk=pk,
            usuario=request.user
        )
        
        # Obtener logs recientes
        logs_recientes = LogProcesamiento.objects.filter(
            procesamiento=procesamiento
        ).order_by('-timestamp')[:10]
        
        data = {
            'estado': procesamiento.estado,
            'progreso': {
                'total_registros_aging': procesamiento.total_registros_aging,
                'registros_actualizados_pipeline': procesamiento.registros_actualizados_pipeline,
                'registros_actualizados_oracle': procesamiento.registros_actualizados_oracle,
                'registros_no_coincidentes': procesamiento.registros_no_coincidentes,
                'tasa_exito_total': procesamiento.tasa_exito_total,
            },
            'logs_recientes': [
                {
                    'timestamp': log.timestamp.strftime('%H:%M:%S'),
                    'nivel': log.nivel,
                    'mensaje': log.mensaje
                }
                for log in logs_recientes
            ],
            'tiempo_procesamiento': procesamiento.tiempo_procesamiento,
            'puede_descargar': procesamiento.estado == 'completado'
        }
        
        return JsonResponse(data)
        
    except ProcesamientoAnalisis.DoesNotExist:
        return JsonResponse({'error': 'Procesamiento no encontrado'}, status=404)

@login_required
def eliminar_procesamiento(request, pk):
    """
    Vista para eliminar un procesamiento y sus archivos asociados
    """
    procesamiento = get_object_or_404(
        ProcesamientoAnalisis,
        pk=pk,
        usuario=request.user
    )
    
    if request.method == 'POST':
        try:
            # Eliminar archivos físicos si existen
            archivos_a_eliminar = [
                procesamiento.archivo_resultado,
                procesamiento.archivo_no_coincidentes
            ]
            
            for archivo_path in archivos_a_eliminar:
                if archivo_path:
                    archivo_completo = os.path.join(settings.MEDIA_ROOT, archivo_path)
                    if os.path.exists(archivo_completo):
                        os.remove(archivo_completo)
            
            # Eliminar el procesamiento (los logs se eliminan en cascada)
            procesamiento.delete()
            
            messages.success(
                request,
                f"🗑️ Procesamiento {pk} eliminado exitosamente."
            )
            
        except Exception as e:
            messages.error(
                request,
                f"❌ Error al eliminar el procesamiento: {str(e)}"
            )
    
    return redirect('analisis:historial')

@login_required
def exportar_logs(request, pk):
    """
    Vista para exportar logs de un procesamiento a un archivo de texto
    """
    procesamiento = get_object_or_404(
        ProcesamientoAnalisis,
        pk=pk,
        usuario=request.user
    )
    
    # Generar contenido del archivo de logs
    logs_content = []
    logs_content.append("=" * 80)
    logs_content.append("LOGS DE PROCESAMIENTO DE ANÁLISIS DE INVENTARIO")
    logs_content.append("=" * 80)
    logs_content.append(f"Procesamiento ID: {procesamiento.id}")
    logs_content.append(f"Usuario: {procesamiento.usuario.username}")
    logs_content.append(f"Fecha: {procesamiento.fecha_procesamiento.strftime('%Y-%m-%d %H:%M:%S')}")
    logs_content.append(f"Estado: {procesamiento.get_estado_display()}")
    logs_content.append("")
    logs_content.append("ARCHIVOS PROCESADOS:")
    logs_content.append(f"- Aging: {procesamiento.archivo_aging}")
    logs_content.append(f"- Pipeline: {procesamiento.archivo_pipeline}")
    logs_content.append(f"- Oracle: {procesamiento.archivo_oracle}")
    logs_content.append("")
    logs_content.append("ESTADÍSTICAS:")
    logs_content.append(f"- Total registros aging: {procesamiento.total_registros_aging}")
    logs_content.append(f"- Actualizados con pipeline: {procesamiento.registros_actualizados_pipeline}")
    logs_content.append(f"- Actualizados con oracle: {procesamiento.registros_actualizados_oracle}")
    logs_content.append(f"- Sin coincidencias: {procesamiento.registros_no_coincidentes}")
    logs_content.append(f"- Tasa de éxito: {procesamiento.tasa_exito_total}%")
    if procesamiento.tiempo_procesamiento:
        logs_content.append(f"- Tiempo de procesamiento: {procesamiento.tiempo_procesamiento:.2f} segundos")
    logs_content.append("")
    logs_content.append("=" * 80)
    logs_content.append("LOGS DETALLADOS:")
    logs_content.append("=" * 80)
    
    # Agregar logs detallados
    logs_detallados = LogProcesamiento.objects.filter(
        procesamiento=procesamiento
    ).order_by('timestamp')
    
    for log in logs_detallados:
        timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        logs_content.append(f"[{timestamp}] {log.nivel}: {log.mensaje}")
    
    # Generar respuesta
    content = '\n'.join(logs_content)
    filename = f"logs_procesamiento_{procesamiento.id}_{procesamiento.fecha_procesamiento.strftime('%Y%m%d_%H%M%S')}.txt"
    
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
