# 🐳 AT&T Executive Portal - Dockerización

## 📋 Información General

La aplicación **AT&T Executive Portal** ha sido completamente dockerizada con una arquitectura profesional de microservicios.

### 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │────│     Django      │────│     MySQL       │
│   (Port 80)     │    │   (Port 8000)   │    │   (Port 3306)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Port 6379)   │
                       └─────────────────┘
```

### 🛠️ Componentes

- **🌐 Nginx**: Servidor web y proxy reverso
- **🐍 Django**: Aplicación web principal
- **🗄️ MySQL**: Base de datos principal
- **⚡ Redis**: Cache y sesiones

---

## 🚀 Comandos Básicos

### **Iniciar aplicación completa**
```bash
# Desarrollo (con hot-reloading)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Producción (con Nginx)
docker-compose up -d

# Solo base de datos
docker-compose up -d mysql redis
```

### **Ver estado de servicios**
```bash
# Estado de contenedores
docker-compose ps

# Logs en tiempo real
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f web
docker-compose logs -f mysql
```

### **Parar aplicación**
```bash
# Parar servicios
docker-compose down

# Parar y eliminar volúmenes (¡CUIDADO!)
docker-compose down -v
```

---

## 🔧 Desarrollo

### **Modo desarrollo recomendado**
```bash
# 1. Iniciar solo base de datos
docker-compose up -d mysql redis

# 2. Ejecutar Django localmente (en tu venv)
python manage.py runserver

# O usando Docker con hot-reloading:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d web
```

### **Acceso a servicios en desarrollo**
- **Django**: http://localhost:8000
- **MySQL**: localhost:3306
- **Redis**: localhost:6379

### **Comandos de desarrollo**
```bash
# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic

# Shell de Django
docker-compose exec web python manage.py shell

# Acceder al contenedor
docker-compose exec web bash
```

---

## 🏭 Producción

### **Iniciar en modo producción**
```bash
# Build y start
docker-compose up --build -d

# Verificar que todo esté corriendo
docker-compose ps
```

### **Acceso en producción**
- **Aplicación**: http://localhost (Puerto 80)
- **Admin**: http://localhost/admin/

### **Monitoreo**
```bash
# Ver uso de recursos
docker stats

# Health checks
docker-compose exec mysql mysqladmin ping
docker-compose exec redis redis-cli ping
docker-compose exec web curl -f http://localhost:8000/
```

---

## 📦 Gestión de Datos

### **Backups automáticos**
```bash
# Backup manual
docker-compose exec mysql mysqldump -u att_inventario -patt_secure_2024 inventario_network_db > backups/backup_$(date +%Y%m%d).sql

# Backup usando script
docker-compose exec mysql /usr/local/bin/backup.sh
```

### **Restaurar datos**
```bash
# Desde backup
docker-compose exec -T mysql mysql -u att_inventario -patt_secure_2024 inventario_network_db < backups/backup.sql
```

### **Volúmenes de datos**
```bash
# Ver volúmenes
docker volume ls

# Backup de volúmenes
docker run --rm -v inventario_network_app_mysql_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/mysql_volume_backup.tar.gz -C /data .
```

---

## 🔍 Debugging

### **Ver logs detallados**
```bash
# Todos los servicios
docker-compose logs --tail=100 -f

# Servicio específico
docker-compose logs --tail=50 -f web
docker-compose logs --tail=50 -f mysql
docker-compose logs --tail=50 -f nginx
```

### **Acceso directo a contenedores**
```bash
# Django container
docker-compose exec web bash
docker-compose exec web python manage.py shell

# MySQL container
docker-compose exec mysql mysql -u att_inventario -p
docker-compose exec mysql bash

# Redis container
docker-compose exec redis redis-cli
```

### **Verificar configuración**
```bash
# Variables de entorno Django
docker-compose exec web printenv | grep -E "(DJANGO|DB_)"

# Configuración MySQL
docker-compose exec mysql mysql -u root -p -e "SHOW VARIABLES LIKE 'version%';"

# Test de conectividad
docker-compose exec web python manage.py dbshell --command="SELECT 1;"
```

---

## 🛡️ Seguridad

### **Cambiar credenciales**
1. Editar `.env` file:
```env
DB_PASSWORD=nueva_contraseña_segura
MYSQL_ROOT_PASSWORD=nueva_root_password
```

2. Recrear contenedores:
```bash
docker-compose down
docker-compose up -d
```

### **Usuarios de base de datos**
```bash
# Crear usuario de solo lectura
docker-compose exec mysql mysql -u root -p -e "
CREATE USER 'readonly'@'%' IDENTIFIED BY 'readonly_pass';
GRANT SELECT ON inventario_network_db.* TO 'readonly'@'%';
FLUSH PRIVILEGES;"
```

---

## ⚡ Performance

### **Escalado horizontal**
```bash
# Múltiples instancias de Django
docker-compose up --scale web=3 -d

# Load balancer automático con Nginx
# (Nginx distribuirá automáticamente las requests)
```

### **Optimización de recursos**
```bash
# Limitar memoria de contenedores
docker-compose exec web docker update --memory=1g att_django_web
docker-compose exec mysql docker update --memory=2g att_inventario_mysql
```

### **Cache con Redis**
```bash
# Ver estadísticas de Redis
docker-compose exec redis redis-cli info stats

# Limpiar cache
docker-compose exec redis redis-cli flushall
```

---

## 🔧 Configuración Avanzada

### **Variables de entorno disponibles**

#### Django (web service):
```env
# Database
DB_HOST=mysql
DB_PORT=3306
DB_NAME=inventario_network_db
DB_USER=att_inventario
DB_PASSWORD=att_secure_2024

# Django
DJANGO_DEVELOPMENT=true
DEBUG=true
SECRET_KEY=your-secret-key
DJANGO_SETTINGS_MODULE=core.settings

# Superuser (solo desarrollo)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@att.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

#### MySQL (mysql service):
```env
MYSQL_ROOT_PASSWORD=att_root_2024
MYSQL_DATABASE=inventario_network_db
MYSQL_USER=att_inventario
MYSQL_PASSWORD=att_secure_2024
```

### **Personalizar configuraciones**

#### Nginx personalizado:
```bash
# Editar configuración
nano docker/nginx.conf

# Aplicar cambios
docker-compose restart nginx
```

#### MySQL personalizado:
```bash
# Crear configuración personalizada
echo "[mysqld]
max_connections = 500
innodb_buffer_pool_size = 1G" > docker/mysql.cnf

# Agregar volumen en docker-compose.yml:
# - ./docker/mysql.cnf:/etc/mysql/conf.d/custom.cnf
```

---

## 📊 Monitoreo y Métricas

### **Health Checks**
```bash
# Verificar salud de todos los servicios
docker-compose ps

# Health check manual
curl -f http://localhost/health/ || echo "Django no responde"
docker-compose exec mysql mysqladmin ping || echo "MySQL no responde"
docker-compose exec redis redis-cli ping || echo "Redis no responde"
```

### **Métricas de performance**
```bash
# Uso de recursos en tiempo real
docker stats

# Específico por contenedor
docker stats att_django_web att_inventario_mysql att_nginx att_redis
```

---

## 🚨 Troubleshooting

### **Problemas comunes**

#### 1. **Django no se conecta a MySQL**
```bash
# Verificar que MySQL esté listo
docker-compose logs mysql | grep "ready for connections"

# Test de conectividad
docker-compose exec web python manage.py dbshell --command="SELECT 1;"
```

#### 2. **Nginx devuelve 502 Bad Gateway**
```bash
# Verificar que Django esté corriendo
docker-compose exec web curl -f http://localhost:8000/

# Ver logs de Nginx
docker-compose logs nginx
```

#### 3. **Archivos estáticos no se sirven**
```bash
# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Verificar permisos
docker-compose exec web ls -la /app/staticfiles/
```

#### 4. **Permisos de archivos**
```bash
# Corregir permisos (si es necesario)
docker-compose exec web chown -R django:django /app/media
docker-compose exec web chown -R django:django /app/logs
```

### **Reset completo**
```bash
# ⚠️ ESTO ELIMINA TODOS LOS DATOS ⚠️
docker-compose down -v
docker system prune -a --volumes
docker-compose up --build -d
```

---

## 📚 Referencias

### **Archivos importantes**
- `Dockerfile` - Configuración del contenedor Django
- `docker-compose.yml` - Orquestación de servicios (producción)
- `docker-compose.dev.yml` - Override para desarrollo
- `docker/nginx.conf` - Configuración de Nginx
- `docker/entrypoint.sh` - Script de inicialización
- `.dockerignore` - Archivos excluidos del build

### **Puertos utilizados**
- **80**: Nginx (producción)
- **8000**: Django (desarrollo)
- **3306**: MySQL
- **6379**: Redis

### **Volúmenes persistentes**
- `mysql_data`: Datos de MySQL
- `redis_data`: Datos de Redis
- `./media`: Archivos subidos
- `./staticfiles`: Archivos estáticos
- `./logs`: Logs de la aplicación
- `./backups`: Backups de base de datos

---

**🎯 AT&T Executive Portal - Containerized Infrastructure**  
**Fecha:** $(date +%Y-%m-%d)  
**Stack:** Django + MySQL + Redis + Nginx + Docker 