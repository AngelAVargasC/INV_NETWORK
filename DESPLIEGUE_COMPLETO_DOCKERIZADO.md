# 🚀 **AT&T Executive Portal - Guía de Despliegue Completo Dockerizado**

## 📋 **Índice**
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Prerrequisitos](#prerrequisitos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración de Variables](#configuración-de-variables)
- [Despliegue Rápido](#despliegue-rápido)
- [Comandos de Gestión](#comandos-de-gestión)
- [Acceso a la Aplicación](#acceso-a-la-aplicación)
- [Backup y Restauración](#backup-y-restauración)
- [Troubleshooting](#troubleshooting)
- [Migración entre Servidores](#migración-entre-servidores)
- [Monitoreo y Logs](#monitoreo-y-logs)
- [Escalabilidad](#escalabilidad)

---

## 🏗️ **Arquitectura del Sistema**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Nginx     │────│   Django    │────│   MySQL     │    │   Redis     │
│ (Port 80)   │    │ (Port 8000) │    │ (Port 3306) │    │ (Port 6379) │
│ Reverse     │    │ Web App     │    │ Database    │    │ Cache/      │
│ Proxy       │    │ Backend     │    │ Storage     │    │ Sessions    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### **Servicios Dockerizados:**
- **nginx**: Servidor web, reverse proxy, archivos estáticos
- **web**: Aplicación Django con Python 3.11
- **mysql**: Base de datos MySQL 8.0 con persistencia
- **redis**: Cache y gestión de sesiones

---

## 🔧 **Prerrequisitos**

### **Sistema Operativo Soportado:**
- ✅ Windows 10/11 con WSL2
- ✅ Linux (Ubuntu 20.04+, CentOS 8+)
- ✅ macOS 10.15+

### **Software Requerido:**
```bash
# Docker y Docker Compose
Docker Engine >= 20.10.0
Docker Compose >= 2.0.0

# Git para clonar repositorio
Git >= 2.25.0

# Puertos requeridos
Puerto 80   - Nginx (HTTP)
Puerto 8000 - Django (desarrollo)
Puerto 3306 - MySQL
Puerto 6379 - Redis
```

### **Instalación Docker (Linux Ubuntu/Debian):**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalación
docker --version
docker-compose --version
```

### **Instalación Docker (CentOS/RHEL):**
```bash
# Instalar Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## 📁 **Estructura del Proyecto**

```
INVENTARIO_NETWORK_APP/
├── docker-compose.yml          # Configuración servicios producción
├── docker-compose.dev.yml      # Configuración desarrollo
├── Dockerfile                  # Imagen Django personalizada
├── .dockerignore              # Archivos excluidos en build
├── requirements.txt           # Dependencias Python
├── .env                      # Variables de entorno (crear)
├── docker/
│   ├── entrypoint.sh         # Script inicialización Django
│   └── nginx.conf            # Configuración Nginx
├── apps/                     # Aplicaciones Django
│   ├── home/
│   ├── inventario/
│   └── usuarios/
├── core/                     # Configuración Django
│   ├── settings.py
│   └── urls.py
├── templates/                # Plantillas HTML
├── static/                   # Archivos estáticos
├── media/                    # Archivos subidos
├── backups/                  # Directorio backups DB
└── logs/                     # Logs aplicación
```

---

## ⚙️ **Configuración de Variables**

### **1. Crear archivo `.env` en la raíz del proyecto:**
```bash
# Crear archivo de variables de entorno
cat > .env << 'EOF'
# === CONFIGURACIÓN BASE DE DATOS ===
DB_NAME=inventario_network_db
DB_USER=att_inventario
DB_PASSWORD=att_secure_2024
DB_HOST=mysql
DB_PORT=3306
DB_ROOT_PASSWORD=att_root_2024

# === CONFIGURACIÓN DJANGO ===
SECRET_KEY=django-insecure-32&jnej0n!4gnx7i3(fhc(pqp&dfghf=%y@2gp!66w7(5_+bj6
DEBUG=true
DJANGO_DEVELOPMENT=true

# === SUPERUSUARIO AUTOMÁTICO ===
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@att.com
DJANGO_SUPERUSER_PASSWORD=admin123

# === CONFIGURACIÓN ADICIONAL ===
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
TIMEZONE=America/Mexico_City
EOF
```

### **2. Variables de Entorno por Ambiente:**

**Desarrollo (.env.dev):**
```bash
DEBUG=true
DJANGO_DEVELOPMENT=true
DB_HOST=mysql
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Producción (.env.prod):**
```bash
DEBUG=false
DJANGO_DEVELOPMENT=false
DB_HOST=mysql
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
SECRET_KEY=tu-clave-secreta-muy-fuerte-aqui
```

---

## 🚀 **Despliegue Rápido**

### **1. Clonar y Preparar Proyecto:**
```bash
# Clonar repositorio
git clone <URL_DEL_REPOSITORIO>
cd INVENTARIO_NETWORK_APP

# Crear archivo de variables (editar según ambiente)
cp .env.example .env
# Editar .env con tus credenciales
nano .env
```

### **2. Despliegue Completo (Primera vez):**
```bash
# Construir y levantar todos los servicios
docker-compose up --build -d

# Verificar que todos los servicios estén funcionando
docker-compose ps

# Ver logs de inicialización
docker-compose logs -f web
```

### **3. Verificar Despliegue:**
```bash
# Estado de contenedores
docker-compose ps

# Logs de todos los servicios
docker-compose logs --tail=50

# Healthcheck específico
docker-compose exec web python manage.py check
```

### **4. Acceso a la Aplicación:**
- **Producción (Nginx):** http://localhost o http://tu-servidor
- **Desarrollo (Django):** http://localhost:8000
- **Administración:** http://localhost/admin (admin/admin123)

---

## 🎮 **Comandos de Gestión**

### **Gestión de Servicios:**
```bash
# Levantar servicios
docker-compose up -d                    # Todos los servicios
docker-compose up -d web mysql          # Servicios específicos

# Parar servicios
docker-compose stop                     # Parar todos
docker-compose stop web                 # Parar específico

# Reiniciar servicios
docker-compose restart                  # Reiniciar todos
docker-compose restart web              # Reiniciar específico

# Eliminar servicios (mantiene volúmenes)
docker-compose down

# Eliminar TODO (incluye volúmenes)
docker-compose down -v --remove-orphans
```

### **Gestión de Django:**
```bash
# Migraciones
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Superusuario
docker-compose exec web python manage.py createsuperuser

# Collectstatic (archivos estáticos)
docker-compose exec web python manage.py collectstatic --noinput

# Shell Django
docker-compose exec web python manage.py shell

# Comandos personalizados
docker-compose exec web python manage.py crear_datos_ejemplo
```

### **Gestión de Base de Datos:**
```bash
# Acceso a MySQL
docker-compose exec mysql mysql -u att_inventario -p

# Backup base de datos
docker-compose exec mysql mysqldump -u att_inventario -p inventario_network_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker-compose exec -T mysql mysql -u att_inventario -p inventario_network_db < backup_20231219_143022.sql

# Ver logs MySQL
docker-compose logs mysql
```

---

## 🌐 **Acceso a la Aplicación**

### **URLs Principales:**
```bash
# Aplicación Principal
http://localhost/                       # Home/Dashboard
http://localhost/login/                 # Login usuarios
http://localhost/admin/                 # Administración Django

# Gestión de Inventario
http://localhost/inventario/articulos/  # Lista artículos
http://localhost/inventario/dashboard/  # Dashboard PMO

# APIs (si están habilitadas)
http://localhost/api/v1/articulos/      # API REST
```

### **Credenciales por Defecto:**
```bash
# Superusuario Django
Usuario: admin
Password: admin123

# Base de datos MySQL
Usuario: att_inventario
Password: att_secure_2024
Base de datos: inventario_network_db
```

---

## 💾 **Backup y Restauración**

### **Backup Automático:**
```bash
# Script de backup completo
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"

# Crear directorio backup
mkdir -p $BACKUP_DIR

# Backup base de datos
docker-compose exec -T mysql mysqldump -u att_inventario -p"att_secure_2024" inventario_network_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup archivos media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz media/

# Backup logs
tar -czf $BACKUP_DIR/logs_backup_$DATE.tar.gz logs/

echo "✅ Backup completado: $DATE"
EOF

chmod +x scripts/backup.sh
```

### **Restauración:**
```bash
# Restaurar base de datos específica
docker-compose exec -T mysql mysql -u att_inventario -p"att_secure_2024" inventario_network_db < backups/db_backup_20231219_143022.sql

# Restaurar archivos media
tar -xzf backups/media_backup_20231219_143022.tar.gz

# Reiniciar servicios después de restauración
docker-compose restart web
```

### **Backup de Configuración:**
```bash
# Backup completo del proyecto (sin containers)
tar --exclude='logs' --exclude='media' -czf att_portal_config_$(date +%Y%m%d_%H%M%S).tar.gz .
```

---

## 🔍 **Troubleshooting**

### **Problemas Comunes:**

**1. Django no arranca - "MySQL no está listo":**
```bash
# Verificar estado MySQL
docker-compose logs mysql

# Reiniciar servicios en orden
docker-compose restart mysql
sleep 30
docker-compose restart web
```

**2. Puerto 80 ocupado:**
```bash
# Ver qué usa el puerto 80
sudo netstat -tulpn | grep :80

# Cambiar puerto en docker-compose.yml
ports:
  - "8080:80"  # Usar puerto 8080 en lugar de 80
```

**3. Permisos de archivos (Linux):**
```bash
# Arreglar permisos
sudo chown -R $USER:$USER .
sudo chmod -R 755 .
sudo chmod +x docker/entrypoint.sh
```

**4. Espacio en disco:**
```bash
# Limpiar imágenes no usadas
docker system prune -a

# Ver uso de espacio
docker system df
```

**5. Problemas de red entre contenedores:**
```bash
# Verificar red Docker
docker network ls
docker network inspect inventario_network_app_att_network

# Recrear red
docker-compose down
docker-compose up --force-recreate -d
```

### **Logs de Diagnóstico:**
```bash
# Logs específicos por servicio
docker-compose logs web --tail=100
docker-compose logs mysql --tail=50
docker-compose logs nginx --tail=30

# Logs en tiempo real
docker-compose logs -f

# Logs con timestamps
docker-compose logs -t web
```

---

## 🚚 **Migración entre Servidores**

### **1. Servidor Origen (Exportar):**
```bash
# Backup completo
./scripts/backup.sh

# Exportar configuración
tar -czf att_portal_migration_$(date +%Y%m%d_%H%M%S).tar.gz \
  docker-compose.yml \
  docker-compose.dev.yml \
  Dockerfile \
  .dockerignore \
  requirements.txt \
  .env \
  docker/ \
  apps/ \
  core/ \
  templates/ \
  static/ \
  backups/

# Copiar al servidor destino
scp att_portal_migration_*.tar.gz user@servidor-destino:/opt/att-portal/
```

### **2. Servidor Destino (Importar):**
```bash
# Extraer archivos
cd /opt/att-portal
tar -xzf att_portal_migration_*.tar.gz

# Editar variables de entorno para nuevo servidor
nano .env

# Desplegar
docker-compose up --build -d

# Restaurar datos
docker-compose exec -T mysql mysql -u att_inventario -p < backups/db_backup_latest.sql
```

### **3. Migración con Downtime Mínimo:**
```bash
# En servidor destino (preparar)
docker-compose build
docker-compose up -d mysql redis

# Sincronizar datos
rsync -avz origen:/opt/att-portal/media/ /opt/att-portal/media/
scp origen:/opt/att-portal/backups/db_backup_latest.sql /tmp/

# Importar DB
docker-compose exec -T mysql mysql -u att_inventario -p < /tmp/db_backup_latest.sql

# Levantar servicios
docker-compose up -d

# Cambiar DNS/Load Balancer al nuevo servidor
```

---

## 📊 **Monitoreo y Logs**

### **Monitoreo de Recursos:**
```bash
# Uso de recursos por contenedor
docker stats

# Uso de espacio
docker system df

# Información detallada de contenedores
docker-compose top
```

### **Configuración de Logs:**
```bash
# Configurar rotación de logs en docker-compose.yml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### **Logs Centralizados (Opcional):**
```bash
# Agregar servicio de logs
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./config/loki.yml:/etc/loki/local-config.yaml
```

### **Health Checks Avanzados:**
```bash
# Script de monitoreo
cat > scripts/health_check.sh << 'EOF'
#!/bin/bash
echo "🔍 AT&T Portal Health Check"
echo "=========================="

# Verificar servicios
docker-compose ps

# Verificar acceso web
curl -s -o /dev/null -w "%{http_code}" http://localhost || echo "❌ Web no accesible"

# Verificar DB
docker-compose exec mysql mysqladmin ping -h mysql -u att_inventario -p"att_secure_2024" || echo "❌ MySQL no responde"

echo "✅ Health check completado"
EOF
```

---

## 📈 **Escalabilidad**

### **Escalado Horizontal (Múltiples Instancias Django):**
```yaml
# docker-compose.yml
services:
  web:
    # ... configuración base
    deploy:
      replicas: 3
  
  nginx:
    # ... configuración con load balancing
    depends_on:
      - web
```

### **Base de Datos en Cluster:**
```yaml
# Para producción - MySQL Master-Slave
services:
  mysql-master:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_REPLICATION_MODE: master
      
  mysql-slave:
    image: mysql:8.0
    environment:
      MYSQL_REPLICATION_MODE: slave
      MYSQL_MASTER_HOST: mysql-master
```

### **Redis Cluster:**
```yaml
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes
  
  redis-slave:
    image: redis:7-alpine
    command: redis-server --slaveof redis-master 6379
```

---

## 🔒 **Seguridad**

### **Variables de Entorno Seguras:**
```bash
# Generar SECRET_KEY segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Usar Docker Secrets en producción
echo "att_secure_password_2024" | docker secret create mysql_password -
```

### **Nginx con SSL (Producción):**
```nginx
server {
    listen 443 ssl;
    server_name tu-dominio.com;
    
    ssl_certificate /etc/ssl/certs/tu-dominio.crt;
    ssl_certificate_key /etc/ssl/private/tu-dominio.key;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📚 **Comandos de Referencia Rápida**

```bash
# === DESPLIEGUE ===
docker-compose up --build -d        # Desplegar todo
docker-compose down                  # Parar todo
docker-compose restart web          # Reiniciar servicio

# === DJANGO ===
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py createsuperuser

# === BASE DE DATOS ===
docker-compose exec mysql mysql -u att_inventario -p
docker-compose exec mysql mysqldump -u att_inventario -p inventario_network_db > backup.sql

# === LOGS Y MONITOREO ===
docker-compose logs -f web          # Logs Django
docker-compose ps                    # Estado servicios
docker stats                         # Recursos en tiempo real

# === BACKUP ===
./scripts/backup.sh                  # Backup completo
tar -czf config_backup.tar.gz docker-compose.yml .env docker/
```

---

## 🎯 **Próximos Pasos**

1. **SSL/HTTPS:** Configurar certificados SSL para producción
2. **CI/CD:** Implementar pipeline de deployment automatizado
3. **Monitoreo:** Agregar Prometheus + Grafana
4. **Backup Automático:** Configurar backups programados
5. **CDN:** Implementar CDN para archivos estáticos
6. **Multi-región:** Despliegue en múltiples zonas geográficas

---

## 📞 **Soporte**

Para issues o preguntas:
- Revisar logs: `docker-compose logs`
- Estado servicios: `docker-compose ps`
- Health check: `./scripts/health_check.sh`

**¡Tu AT&T Executive Portal está listo para producción! 🚀** 