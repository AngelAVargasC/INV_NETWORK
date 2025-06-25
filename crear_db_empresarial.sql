-- =============================================================================
-- SCRIPT PARA CREAR BASE DE DATOS INVENTARIO EN MYSQL EMPRESARIAL
-- =============================================================================
-- Para ser ejecutado por el administrador de base de datos
-- MySQL Server: 10.150.153.31:3306

-- 1. Verificar bases de datos existentes (NO MODIFICAR)
SHOW DATABASES;

-- 2. Crear base de datos específica para AT&T Inventario
CREATE DATABASE IF NOT EXISTS inventario_network_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- 3. Verificar creación
SHOW DATABASES LIKE 'inventario%';

-- 4. (OPCIONAL) Crear usuario específico para mayor seguridad
-- Si prefieren no usar root, crear usuario dedicado:
/*
CREATE USER 'att_inventario'@'%' IDENTIFIED BY 'att_secure_2024_inv';
GRANT ALL PRIVILEGES ON inventario_network_db.* TO 'att_inventario'@'%';
FLUSH PRIVILEGES;

-- Verificar permisos
SHOW GRANTS FOR 'att_inventario'@'%';
*/

-- 5. Usar la base de datos para verificar
USE inventario_network_db;

-- 6. Mostrar información de la base de datos
SELECT 
    SCHEMA_NAME as 'Base de Datos',
    DEFAULT_CHARACTER_SET_NAME as 'Charset',
    DEFAULT_COLLATION_NAME as 'Collation'
FROM information_schema.SCHEMATA 
WHERE SCHEMA_NAME = 'inventario_network_db';

-- =============================================================================
-- COMANDOS DE VERIFICACIÓN SEGURA
-- =============================================================================

-- Verificar que no interfiere con otras DBs
SELECT SCHEMA_NAME FROM information_schema.SCHEMATA 
WHERE SCHEMA_NAME NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys', 'inventario_network_db')
ORDER BY SCHEMA_NAME;

-- Verificar espacio disponible
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
GROUP BY table_schema
ORDER BY SUM(data_length + index_length) DESC;

-- =============================================================================
-- NOTAS IMPORTANTES:
-- 
-- 1. Este script SOLO crea la base de datos 'inventario_network_db'
-- 2. NO modifica ni interfiere con otras bases de datos existentes
-- 3. Las tablas se crearán automáticamente con las migraciones de Django
-- 4. Si ya existe la base de datos, el script no hace nada (IF NOT EXISTS)
-- 5. Usar usuario 'root' con password 's3cr3t00!' como en la configuración
-- ============================================================================= 