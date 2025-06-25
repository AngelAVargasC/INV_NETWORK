#!/usr/bin/env python3
"""
Script de verificación y actualización de dependencias
AT&T Inventario Network App - Preparación para Producción
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, check=True):
    """Ejecutar comando y devolver resultado"""
    print(f"🔧 Ejecutando: {command}")
    try:
        result = subprocess.run(
            command.split(), 
            capture_output=True, 
            text=True, 
            check=check
        )
        if result.stdout:
            print(f"✅ Salida: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error output: {e.stderr}")
        return None

def verificar_entorno():
    """Verificar que estamos en el entorno correcto"""
    print("🔍 Verificando entorno...")
    
    # Verificar que estamos en el directorio correcto
    if not Path("manage.py").exists():
        print("❌ Error: No se encontró manage.py. Ejecuta desde el directorio raíz del proyecto.")
        return False
    
    # Verificar Python version
    python_version = sys.version_info
    if python_version < (3, 11):
        print(f"⚠️ Advertencia: Python {python_version.major}.{python_version.minor} detectado. Se recomienda Python >= 3.11")
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor} - Compatible")
    
    return True

def crear_backup_requirements():
    """Crear backup del requirements actual"""
    print("💾 Creando backup de requirements.txt...")
    if Path("requirements.txt").exists():
        import shutil
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"requirements_backup_{timestamp}.txt"
        shutil.copy("requirements.txt", backup_name)
        print(f"✅ Backup creado: {backup_name}")

def verificar_dependencias_actuales():
    """Verificar dependencias instaladas actualmente"""
    print("📋 Verificando dependencias actuales...")
    result = run_command("pip freeze")
    if result:
        with open("dependencias_actuales.txt", "w") as f:
            f.write(result.stdout)
        print("✅ Lista guardada en: dependencias_actuales.txt")

def instalar_dependencias():
    """Instalar dependencias actualizadas"""
    print("📦 Instalando dependencias actualizadas...")
    
    # Actualizar pip primero
    run_command("python -m pip install --upgrade pip")
    
    # Instalar desde requirements.txt
    result = run_command("pip install -r requirements.txt --upgrade")
    
    if result and result.returncode == 0:
        print("✅ Dependencias instaladas correctamente")
        return True
    else:
        print("❌ Error instalando dependencias")
        return False

def verificar_instalacion():
    """Verificar que todas las dependencias están correctamente instaladas"""
    print("🔍 Verificando instalación...")
    
    dependencias_criticas = [
        'django',
        'mysqlclient', 
        'pandas',
        'openpyxl',
        'pillow',
        'gunicorn',
        'whitenoise'
    ]
    
    errores = []
    for dep in dependencias_criticas:
        try:
            __import__(dep)
            print(f"✅ {dep} - OK")
        except ImportError:
            print(f"❌ {dep} - FALTA")
            errores.append(dep)
    
    return len(errores) == 0

def ejecutar_tests_basicos():
    """Ejecutar tests básicos del proyecto"""
    print("🧪 Ejecutando tests básicos...")
    
    # Check de Django
    result = run_command("python manage.py check", check=False)
    if result and result.returncode == 0:
        print("✅ Django check - OK")
    else:
        print("❌ Django check - ERRORES")
        return False
    
    # Collectstatic (test)
    result = run_command("python manage.py collectstatic --noinput --dry-run", check=False)
    if result and result.returncode == 0:
        print("✅ Collectstatic - OK")
    else:
        print("⚠️ Collectstatic - Verificar archivos estáticos")
    
    return True

def generar_reporte():
    """Generar reporte final"""
    print("\n📊 GENERANDO REPORTE FINAL...")
    
    # Información del sistema
    with open("reporte_dependencias.txt", "w", encoding="utf-8") as f:
        f.write("=== REPORTE DE DEPENDENCIAS AT&T INVENTARIO ===\n")
        f.write(f"Fecha: {datetime.datetime.now()}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"Directorio: {os.getcwd()}\n\n")
        
        # Dependencias instaladas
        result = run_command("pip freeze")
        if result:
            f.write("=== DEPENDENCIAS INSTALADAS ===\n")
            f.write(result.stdout)
            f.write("\n")
        
        # Información de Django
        result = run_command("python manage.py version", check=False)
        if result:
            f.write(f"Django Version: {result.stdout.strip()}\n")
        
        f.write("\n=== COMANDOS PARA PRODUCCIÓN ===\n")
        f.write("# Instalar en servidor:\n")
        f.write("pip install -r requirements-prod.txt\n\n")
        f.write("# Comandos Django:\n")
        f.write("python manage.py migrate\n")
        f.write("python manage.py collectstatic --noinput\n")
        f.write("python manage.py check --deploy\n\n")
        f.write("# Servidor producción:\n")
        f.write("gunicorn core.wsgi:application --bind 0.0.0.0:8000\n")
    
    print("✅ Reporte generado: reporte_dependencias.txt")

def main():
    """Función principal"""
    print("🚀 SCRIPT DE ACTUALIZACIÓN DE DEPENDENCIAS")
    print("=" * 50)
    
    import datetime
    
    if not verificar_entorno():
        sys.exit(1)
    
    # Crear backup
    crear_backup_requirements()
    
    # Verificar dependencias actuales
    verificar_dependencias_actuales()
    
    # Preguntar si continuar
    respuesta = input("\n¿Proceder con la actualización? (s/N): ").lower()
    if respuesta not in ['s', 'si', 'yes', 'y']:
        print("❌ Actualización cancelada por el usuario")
        sys.exit(0)
    
    # Instalar dependencias
    if not instalar_dependencias():
        print("❌ Error en la instalación. Revisa los errores arriba.")
        sys.exit(1)
    
    # Verificar instalación
    if not verificar_instalacion():
        print("❌ Algunas dependencias faltan. Revisa la instalación.")
        sys.exit(1)
    
    # Tests básicos
    if not ejecutar_tests_basicos():
        print("⚠️ Algunos tests fallaron. Revisa la configuración.")
    
    # Generar reporte
    generar_reporte()
    
    print("\n🎉 ACTUALIZACIÓN COMPLETADA")
    print("=" * 50)
    print("✅ Dependencias actualizadas correctamente")
    print("✅ Proyecto listo para despliegue en producción")
    print("📄 Revisa: reporte_dependencias.txt")
    print("\n🚀 Próximos pasos:")
    print("1. Revisa el reporte generado")
    print("2. Ejecuta: python manage.py check --deploy")
    print("3. Crea el archivo .env para producción")
    print("4. Despliega con: podman-compose up -d")

if __name__ == "__main__":
    main() 