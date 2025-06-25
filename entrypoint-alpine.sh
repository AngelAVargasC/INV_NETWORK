#!/bin/bash

echo "🚀 AT&T Inventario Network App - Conectando a MySQL Empresarial"
echo "=============================================================="

# Verificar conexión al MySQL empresarial (con timeout de seguridad)
echo "🔍 Verificando conexión a MySQL empresarial..."
timeout 30 python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Conexión a MySQL empresarial exitosa")
except Exception as e:
    print(f"❌ Error conectando a MySQL: {e}")
    exit(1)
EOF

# Verificar que la base de datos existe (sin crear si no existe)
echo "🔍 Verificando base de datos inventario_network_db..."
python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
db_name = os.getenv('DB_NAME', 'inventario_network_db')

try:
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
        result = cursor.fetchone()
        if result:
            print(f"✅ Base de datos '{db_name}' existe")
        else:
            print(f"⚠️ Base de datos '{db_name}' NO existe")
            print(f"💡 Solicita al administrador crear: CREATE DATABASE {db_name};")
            exit(1)
except Exception as e:
    print(f"❌ Error verificando base de datos: {e}")
    exit(1)
EOF

echo 'Running collectstatic......'
python manage.py collectstatic --no-input --settings=core.settings

echo 'Applying migrations...'
python manage.py makemigrations --settings=core.settings
python manage.py migrate --settings=core.settings

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell << EOF
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@att.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'✅ Superusuario {username} creado exitosamente')
else:
    print(f'ℹ️ Superusuario {username} ya existe')
EOF

echo "🚀 Iniciando servidor en puerto 8449..."
gunicorn --env DJANGO_SETTINGS_MODULE=core.settings core.wsgi:application --bind 0.0.0.0:8449 --workers 3 