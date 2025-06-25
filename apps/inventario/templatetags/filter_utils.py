from django import template

register = template.Library()

@register.simple_tag
def count_active_filters(request):
    """Cuenta los filtros activos de manera eficiente"""
    filtros_activos = [
        'q', 'año', 'articulo', 'descripcion', 'proveedor', 
        'proyecto_recibo', 'orden_compra', 'id_pmo', 'nombre_proyecto',
        'manager', 'estatus', 'avp', 'tipo', 'fabrica',
        'costo_min', 'costo_max', 'existencia_min'
    ]
    
    count = 0
    for filtro in filtros_activos:
        if request.GET.get(filtro, '').strip():
            count += 1
    
    return count

@register.simple_tag
def pluralize_filtros(count):
    """Pluraliza correctamente la palabra filtros"""
    if count == 1:
        return f"{count} filtro activo"
    else:
        return f"{count} filtros activos"

@register.simple_tag
def get_filter_summary(request):
    """Obtiene un resumen completo de filtros para debugging"""
    filtros_activos = {}
    filtros_config = [
        'q', 'año', 'articulo', 'descripcion', 'proveedor', 
        'proyecto_recibo', 'orden_compra', 'id_pmo', 'nombre_proyecto',
        'manager', 'estatus', 'avp', 'tipo', 'fabrica',
        'costo_min', 'costo_max', 'existencia_min'
    ]
    
    for filtro in filtros_config:
        valor = request.GET.get(filtro, '').strip()
        if valor:
            filtros_activos[filtro] = valor
    
    return filtros_activos 