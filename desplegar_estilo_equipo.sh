#!/bin/bash

# =============================================================================
# SCRIPT DE DESPLIEGUE ESTILO EQUIPO AT&T
# =============================================================================
# Proceso simplificado siguiendo las configuraciones del equipo

echo "🚀 DESPLEGANDO AT&T INVENTARIO - ESTILO EQUIPO"
echo "=============================================="

# 1. Verificar archivos necesarios
echo "🔍 Verificando archivos..."
if [ ! -f "production.env" ]; then
    echo "❌ Error: Falta archivo production.env"
    echo "💡 Crea el archivo con las variables necesarias"
    exit 1
fi

if [ ! -f "Dockerfile.alpine" ]; then
    echo "❌ Error: Falta Dockerfile.alpine"
    exit 1
fi

if [ ! -f "entrypoint-alpine.sh" ]; then
    echo "❌ Error: Falta entrypoint-alpine.sh"
    exit 1
fi

# 2. Hacer ejecutable el entrypoint
echo "🔧 Configurando permisos..."
chmod +x entrypoint-alpine.sh

# 3. Detener contenedor anterior si existe
echo "🛑 Deteniendo contenedor anterior..."
podman stop att_inventario_alpine 2>/dev/null || true
podman rm att_inventario_alpine 2>/dev/null || true

# 4. Construir imagen Alpine (como el equipo)
echo "🔨 Construyendo imagen Alpine..."
podman build -f Dockerfile.alpine -t att_inventario:alpine .

# 5. Ejecutar contenedor con configuración del equipo
echo "🚀 Iniciando contenedor..."
podman run -d \
    --name att_inventario_alpine \
    --restart unless-stopped \
    -p 8449:8449 \
    --env-file production.env \
    -v $(pwd)/media:/code/media \
    -v $(pwd)/logs:/code/logs \
    -v $(pwd)/staticfiles:/code/staticfiles \
    att_inventario:alpine

# 6. Verificar estado
echo "🔍 Verificando despliegue..."
sleep 5

if podman ps | grep -q att_inventario_alpine; then
    echo "✅ DESPLIEGUE EXITOSO!"
    echo "🌐 Aplicación disponible en: http://localhost:8449"
    echo "📋 Ver logs: podman logs att_inventario_alpine"
    echo "🛑 Detener: podman stop att_inventario_alpine"
    
    # Mostrar logs iniciales
    echo "📋 Logs iniciales:"
    podman logs --tail=20 att_inventario_alpine
else
    echo "❌ Error en el despliegue"
    echo "🔍 Ver logs de error:"
    podman logs att_inventario_alpine
    exit 1
fi

echo ""
echo "🎉 PROYECTO DESPLEGADO EXITOSAMENTE!"
echo "=============================================="
echo "📱 Acceso: http://localhost:8449"
echo "👤 Admin: http://localhost:8449/admin"
echo "📊 Dashboard: http://localhost:8449/inventario"
echo "==============================================" 