from django.urls import path
from . import views

app_name = 'analisis'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_analisis, name='dashboard'),
    
    # Procesamiento de archivos
    path('procesar/', views.procesar_archivos, name='procesar_archivos'),
    
    # Historial de procesamientos
    path('historial/', views.HistorialProcesamientosView.as_view(), name='historial'),
    
    # Detalle de procesamiento
    path('procesamiento/<int:pk>/', views.DetalleProcesamientoView.as_view(), name='detalle_procesamiento'),
    
    # Descargas de archivos
    path('procesamiento/<int:pk>/descargar/<str:tipo>/', views.descargar_archivo, name='descargar_archivo'),
    
    # Exportar logs
    path('procesamiento/<int:pk>/logs/', views.exportar_logs, name='exportar_logs'),
    
    # AJAX para estado de procesamiento
    path('procesamiento/<int:pk>/estado/', views.estado_procesamiento_ajax, name='estado_procesamiento_ajax'),
    
    # Eliminar procesamiento
    path('procesamiento/<int:pk>/eliminar/', views.eliminar_procesamiento, name='eliminar_procesamiento'),
] 