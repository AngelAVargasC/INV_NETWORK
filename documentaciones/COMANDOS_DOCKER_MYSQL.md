# 🐳 Comandos Docker para MySQL - AT&T Executive Portal

## 📋 Índice
- [Gestión del Contenedor](#gestión-del-contenedor)
- [Acceso a MySQL](#acceso-a-mysql)
- [Backups y Restauración](http://localhost:8080)
- [Monitoreo y Análisis](#monitoreo-y-análisis)
- [Configuración Avanzada](#configuración-avanzada)
- [Seguridad](#seguridad)
- [Escalabilidad](#escalabilidad)
- [Herramientas Adicionales](#herramientas-adicionales)
- [Comandos de Emergencia](#comandos-de-emergencia)

---

## 🔧 Gestión del Contenedor

### Comandos básicos de contenedor
```bash
# Ver estado de contenedores
docker ps
docker ps -a  # Incluir contenedores parados

# Estadísticas en tiempo real
docker stats att_inventario_mysql

# Controlar el contenedor
docker stop att_inventario_mysql
docker start att_inventario_mysql
docker restart att_inventario_mysql

# Eliminar contenedor (¡CUIDADO!)
docker rm att_inventario_mysql

# Ver logs
docker logs att_inventario_mysql
docker logs -f att_inventario_mysql  # Seguir logs en tiempo real
docker logs --tail 100 att_inventario_mysql  # Últimas 100 líneas
```

### Docker Compose
```bash
# Levantar todos los servicios
docker-compose up -d

# Levantar solo MySQL
docker-compose up -d mysql

# Ver estado de servicios
docker-compose ps

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes (¡CUIDADO!)
docker-compose down -v

# Ver logs de servicios
docker-compose logs mysql
docker-compose logs -f mysql
```

---

## 💻 Acceso a MySQL

### Conexión directa
```bash
# Conectar como usuario de la aplicación
docker exec -it att_inventario_mysql mysql -u att_inventario -p

# Conectar como root
docker exec -it att_inventario_mysql mysql -u root -p

# Ejecutar comando específico
docker exec att_inventario_mysql mysql -u att_inventario -p -e "SHOW DATABASES;"

# Acceder al shell del contenedor
docker exec -it att_inventario_mysql bash

# Ejecutar script SQL desde archivo
docker exec -i att_inventario_mysql mysql -u att_inventario -p inventario_network_db < script.sql
```

### Comandos MySQL útiles
```sql
-- Una vez conectado a MySQL:
USE inventario_network_db;
SHOW TABLES;
DESCRIBE inventario_articulo;
SELECT COUNT(*) FROM inventario_articulo;
SHOW PROCESSLIST;
SHOW VARIABLES LIKE 'version';
```

---

## 💾 Backups y Restauración

### Crear backups
```bash
# Backup completo
docker exec att_inventario_mysql mysqldump -u att_inventario -patt_secure_2024 inventario_network_db > backup_$(date +%Y%m%d).sql

# Backup comprimido
docker exec att_inventario_mysql mysqldump -u att_inventario -patt_secure_2024 inventario_network_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup solo estructura (sin datos)
docker exec att_inventario_mysql mysqldump -u att_inventario -patt_secure_2024 --no-data inventario_network_db > estructura.sql

# Backup solo datos (sin estructura)
docker exec att_inventario_mysql mysqldump -u att_inventario -patt_secure_2024 --no-create-info inventario_network_db > datos.sql

# Backup de tabla específica
docker exec att_inventario_mysql mysqldump -u att_inventario -patt_secure_2024 inventario_network_db inventario_articulo > backup_articulos.sql

# Backup con fecha en nombre
docker exec att_inventario_mysql mysqldump -u att_inventario -patt_secure_2024 inventario_network_db > "backup_inventario_$(date +%Y%m%d_%H%M%S).sql"
```

### Restaurar backups
```bash
# Restaurar desde archivo
docker exec -i att_inventario_mysql mysql -u att_inventario -patt_secure_2024 inventario_network_db < backup.sql

# Restaurar desde archivo comprimido
gunzip < backup.sql.gz | docker exec -i att_inventario_mysql mysql -u att_inventario -patt_secure_2024 inventario_network_db

# Restaurar creando nueva base de datos
docker exec att_inventario_mysql mysql -u root -p -e "CREATE DATABASE inventario_backup;"
docker exec -i att_inventario_mysql mysql -u root -p inventario_backup < backup.sql
```

### Backup automático (Cron)
```bash
# Agregar a crontab para backup diario a las 2 AM
echo "0 2 * * * docker exec att_inventario_mysql mysqldump -u att_inventario -patt_secure_2024 inventario_network_db > /backup/inventario_\$(date +\%Y\%m\%d).sql" | crontab -

# Ver tareas cron actuales
crontab -l

# Editar crontab
crontab -e
```

---

## 🔍 Monitoreo y Análisis

### Performance del contenedor
```bash
# Uso de recursos en tiempo real
docker stats att_inventario_mysql

# Información detallada del contenedor
docker inspect att_inventario_mysql

# Procesos corriendo en el contenedor
docker exec att_inventario_mysql ps aux

# Espacio en disco usado por el contenedor
docker exec att_inventario_mysql df -h

# Memoria usada por MySQL
docker exec att_inventario_mysql mysql -u root -p -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size';"
```

### Análisis de la base de datos
```bash
# Ver tamaño de todas las bases de datos
docker exec att_inventario_mysql mysql -u root -p -e "
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
GROUP BY table_schema;"

# Ver tablas más grandes
docker exec att_inventario_mysql mysql -u root -p inventario_network_db -e "
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
    table_rows AS 'Rows'
FROM information_schema.TABLES 
WHERE table_schema = 'inventario_network_db'
ORDER BY (data_length + index_length) DESC;"

# Procesos MySQL activos
docker exec att_inventario_mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# Status del servidor
docker exec att_inventario_mysql mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
docker exec att_inventario_mysql mysql -u root -p -e "SHOW STATUS LIKE 'Queries';"
docker exec att_inventario_mysql mysql -u root -p -e "SHOW STATUS LIKE 'Uptime';"
```

### Análisis de queries
```bash
# Habilitar log de queries lentas
docker exec att_inventario_mysql mysql -u root -p -e "
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';"

# Ver queries lentas
docker exec att_inventario_mysql tail -f /var/log/mysql/slow.log
```

---

## ⚙️ Configuración Avanzada

### Ver configuración actual
```bash
# Ver archivo de configuración principal
docker exec att_inventario_mysql cat /etc/mysql/my.cnf

# Ver todas las variables de configuración
docker exec att_inventario_mysql mysql -u root -p -e "SHOW VARIABLES;" > mysql_config.txt

# Variables específicas
docker exec att_inventario_mysql mysql -u root -p -e "SHOW VARIABLES LIKE 'innodb%';"
docker exec att_inventario_mysql mysql -u root -p -e "SHOW VARIABLES LIKE 'max_connections';"
```

### Configuración personalizada
```bash
# Crear archivo de configuración personalizada
cat > custom-mysql.cnf << EOF
[mysqld]
max_connections = 500
innodb_buffer_pool_size = 1G
query_cache_size = 64M
query_cache_type = 1
slow_query_log = 1
long_query_time = 2
EOF

# Aplicar configuración (agregar a docker-compose.yml)
# volumes:
#   - ./custom-mysql.cnf:/etc/mysql/conf.d/custom.cnf
```

### Optimización de tablas
```bash
# Analizar y optimizar tablas
docker exec att_inventario_mysql mysql -u root -p inventario_network_db -e "
ANALYZE TABLE inventario_articulo;
OPTIMIZE TABLE inventario_articulo;
CHECK TABLE inventario_articulo;
REPAIR TABLE inventario_articulo;"

# Ver índices de una tabla
docker exec att_inventario_mysql mysql -u root -p inventario_network_db -e "
SHOW INDEX FROM inventario_articulo;"

# Ver estadísticas de una tabla
docker exec att_inventario_mysql mysql -u root -p inventario_network_db -e "
SHOW TABLE STATUS LIKE 'inventario_articulo';"
```

---

## 🛡️ Seguridad

### Gestión de usuarios
```bash
# Crear usuario de solo lectura
docker exec att_inventario_mysql mysql -u root -p -e "
CREATE USER 'readonly'@'%' IDENTIFIED BY 'readonly_pass';
GRANT SELECT ON inventario_network_db.* TO 'readonly'@'%';
FLUSH PRIVILEGES;"

# Crear usuario para backups
docker exec att_inventario_mysql mysql -u root -p -e "
CREATE USER 'backup_user'@'localhost' IDENTIFIED BY 'backup_pass';
GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER ON inventario_network_db.* TO 'backup_user'@'localhost';
FLUSH PRIVILEGES;"

# Ver usuarios existentes
docker exec att_inventario_mysql mysql -u root -p -e "
SELECT user, host, authentication_string FROM mysql.user;"

# Ver permisos de un usuario
docker exec att_inventario_mysql mysql -u root -p -e "
SHOW GRANTS FOR 'att_inventario'@'%';"

# Eliminar usuario
docker exec att_inventario_mysql mysql -u root -p -e "
DROP USER 'usuario_a_eliminar'@'%';"
```

### Verificaciones de seguridad
```bash
# Verificar SSL
docker exec att_inventario_mysql mysql -u root -p -e "SHOW VARIABLES LIKE 'have_ssl';"

# Ver conexiones actuales
docker exec att_inventario_mysql mysql -u root -p -e "
SELECT USER, HOST, DB, COMMAND, TIME, STATE 
FROM information_schema.PROCESSLIST 
WHERE USER != 'system user';"

# Verificar configuración de seguridad
docker exec att_inventario_mysql mysql -u root -p -e "
SHOW VARIABLES LIKE 'validate_password%';"
```

---

## 🚀 Escalabilidad

### Múltiples ambientes en docker-compose.yml
```yaml
# Ejemplo de configuración multi-ambiente
version: '3.8'

services:
  mysql-dev:
    image: mysql:8.0
    container_name: att_mysql_dev
    environment:
      MYSQL_ROOT_PASSWORD: dev_root_2024
      MYSQL_DATABASE: inventario_dev
      MYSQL_USER: dev_user
      MYSQL_PASSWORD: dev_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_dev_data:/var/lib/mysql
    networks:
      - att_network

  mysql-test:
    image: mysql:8.0
    container_name: att_mysql_test
    environment:
      MYSQL_ROOT_PASSWORD: test_root_2024
      MYSQL_DATABASE: inventario_test
      MYSQL_USER: test_user
      MYSQL_PASSWORD: test_pass
    ports:
      - "3307:3306"
    volumes:
      - mysql_test_data:/var/lib/mysql
    networks:
      - att_network

volumes:
  mysql_dev_data:
  mysql_test_data:

networks:
  att_network:
    driver: bridge
```

### Comandos para múltiples ambientes
```bash
# Conectar a ambiente de desarrollo
docker exec -it att_mysql_dev mysql -u dev_user -p

# Conectar a ambiente de testing
docker exec -it att_mysql_test mysql -u test_user -p

# Migrar datos entre ambientes
docker exec att_mysql_dev mysqldump -u dev_user -pdev_pass inventario_dev | docker exec -i att_mysql_test mysql -u test_user -ptest_pass inventario_test
```

---

## 🌐 Herramientas Adicionales

### Agregar phpMyAdmin
```yaml
# Agregar a docker-compose.yml
  phpmyadmin:
    image: phpmyadmin:latest
    container_name: att_phpmyadmin
    restart: unless-stopped
    ports:
      - "8080:80"
    environment:
      PMA_HOST: mysql
      PMA_USER: att_inventario
      PMA_PASSWORD: att_secure_2024
    depends_on:
      - mysql
    networks:
      - att_network
```

```bash
# Comandos para phpMyAdmin
docker-compose up -d phpmyadmin
# Acceder: http://localhost:8080
```

### Agregar Adminer (alternativa ligera)
```yaml
# Agregar a docker-compose.yml
  adminer:
    image: adminer:latest
    container_name: att_adminer
    restart: unless-stopped
    ports:
      - "8081:8080"
    networks:
      - att_network
```

```bash
# Comandos para Adminer
docker-compose up -d adminer
# Acceder: http://localhost:8081
```

---

## 🚨 Comandos de Emergencia

### Recuperación de datos
```bash
# Acceso de emergencia si olvidas contraseñas
docker exec -it att_inventario_mysql mysql --skip-grant-tables

# Resetear contraseña de root
docker exec att_inventario_mysql mysql -u root -p -e "
ALTER USER 'root'@'localhost' IDENTIFIED BY 'nueva_contraseña';
FLUSH PRIVILEGES;"

# Recrear usuario si se corrompe
docker exec att_inventario_mysql mysql -u root -p -e "
DROP USER IF EXISTS 'att_inventario'@'%';
CREATE USER 'att_inventario'@'%' IDENTIFIED BY 'att_secure_2024';
GRANT ALL PRIVILEGES ON inventario_network_db.* TO 'att_inventario'@'%';
FLUSH PRIVILEGES;"
```

### Limpiar espacio
```bash
# Limpiar logs binarios antiguos
docker exec att_inventario_mysql mysql -u root -p -e "PURGE BINARY LOGS BEFORE DATE_SUB(NOW(), INTERVAL 7 DAY);"

# Limpiar logs de error antiguos
docker exec att_inventario_mysql truncate -s 0 /var/log/mysql/error.log

# Optimizar todas las tablas
docker exec att_inventario_mysql mysql -u root -p inventario_network_db -e "
SELECT CONCAT('OPTIMIZE TABLE ', table_name, ';') 
FROM information_schema.tables 
WHERE table_schema = 'inventario_network_db';"
```

### Recrear contenedor manteniendo datos
```bash
# Backup antes de recrear
docker exec att_inventario_mysql mysqldump -u att_inventario -patt_secure_2024 inventario_network_db > backup_before_recreate.sql

# Parar y eliminar contenedor (mantiene volúmenes)
docker stop att_inventario_mysql
docker rm att_inventario_mysql

# Recrear contenedor
docker-compose up -d mysql

# Verificar que los datos están intactos
docker exec att_inventario_mysql mysql -u att_inventario -patt_secure_2024 -e "SELECT COUNT(*) FROM inventario_network_db.inventario_articulo;"
```

---

## 📚 Notas Importantes

### ⚠️ Precauciones
- **SIEMPRE** hacer backup antes de cambios importantes
- **NUNCA** usar `docker-compose down -v` en producción
- **VERIFICAR** conexiones antes de eliminar contenedores
- **PROBAR** restauraciones en ambiente de desarrollo

### 🔐 Seguridad
- Cambiar contraseñas por defecto en producción
- Usar variables de entorno para credenciales
- Limitar acceso por IP en producción
- Habilitar SSL/TLS para conexiones remotas

### 📊 Monitoreo recomendado
- Configurar alertas para espacio en disco
- Monitorear conexiones concurrentes
- Revisar logs de queries lentas regularmente
- Hacer backups automáticos diarios

---

**Creado para AT&T Executive Portal - Proyecto de Inventario**  
**Fecha:** $(date +%Y-%m-%d)  
**Versión:** MySQL 8.0 en Docker 