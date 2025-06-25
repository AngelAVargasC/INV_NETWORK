# Usar Python 3.11 slim para mejor performance
FROM python:3.11-slim

# Información del mantenedor
LABEL maintainer="AT&T Executive Portal Team"
LABEL description="AT&T Inventario Network App - Executive Portal"

# Configurar zona horaria para México
ENV TZ=America/Mexico_City
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root para seguridad
RUN groupadd -r django && useradd --no-log-init -r -g django django

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # Base de datos
        postgresql-client \
        default-mysql-client \
        # Compilación
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        # Utilities
        curl \
        wget \
        # Limpieza
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . /app/

# Crear directorios necesarios con permisos correctos
RUN mkdir -p /app/logs /app/media /app/staticfiles /app/backups \
    && chown -R django:django /app \
    && chmod 755 /app/logs /app/media /app/staticfiles

# Cambiar a usuario no-root
USER django

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 