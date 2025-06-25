# 🔄 **AT&T Executive Portal - Flujo de Despliegue y Arranque de Contenedores**

## 📋 **Índice**
- [Conceptos Fundamentales](#conceptos-fundamentales)
- [Flujo Clásico de Despliegue](#flujo-clásico-de-despliegue)
- [Comandos de Arranque](#comandos-de-arranque)
- [Secuencias de Inicio](#secuencias-de-inicio)
- [Escenarios de Uso](#escenarios-de-uso)
- [Automatización y Scripting](#automatización-y-scripting)
- [Monitoreo del Arranque](#monitoreo-del-arranque)
- [Troubleshooting de Arranque](#troubleshooting-de-arranque)

---

## 🧩 **Conceptos Fundamentales**

### **¿Qué es Docker Compose?**
Docker Compose es una herramienta que te permite definir y ejecutar aplicaciones Docker multi-contenedor usando un archivo YAML.

### **¿Por qué usar múltiples contenedores?**
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Nginx     │  │   Django    │  │   MySQL     │  │   Redis     │
│ Web Server  │  │ Application │  │  Database   │  │   Cache     │
│ (Stateless) │  │ (Stateless) │  │ (Stateful)  │  │ (Stateful)  │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

**Ventajas:**
- ✅ **Separación de responsabilidades**
- ✅ **Escalabilidad independiente**
- ✅ **Mantenimiento más fácil**
- ✅ **Recuperación granular**

---

## 🚀 **Flujo Clásico de Despliegue**

### **1. Preparación del Entorno**
```bash
# Estado inicial: Proyecto clonado
INVENTARIO_NETWORK_APP/
├── docker-compose.yml     ← Configuración principal
├── .env                   ← Variables de entorno
└── Dockerfile             ← Imagen personalizada Django
```

### **2. Verificación Previa**
```bash
# Verificar Docker funcionando
docker --version
docker-compose --version

# Verificar archivos necesarios
ls -la docker-compose.yml .env Dockerfile

# Verificar puertos disponibles
netstat -tuln | grep -E ':(80|8000|3306|6379)\s'
```

### **3. Construcción de Imágenes**
```bash
# Construir imágenes personalizadas (primera vez)
docker-compose build

# Ver imágenes creadas
docker images | grep inventario
```

### **4. Inicio de Servicios**
```bash
# OPCIÓN 1: Un solo comando (recomendado)
docker-compose up -d

# OPCIÓN 2: Con construcción
docker-compose up --build -d

# OPCIÓN 3: Solo servicios específicos
docker-compose up -d mysql redis
docker-compose up -d web
docker-compose up -d nginx
```

---

## ⚡ **Comandos de Arranque**

### **🎯 Comando Único (Todo en Uno)**
```bash
# ✅ RECOMENDADO: Arranque completo
docker-compose up --build -d

# ¿Qué hace este comando?
# --build  : Construye imágenes si hay cambios
# -d       : Ejecuta en segundo plano (detached)
# up       : Levanta todos los servicios definidos
```

### **🔧 Arranque Paso a Paso**
```bash
# Paso 1: Servicios de datos (primero)
docker-compose up -d mysql redis

# Esperar que estén listos
docker-compose logs mysql | grep "ready for connections"

# Paso 2: Aplicación web
docker-compose up -d web

# Esperar que Django arranque
docker-compose logs web | grep "Starting development server"

# Paso 3: Proxy web
docker-compose up -d nginx
```

### **🚦 Verificación de Arranque**
```bash
# Ver estado de todos los contenedores
docker-compose ps

# Salida esperada:
# NAME                    STATUS                 PORTS
# att_django_web         Up 2 minutes (healthy) 0.0.0.0:8000->8000/tcp
# att_inventario_mysql   Up 3 minutes (healthy) 0.0.0.0:3306->3306/tcp
# att_nginx              Up 1 minute            0.0.0.0:80->80/tcp
# att_redis              Up 3 minutes (healthy) 0.0.0.0:6379->6379/tcp
```

---

## 🔄 **Secuencias de Inicio**

### **Secuencia Automática (docker-compose.yml)**
```yaml
# En tu docker-compose.yml ya está configurado:
services:
  mysql:
    # Arranca primero (sin dependencias)
    
  redis:
    # Arranca primero (sin dependencias)
    
  web:
    depends_on:
      mysql:
        condition: service_healthy  # Espera MySQL
    # Arranca después de MySQL
    
  nginx:
    depends_on:
      - web  # Espera Django
    # Arranca al final
```

### **Orden de Arranque Real:**
```
1. 🗄️  MySQL + Redis    (paralelo)
   ↓ (health check)
2. 🐍  Django Web       (espera MySQL healthy)
   ↓ (service ready)  
3. 🌐  Nginx            (espera Django)
```

### **Timeline Típico:**
```
T+0s   : docker-compose up -d
T+5s   : MySQL iniciando...
T+10s  : Redis listo ✅
T+15s  : MySQL listo ✅ (health check passed)
T+20s  : Django iniciando...
T+45s  : Django migraciones completadas
T+50s  : Django servidor listo ✅
T+55s  : Nginx iniciando...
T+60s  : Nginx listo ✅
T+65s  : ¡Aplicación disponible! 🎉
```

---

## 🎮 **Escenarios de Uso**

### **🟢 Desarrollo (Primera vez)**
```bash
# Clonar proyecto
git clone <repo> && cd INVENTARIO_NETWORK_APP

# Configurar variables
cp .env.example .env
nano .env  # Editar credenciales

# Arranque completo
docker-compose up --build -d

# Verificar
docker-compose ps
curl http://localhost:8000
```

### **🔵 Desarrollo (Día a día)**
```bash
# Arranque normal
docker-compose up -d

# Si hay cambios en código
docker-compose restart web

# Si hay cambios en requirements.txt
docker-compose up --build -d web
```

### **🟡 Testing/Staging**
```bash
# Usar configuración específica
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Con variables de staging
docker-compose --env-file .env.staging up -d
```

### **🔴 Producción**
```bash
# Construcción optimizada
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# Deploy con healthchecks
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verificación completa
./scripts/production_healthcheck.sh
```

### **🟣 Migración/Actualización**
```bash
# Backup antes de actualizar
./scripts/backup.sh

# Parar servicios
docker-compose down

# Actualizar código
git pull origin main

# Rebuild y deploy
docker-compose up --build -d

# Verificar migración
docker-compose exec web python manage.py showmigrations
```

---

## 🤖 **Automatización y Scripting**

### **Script de Inicio Completo**
```bash
# Crear: scripts/start_app.sh
cat > scripts/start_app.sh << 'EOF'
#!/bin/bash
set -e  # Parar en errores

echo "🚀 Iniciando AT&T Executive Portal..."

# Verificar prerrequisitos
echo "🔍 Verificando Docker..."
docker --version || { echo "❌ Docker no instalado"; exit 1; }
docker-compose --version || { echo "❌ Docker Compose no instalado"; exit 1; }

# Verificar archivos
echo "📁 Verificando archivos..."
[ ! -f docker-compose.yml ] && { echo "❌ docker-compose.yml no encontrado"; exit 1; }
[ ! -f .env ] && { echo "❌ .env no encontrado"; exit 1; }

# Limpiar contenedores anteriores si existen
echo "🧹 Limpiando contenedores anteriores..."
docker-compose down 2>/dev/null || true

# Construir y arrancar
echo "🏗️  Construyendo imágenes..."
docker-compose build

echo "⚡ Iniciando servicios..."
docker-compose up -d

# Esperar servicios
echo "⏳ Esperando servicios..."
sleep 10

# Verificar health
echo "🔍 Verificando servicios..."
docker-compose ps

# Test de conectividad
echo "🌐 Probando conectividad..."
timeout 30 bash -c 'until curl -s http://localhost:8000 >/dev/null; do sleep 2; done' || {
    echo "❌ Django no responde"
    docker-compose logs web --tail=20
    exit 1
}

echo "✅ AT&T Executive Portal iniciado correctamente!"
echo "🌐 Accede en: http://localhost"
echo "🔧 Django Admin: http://localhost:8000/admin"
echo "📊 Logs: docker-compose logs -f"
EOF

chmod +x scripts/start_app.sh
```

### **Script de Parada Graceful**
```bash
# Crear: scripts/stop_app.sh
cat > scripts/stop_app.sh << 'EOF'
#!/bin/bash
echo "🛑 Deteniendo AT&T Executive Portal..."

# Parada graceful
echo "📊 Estado actual:"
docker-compose ps

echo "💾 Backup rápido..."
docker-compose exec mysql mysqldump -u att_inventario -p"att_secure_2024" inventario_network_db > "backups/shutdown_backup_$(date +%Y%m%d_%H%M%S).sql" 2>/dev/null || echo "⚠️  Backup falló"

echo "⏹️  Deteniendo servicios..."
docker-compose stop

echo "🧹 Limpiando contenedores..."
docker-compose down

echo "✅ AT&T Executive Portal detenido correctamente"
EOF

chmod +x scripts/stop_app.sh
```

### **Script de Restart Inteligente**
```bash
# Crear: scripts/restart_app.sh  
cat > scripts/restart_app.sh << 'EOF'
#!/bin/bash
echo "🔄 Reiniciando AT&T Executive Portal..."

# Verificar qué servicios están corriendo
RUNNING_SERVICES=$(docker-compose ps --services --filter "status=running")

if [ -z "$RUNNING_SERVICES" ]; then
    echo "ℹ️  No hay servicios corriendo, iniciando desde cero..."
    ./scripts/start_app.sh
else
    echo "🔄 Reiniciando servicios activos: $RUNNING_SERVICES"
    
    # Restart específico para preservar datos
    if echo "$RUNNING_SERVICES" | grep -q "web"; then
        echo "🐍 Reiniciando Django..."
        docker-compose restart web
    fi
    
    if echo "$RUNNING_SERVICES" | grep -q "nginx"; then
        echo "🌐 Reiniciando Nginx..."
        docker-compose restart nginx
    fi
    
    # MySQL y Redis normalmente no necesitan restart
    echo "✅ Restart completado"
fi

# Verificar estado final
docker-compose ps
EOF

chmod +x scripts/restart_app.sh
```

---

## 📊 **Monitoreo del Arranque**

### **Health Check en Tiempo Real**
```bash
# Script de monitoreo: scripts/monitor_startup.sh
cat > scripts/monitor_startup.sh << 'EOF'
#!/bin/bash
echo "📊 Monitoreando arranque de AT&T Executive Portal..."

# Función para verificar servicio
check_service() {
    local SERVICE=$1
    local PORT=$2
    local MAX_ATTEMPTS=30
    local ATTEMPTS=0

    echo -n "⏳ Esperando $SERVICE (puerto $PORT)... "
    
    while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
        if docker-compose ps $SERVICE | grep -q "Up"; then
            if nc -z localhost $PORT 2>/dev/null; then
                echo "✅"
                return 0
            fi
        fi
        sleep 2
        ATTEMPTS=$((ATTEMPTS + 1))
        echo -n "."
    done
    
    echo "❌"
    return 1
}

# Verificar servicios en orden
check_service "mysql" 3306
check_service "redis" 6379
check_service "web" 8000
check_service "nginx" 80

# Test final de la aplicación
echo -n "🌐 Probando aplicación completa... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|302"; then
    echo "✅"
    echo ""
    echo "🎉 ¡AT&T Executive Portal está completamente operativo!"
    echo "📍 URLs disponibles:"
    echo "   • Aplicación: http://localhost"
    echo "   • Django: http://localhost:8000" 
    echo "   • Admin: http://localhost/admin"
else
    echo "❌"
    echo "🔍 Verificando logs..."
    docker-compose logs --tail=10
fi
EOF

chmod +x scripts/monitor_startup.sh
```

### **Dashboard de Estado**
```bash
# Script de estado: scripts/status.sh
cat > scripts/status.sh << 'EOF'
#!/bin/bash
clear
echo "══════════════════════════════════════════════"
echo "📊 AT&T Executive Portal - Estado del Sistema"
echo "══════════════════════════════════════════════"
echo ""

# Información del sistema
echo "🖥️  INFORMACIÓN DEL SISTEMA:"
echo "   Docker: $(docker --version 2>/dev/null || echo 'No instalado')"
echo "   Compose: $(docker-compose --version 2>/dev/null || echo 'No instalado')"
echo "   Fecha: $(date)"
echo ""

# Estado de contenedores
echo "🐳 ESTADO DE CONTENEDORES:"
if docker-compose ps &>/dev/null; then
    docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}\t{{.Ports}}"
else
    echo "   ❌ No hay contenedores corriendo"
fi
echo ""

# Uso de recursos
echo "💻 USO DE RECURSOS:"
if command -v docker &>/dev/null; then
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null || echo "   ℹ️  No hay contenedores activos"
else
    echo "   ❌ Docker no disponible"
fi
echo ""

# URLs de acceso
echo "🌐 URLs DE ACCESO:"
if docker-compose ps nginx 2>/dev/null | grep -q "Up"; then
    echo "   ✅ Aplicación Principal: http://localhost"
else
    echo "   ❌ Nginx no disponible"
fi

if docker-compose ps web 2>/dev/null | grep -q "Up"; then
    echo "   ✅ Django Directo: http://localhost:8000"
    echo "   ✅ Admin Django: http://localhost:8000/admin"
else
    echo "   ❌ Django no disponible"
fi
echo ""

# Último backup
echo "💾 ÚLTIMO BACKUP:"
if [ -d "backups" ]; then
    LAST_BACKUP=$(ls -t backups/db_backup_*.sql 2>/dev/null | head -1)
    if [ -n "$LAST_BACKUP" ]; then
        echo "   📁 $LAST_BACKUP ($(stat -c %y "$LAST_BACKUP" 2>/dev/null || stat -f %Sm "$LAST_BACKUP" 2>/dev/null || echo 'fecha desconocida'))"
    else
        echo "   ⚠️  No hay backups disponibles"
    fi
else
    echo "   ❌ Directorio backups no existe"
fi

echo ""
echo "══════════════════════════════════════════════"
EOF

chmod +x scripts/status.sh
```

---

## 🚨 **Troubleshooting de Arranque**

### **Problemas Comunes y Soluciones**

#### **1. Puerto ocupado**
```bash
# Error: "Port 80 is already in use"
# Solución:
sudo netstat -tulpn | grep :80  # Ver qué usa el puerto
sudo systemctl stop apache2     # Parar Apache si está corriendo
# O cambiar puerto en docker-compose.yml
```

#### **2. MySQL no arranca**
```bash
# Error: "MySQL connection failed"
# Debug:
docker-compose logs mysql

# Soluciones comunes:
rm -rf mysql_data/                    # Borrar datos corruptos
docker-compose down -v               # Recrear volúmenes
docker-compose up -d mysql           # Solo MySQL
```

#### **3. Django se cuelga esperando MySQL**
```bash
# Error: "MySQL no está listo - esperando..."
# Verificar:
docker-compose exec mysql mysql -u att_inventario -p

# Solución:
docker-compose restart mysql
sleep 30
docker-compose restart web
```

#### **4. Permisos de archivos**
```bash
# Error: "Permission denied"
# Solución Linux:
sudo chown -R $USER:$USER .
chmod +x docker/entrypoint.sh
chmod +x scripts/*.sh
```

#### **5. Espacio en disco insuficiente**
```bash
# Error: "No space left on device"
# Limpieza:
docker system prune -a              # Limpiar imágenes no usadas
docker volume prune                  # Limpiar volúmenes no usados
```

### **Script de Diagnóstico Automático**
```bash
# Crear: scripts/diagnose.sh
cat > scripts/diagnose.sh << 'EOF'
#!/bin/bash
echo "🔍 Diagnóstico AT&T Executive Portal"
echo "===================================="

# Verificar Docker
echo "📦 Docker:"
docker --version &>/dev/null && echo "   ✅ Docker instalado" || echo "   ❌ Docker no instalado"
docker-compose --version &>/dev/null && echo "   ✅ Docker Compose instalado" || echo "   ❌ Docker Compose no instalado"

# Verificar archivos
echo ""
echo "📁 Archivos:"
[ -f docker-compose.yml ] && echo "   ✅ docker-compose.yml" || echo "   ❌ docker-compose.yml faltante"
[ -f .env ] && echo "   ✅ .env" || echo "   ❌ .env faltante" 
[ -f Dockerfile ] && echo "   ✅ Dockerfile" || echo "   ❌ Dockerfile faltante"

# Verificar puertos
echo ""
echo "🔌 Puertos:"
for PORT in 80 8000 3306 6379; do
    if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        echo "   ⚠️  Puerto $PORT ocupado"
    else
        echo "   ✅ Puerto $PORT libre"
    fi
done

# Verificar espacio
echo ""
echo "💾 Espacio en disco:"
SPACE=$(df . | tail -1 | awk '{print $4}')
if [ "$SPACE" -lt 1000000 ]; then
    echo "   ⚠️  Poco espacio disponible: ${SPACE}KB"
else
    echo "   ✅ Espacio suficiente: ${SPACE}KB"
fi

# Estado contenedores
echo ""
echo "🐳 Contenedores:"
if docker-compose ps &>/dev/null; then
    docker-compose ps
else
    echo "   ℹ️  No hay contenedores corriendo"
fi

# Logs recientes si hay errores
echo ""
echo "📋 Logs recientes (si hay errores):"
if docker-compose ps 2>/dev/null | grep -q "Exit\|unhealthy"; then
    echo "   ⚠️  Detectados contenedores con problemas:"
    docker-compose logs --tail=5
fi

echo ""
echo "✅ Diagnóstico completado"
EOF

chmod +x scripts/diagnose.sh
```

---

## 📚 **Comandos de Referencia Rápida**

### **⚡ Arranque Express**
```bash
# Todo en uno (RECOMENDADO)
docker-compose up --build -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### **🎮 Comandos Diarios**
```bash
# Iniciar aplicación
./scripts/start_app.sh              # Script personalizado
# O manual:
docker-compose up -d

# Parar aplicación  
./scripts/stop_app.sh               # Script personalizado
# O manual:
docker-compose down

# Reiniciar
./scripts/restart_app.sh            # Script personalizado
# O manual:
docker-compose restart

# Estado actual
./scripts/status.sh                 # Dashboard personalizado
# O manual:
docker-compose ps
```

### **🔧 Comandos de Mantenimiento**
```bash
# Actualizar aplicación
git pull origin main
docker-compose up --build -d

# Backup
./scripts/backup.sh

# Logs específicos
docker-compose logs web --tail=50

# Acceso directo a contenedor
docker-compose exec web bash
```

---

## 🎯 **Mejores Prácticas**

### **✅ DO - Haz esto:**
- ✅ Usa `docker-compose up -d` para segundo plano
- ✅ Siempre verifica el estado con `docker-compose ps`
- ✅ Mantén logs rotativos para evitar llenar disco
- ✅ Usa scripts de automatización para tareas repetitivas
- ✅ Haz backup antes de cambios importantes
- ✅ Monitorea el health de los servicios

### **❌ DON'T - Evita esto:**
- ❌ No uses `docker run` para servicios multi-contenedor
- ❌ No olvides las dependencias entre servicios
- ❌ No ignores los health checks
- ❌ No hagas `docker-compose down -v` en producción sin backup
- ❌ No cambies configuraciones directamente en contenedores corriendo

---

## 🎉 **Conclusión**

### **Tu aplicación AT&T Executive Portal tiene 3 formas de arranque:**

1. **🚀 Comando Único (Recomendado):**
   ```bash
   docker-compose up --build -d
   ```

2. **🔧 Scripts Automatizados:**
   ```bash
   ./scripts/start_app.sh
   ```

3. **⚙️ Paso a Paso (Control total):**
   ```bash
   docker-compose up -d mysql redis
   docker-compose up -d web  
   docker-compose up -d nginx
   ```

**¡Con cualquiera de estas opciones tendrás tu portal profesional funcionando en menos de 2 minutos! 🎯** 