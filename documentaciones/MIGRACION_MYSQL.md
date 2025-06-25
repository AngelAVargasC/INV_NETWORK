# 🚀 Guía de Migración a MySQL

## 📋 Requisitos Previos

1. **Instalar MySQL Server**
   ```bash
   # Windows (usando Chocolatey)
   choco install mysql
   
   # O descargar desde: https://dev.mysql.com/downloads/mysql/
   ```

2. **Instalar cliente MySQL para Python**
   ```bash
   pip install mysqlclient
   # o alternativamente:
   pip install PyMySQL
   ```

## 🔧 Pasos de Migración

### 1. Crear Base de Datos MySQL
```sql
CREATE DATABASE inventario_network_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'inventario_user'@'localhost' IDENTIFIED BY 'tu_password_seguro';
GRANT ALL PRIVILEGES ON inventario_network_db.* TO 'inventario_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Actualizar Configuración Django
En `core/settings.py`, reemplazar la configuración de DATABASES:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'inventario_network_db',
        'USER': 'inventario_user',
        'PASSWORD': 'tu_password_seguro', 
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'autocommit': True,
        },
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
    }
}
```

### 3. Migrar Datos Existentes

#### Opción A: Usando Django (Recomendado)
```bash
# 1. Exportar datos desde SQLite
python manage.py dumpdata --natural-foreign --natural-primary > backup_data.json

# 2. Cambiar configuración a MySQL
# 3. Aplicar migraciones
python manage.py migrate

# 4. Importar datos
python manage.py loaddata backup_data.json
```

#### Opción B: Re-importar desde Excel
```bash
# Simplemente volver a importar tu archivo Updated_Agin.xlsx
# La nueva configuración optimizada funcionará automáticamente
```

## ⚡ Optimizaciones MySQL Incluidas

### Rendimiento de Importación
- **Lotes de 2000 registros** (vs 1000 en SQLite)
- **Desactivación temporal de checks** durante bulk operations
- **Conexiones persistentes** con `CONN_MAX_AGE`
- **Autocommit optimizado** para operaciones masivas

### Configuraciones MySQL Específicas
```sql
-- Estas se ejecutan automáticamente durante la importación:
SET autocommit = 0;           -- Control manual de commits
SET unique_checks = 0;        -- Desactivar checks de unicidad temporalmente  
SET foreign_key_checks = 0;   -- Desactivar FK checks temporalmente
```

## 📊 Mejoras de Rendimiento Esperadas

| Base de Datos | Tiempo (33K registros) | Lote Óptimo |
|---------------|------------------------|-------------|
| SQLite        | 3-8 segundos          | 1000        |
| **MySQL**     | **2-5 segundos**      | **2000**    |
| PostgreSQL    | 1-3 segundos          | 5000        |

## 🔒 Configuraciones de Seguridad

### Variables de Entorno (Recomendado)
Crear archivo `.env`:
```env
DB_NAME=inventario_network_db
DB_USER=inventario_user
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=3306
```

Actualizar `settings.py`:
```python
import os
from dotenv import load_dotenv
load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        # ... resto de opciones
    }
}
```

## 🚨 Puntos Importantes

1. **Compatibilidad**: El código actual funciona 100% con MySQL sin cambios
2. **Rendimiento**: MySQL será más rápido para las importaciones masivas
3. **Escalabilidad**: MySQL maneja mejor múltiples usuarios concurrentes
4. **Backup**: MySQL tiene mejores herramientas de respaldo empresarial

## 🔧 Comandos Útiles Post-Migración

```bash
# Verificar la migración
python manage.py showmigrations

# Optimizar tablas MySQL
python manage.py dbshell
OPTIMIZE TABLE inventario_articulo;

# Backup regular
mysqldump -u inventario_user -p inventario_network_db > backup.sql
```

## 📈 Beneficios Adicionales MySQL

- **Concurrencia mejorada**: Múltiples usuarios sin bloqueos
- **Índices más eficientes**: Mejor rendimiento en consultas complejas  
- **Replicación**: Posibilidad de configurar réplicas para backup
- **Herramientas**: phpMyAdmin, MySQL Workbench, etc.
- **Escalabilidad**: Manejo de millones de registros sin problemas

¡La migración será transparente y obtendrás mejor rendimiento! 🚀 