#!/bin/bash

# Script de migración automática de Docker a Podman
# AT&T Inventario Network App

echo "🚀 Iniciando migración de Docker a Podman..."
echo "================================================"

# 1. Verificar si Podman está instalado
if ! command -v podman &> /dev/null; then
    echo "❌ Podman no está instalado. Instalando..."
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y podman podman-compose
    # CentOS/RHEL
    # sudo dnf install -y podman podman-compose
fi

# 2. Verificar instalación
echo "✅ Verificando versión de Podman:"
podman --version
podman-compose --version

# 3. Detener Docker si está corriendo
echo "🛑 Deteniendo servicios Docker actuales..."
docker-compose down 2>/dev/null || echo "Docker no estaba corriendo"

# 4. Exportar volúmenes existentes (opcional)
echo "💾 Creando backup de datos..."
mkdir -p backups/migration
docker volume ls -q | grep -E "(mysql_data|redis_data)" | while read volume; do
    echo "Exportando volumen: $volume"
    docker run --rm -v $volume:/source -v $(pwd)/backups/migration:/backup alpine tar czf /backup/${volume}.tar.gz -C /source .
done 2>/dev/null || echo "No hay volúmenes Docker existentes"

# 5. Construir imágenes con Podman
echo "🔨 Construyendo imágenes con Podman..."
podman-compose build

# 6. Levantar servicios con Podman
echo "🚀 Levantando servicios con Podman..."
podman-compose up -d

# 7. Verificar estado
echo "🔍 Verificando estado de los servicios..."
podman-compose ps

# 8. Mostrar logs iniciales
echo "📋 Mostrando logs iniciales..."
podman-compose logs --tail=20

echo ""
echo "✅ Migración completada!"
echo "================================================"
echo "🌐 Tu aplicación está disponible en:"
echo "   - Aplicación: http://localhost:8000"
echo "   - Nginx:      http://localhost:80"
echo "   - MySQL:      localhost:3306"
echo "   - Redis:      localhost:6379"
echo ""
echo "📋 Comandos útiles con Podman:"
echo "   podman-compose ps           # Ver servicios"
echo "   podman-compose logs         # Ver logs"
echo "   podman-compose down         # Detener todo"
echo "   podman-compose restart      # Reiniciar"
echo "================================================" 