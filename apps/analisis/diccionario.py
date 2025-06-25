# =============================================================================
# DICCIONARIO DE COLUMNAS PARA ANÁLISIS DE INVENTARIO
# =============================================================================
# Definición de columnas para el procesamiento de archivos Excel

# Columnas del archivo AGING (Detalle de aging)
cols_inventario_agin = [
    'Año','Articulo','Descripción','Proveedor','Nombre de proyecto recibo',	'Orden de Compra','ID de PMO','Nombre de Proyecto',
    'Program Manager','Estatus PMO','Fecha de Implementación Si/No','Historial','Observaciones','Retrasos en salida','AVP','Tipo','Fabrica',
    'COSTO UNITARIO DISTRIBUCION', 'Cantidad Embarcada', 'Costo Salida $MXN','Existencia Actual','Costo $MXN Existencias','Costo $USD Existencias'
]

# Columnas del archivo PIPELINE (Pipeline 2025)
pipeline = [
    'PO Actual','IDPMO','Nombre de Proyecto','Program / Product','Macro CAT'
]

# Columnas del archivo ORACLE (Hoja1)
oracle_cols = [
    'Orden de compra','ID PMO','FABRICA','Descripción','Cuenta Cargo', 'Capex/Opex',	'Nombre de Proyecto','Program Manager','AVP'
]

# Configuraciones de archivos
ARCHIVO_CONFIGS = {
    'aging': {
        'nombre': 'Detalle Aging Inventario',
        'sheet_name': 'Detalle de aging',
        'header': 3,
        'columnas': cols_inventario_agin,
        'descripcion': 'Datos principales de inventario con información detallada de artículos',
        'icon': '📊',
        'color': '#2196F3'
    },
    'pipeline': {
        'nombre': 'Pipeline',
        'sheet_name': 'Pipeline 2025',
        'header': 10,
        'columnas': pipeline,
        'descripcion': 'Información de proyectos y PMO en desarrollo',
        'icon': '🔄',
        'color': '#4CAF50'
    },
    'oracle': {
        'nombre': 'PO_ORACLE',
        'sheet_name': 'Hoja1',
        'header': 0,
        'columnas': oracle_cols,
        'descripcion': 'Datos complementarios de Oracle ERP',
        'icon': '🏢',
        'color': '#FF9800'
    }
}

# Columnas de salida esperadas en el archivo final
OUTPUT_COLUMNS_ORDER = [
    'Año','Articulo','Descripción','Proveedor','Nombre de proyecto recibo',	'Orden de Compra','ID de PMO','Nombre de Proyecto',
    'Program Manager','Estatus PMO','Fecha de Implementación Si/No','Historial','Observaciones','Retrasos en salida','AVP','Tipo','Fabrica',
    'COSTO UNITARIO DISTRIBUCION', 'Cantidad Embarcada', 'Costo Salida $MXN','Existencia Actual','Costo $MXN Existencias','Costo $USD Existencias'
] 