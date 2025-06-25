#!/usr/bin/env python3
"""
Script para verificar conexión al MySQL empresarial
Ejecutar ANTES del despliegue para validar conectividad
"""

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verificar_mysql_empresarial():
    """Verificar conexión al MySQL empresarial de forma segura"""
    
    print("🔍 VERIFICANDO CONEXIÓN A MYSQL EMPRESARIAL")
    print("=" * 50)
    
    # Cargar variables de entorno
    try:
        from dotenv import load_dotenv
        if Path("production.env").exists():
            load_dotenv("production.env")
            print("✅ Variables de entorno cargadas desde production.env")
        else:
            print("❌ Error: No se encontró production.env")
            return False
    except ImportError:
        print("⚠️ python-dotenv no instalado, usando variables del sistema")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    try:
        import django
        django.setup()
        print("✅ Django configurado correctamente")
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return False
    
    # Variables de conexión
    db_host = os.getenv('DB_HOST', '10.150.153.31')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'inventario_network_db')
    db_user = os.getenv('DB_USER', 'root')
    
    print(f"🔗 Conectando a: {db_user}@{db_host}:{db_port}")
    
    # Test 1: Verificar conectividad de red
    print("\n📡 Test 1: Conectividad de red...")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((db_host, int(db_port)))
        sock.close()
        
        if result == 0:
            print(f"✅ Puerto {db_port} en {db_host} está abierto")
        else:
            print(f"❌ No se puede conectar a {db_host}:{db_port}")
            return False
    except Exception as e:
        print(f"❌ Error de red: {e}")
        return False
    
    # Test 2: Verificar conexión a MySQL
    print("\n🗄️ Test 2: Conexión a MySQL...")
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"✅ MySQL conectado - Versión: {version}")
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        print("💡 Verifica las credenciales en production.env")
        return False
    
    # Test 3: Verificar permisos del usuario
    print("\n🔐 Test 3: Permisos de usuario...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            print(f"✅ Usuario tiene acceso a {len(databases)} bases de datos")
            
            # Mostrar solo algunas para no exponer toda la información
            sample_dbs = [db for db in databases if not db.startswith(('information_schema', 'performance_schema', 'mysql', 'sys'))][:5]
            if sample_dbs:
                print(f"📋 Ejemplos: {', '.join(sample_dbs)}")
    except Exception as e:
        print(f"❌ Error verificando permisos: {e}")
        return False
    
    # Test 4: Verificar si existe la base de datos del proyecto
    print(f"\n📊 Test 4: Base de datos '{db_name}'...")
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
            result = cursor.fetchone()
            
            if result:
                print(f"✅ Base de datos '{db_name}' existe")
                
                # Verificar si tiene tablas
                cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{db_name}'")
                table_count = cursor.fetchone()[0]
                print(f"📋 Contiene {table_count} tablas")
                
                return True
            else:
                print(f"⚠️ Base de datos '{db_name}' NO existe")
                print(f"💡 Ejecuta el script SQL: crear_db_empresarial.sql")
                print(f"💡 O pide al administrador ejecutar:")
                print(f"   CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def main():
    """Función principal"""
    
    # Verificar que estamos en el directorio correcto
    if not Path("manage.py").exists():
        print("❌ Error: Ejecuta desde el directorio raíz del proyecto (donde está manage.py)")
        sys.exit(1)
    
    # Ejecutar verificaciones
    if verificar_mysql_empresarial():
        print("\n🎉 VERIFICACIÓN EXITOSA")
        print("=" * 50)
        print("✅ Tu aplicación puede conectarse al MySQL empresarial")
        print("✅ La base de datos existe y está lista")
        print("🚀 Puedes proceder con el despliegue:")
        print("   bash desplegar_estilo_equipo.sh")
    else:
        print("\n❌ VERIFICACIÓN FALLIDA")
        print("=" * 50)
        print("🔧 Acciones requeridas:")
        print("1. Verificar credenciales en production.env")
        print("2. Pedir al administrador crear la base de datos")
        print("3. Ejecutar: crear_db_empresarial.sql")
        print("4. Repetir verificación")
        sys.exit(1)

if __name__ == "__main__":
    main() 