# 🚀 Sistema de Inventario Network App

Una aplicación Django moderna y profesional para la gestión de inventario de artículos no capitalizados de diferentes áreas de una empresa.

## ✨ Características

- ✅ **Arquitectura Profesional**: Estructura escalable con `core` como núcleo
- ✅ **Sistema de Autenticación**: Login, logout y registro completo
- ✅ **Gestión de Perfiles**: Perfiles extendidos con información laboral
- ✅ **Dashboard Moderno**: Interfaz responsiva y profesional
- ✅ **Diseño Bootstrap 5**: UI/UX moderna y homologada
- ✅ **Estructura MVT**: Siguiendo las mejores prácticas de Django

## 🏗️ Arquitectura del Proyecto

### Estructura Profesional

```
INVENTARIO_NETWORK_APP/
├── 📂 core/                    # 🎯 NÚCLEO DEL PROYECTO
│   ├── settings.py             # Configuración principal
│   ├── urls.py                 # URLs principales del proyecto
│   ├── views.py                # Vistas core (home, dashboard)
│   ├── wsgi.py                 # WSGI para producción
│   └── asgi.py                 # ASGI para async
│
├── 📂 apps/                    # 📦 APLICACIONES DEL PROYECTO
│   ├── __init__.py             # Paquete Python
│   └── 📂 usuarios/            # App gestión de usuarios
│       ├── models.py           # PerfilUsuario model
│       ├── views.py            # Auth views
│       ├── forms.py            # Formularios
│       ├── urls.py             # URLs usuarios
│       ├── admin.py            # Admin config
│       └── migrations/         # DB migrations
│
├── 📂 templates/               # 🎨 TEMPLATES HTML
│   ├── base.html               # Template base moderno
│   ├── 📂 core/
│   │   └── home.html           # Dashboard principal
│   └── 📂 usuarios/
│       ├── login.html          # Login elegante
│       ├── registro.html       # Registro de usuarios
│       └── perfil.html         # Gestión de perfil
│
├── 📂 static/                  # 📋 ARCHIVOS ESTÁTICOS
├── 📂 media/                   # 📷 ARCHIVOS DE USUARIO
└── 📄 manage.py                # Django management script
```

## 🚀 Instalación y Configuración

### 1. Clonar el Proyecto
```bash
git clone <repository-url>
cd INVENTARIO_NETWORK_APP
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
```

### 3. Activar Entorno Virtual

**Windows:**
```bash
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Aplicar Migraciones
```bash
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7. Ejecutar Servidor
```bash
python manage.py runserver
```

## 🌐 URLs del Sistema

- **`/`** - Dashboard principal (requiere login)
- **`/login/`** - Página de inicio de sesión
- **`/logout/`** - Cerrar sesión
- **`/registro/`** - Registro de nuevos usuarios
- **`/usuarios/perfil/`** - Gestión de perfil de usuario
- **`/admin/`** - Panel de administración Django

## 🔧 Tecnologías Utilizadas

- **Backend**: Django 5.2.3
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Base de Datos**: SQLite (desarrollo)
- **Imágenes**: Pillow
- **Idioma**: Español (México)

---

**🏢 Desarrollado para la gestión eficiente de inventarios empresariales** 🚀 