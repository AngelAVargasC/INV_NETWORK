#!/bin/bash

# Script de entrada para contenedor Django - AT&T Executive Portal
# Este script se ejecuta cuando inicia el contenedor

set -e  # Parar si hay errores

echo "🚀 Iniciando AT&T Executive Portal..."

# Esperar a que MySQL esté disponible
echo "⏳ Esperando MySQL..."
until python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('MySQL conectado exitosamente!')
    exit(0)
except Exception as e:
    print(f'Error de conexión: {e}')
    exit(1)
" 2>/dev/null; do
    echo "MySQL no está listo - esperando..."
    sleep 3
done
echo "✅ MySQL está disponible!"

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Crear superusuario si no existe (solo en desarrollo)
if [ "$DJANGO_DEVELOPMENT" = "true" ]; then
    echo "👤 Verificando superusuario..."
    python manage.py shell << EOF
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@att.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Superusuario '{username}' creado")
else:
    print(f"ℹ️  Superusuario '{username}' ya existe")
EOF
fi

# Mensaje de inicio completado
echo "🎉 AT&T Executive Portal listo!"
echo "🌐 Aplicación disponible en: http://localhost:8000"

# Ejecutar comando pasado como argumentos
exec "$@" 