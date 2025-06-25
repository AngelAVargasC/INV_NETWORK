from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    path('debug/', views.dashboard_debug, name='dashboard_debug'),
    
    # Gestión de artículos
    path('articulos/', views.ArticuloListView.as_view(), name='articulo_list'),
    path('articulos/fullscreen/', views.ArticuloListFullscreenView.as_view(), name='articulo_list_fullscreen'),
    path('articulos/<int:pk>/', views.ArticuloDetailView.as_view(), name='articulo_detail'),
    path('articulos/nuevo/', views.ArticuloCreateView.as_view(), name='articulo_create'),
    path('articulos/<int:pk>/editar/', views.ArticuloUpdateView.as_view(), name='articulo_update'),
    path('articulos/<int:pk>/cambiar-estatus/', views.cambiar_estatus_articulo, name='cambiar_estatus'),
    
    # Importación de datos
    path('importar/', views.importar_datos, name='importar_datos'),
    
    # APIs y exportación
    path('api/estadisticas/', views.estadisticas_api, name='estadisticas_api'),
    path('exportar/', views.exportar_articulos, name='exportar_articulos'),
    
    # APIs de métricas
    path('api/metricas-dashboard/', views.api_metricas_dashboard, name='api_metricas_dashboard'),
    path('api/resumen-ejecutivo/', views.api_resumen_ejecutivo, name='api_resumen_ejecutivo'),
    path('api/metricas-financieras/', views.api_metricas_financieras, name='api_metricas_financieras'),
    path('api/analisis-estatus/', views.api_analisis_estatus, name='api_analisis_estatus'),
] 