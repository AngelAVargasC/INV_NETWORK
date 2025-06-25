# Sistema de Avatares de Usuario - AT&T PMO

## Descripción
Sistema completo de avatares de usuario implementado en el Portal Ejecutivo AT&T PMO que permite mostrar imágenes de perfil tanto en el sidebar como en la navbar de todos los templates del proyecto.

## Características Implementadas

### 1. Modelo de Perfil Usuario
- **Ubicación**: `apps/usuarios/models.py`
- **Campo de imagen**: `foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)`
- **Creación automática**: Se crea automáticamente al registrar un usuario mediante señales Django

### 2. Context Processor Global
- **Archivo**: `apps/usuarios/context_processors.py`
- **Función**: `perfil_usuario(request)`
- **Variables disponibles**:
  - `user_profile`: Instancia del perfil del usuario actual
  - `user_has_photo`: Boolean que indica si el usuario tiene foto

### 3. Templates Actualizados

#### Template Ejecutivo (`base.html`)
**Sidebar:**
```html
<div class="profile-avatar">
    {% if user_has_photo %}
        <img src="{{ user_profile.foto_perfil.url }}" alt="Avatar {{ user.get_full_name|default:user.username }}">
    {% else %}
        <div class="default-avatar">
            <i class="fas fa-user-tie"></i>
        </div>
    {% endif %}
</div>
```

**Header/Navbar:**
```html
<div class="user-avatar-header">
    {% if user_has_photo %}
        <img src="{{ user_profile.foto_perfil.url }}" alt="Avatar {{ user.get_full_name|default:user.username }}">
    {% else %}
        <div class="default-avatar-header">
            <i class="fas fa-user-tie"></i>
        </div>
    {% endif %}
</div>
```

#### Template Simple (`base_att.html`)
**Navbar:**
```html
{% if user_has_photo %}
    <img src="{{ user_profile.foto_perfil.url }}" alt="Avatar {{ user.get_full_name|default:user.username }}" class="user-avatar-nav">
{% else %}
    <i class="fas fa-user-circle"></i>
{% endif %}
```

### 4. Estilos CSS Implementados

#### Avatares del Sidebar
```css
.profile-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    transition: all var(--transition-normal);
    cursor: pointer;
}

.profile-avatar:hover {
    transform: scale(1.1);
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: var(--shadow-strong);
}
```

#### Avatares del Header
```css
.user-avatar-header {
    width: 36px;
    height: 36px;
    border: 2px solid var(--att-gray-200);
    transition: all var(--transition-fast);
}

.user-avatar-header:hover {
    border-color: var(--att-primary);
    transform: scale(1.05);
}
```

#### Avatares del Navbar Simple
```css
.user-avatar-nav {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.3);
    transition: all var(--transition-fast);
}

.user-avatar-nav:hover {
    border-color: rgba(255, 255, 255, 0.8);
    transform: scale(1.05);
}
```

## Configuración

### Context Processor Registrado
En `core/settings.py`:
```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.usuarios.context_processors.perfil_usuario',  # ← Agregado
            ],
        },
    },
]
```

## Funcionalidades

### ✅ Implementado
- [x] Mostrar imagen de perfil en sidebar del template ejecutivo
- [x] Mostrar imagen de perfil en header del template ejecutivo
- [x] Mostrar imagen de perfil en navbar del template simple
- [x] Fallback a íconos FontAwesome cuando no hay imagen
- [x] Context processor global para disponibilidad en todos los templates
- [x] Estilos CSS con efectos hover y transiciones suaves
- [x] Responsive design
- [x] Alt text descriptivo para accesibilidad

### 🎨 Efectos Visuales
- Hover effects con scale y border changes
- Transiciones suaves
- Sombras dinámicas
- Bordes con colores corporativos AT&T

## Uso

### Para los usuarios:
1. Ir a **Mi Perfil** desde el menú del usuario
2. Cargar una imagen en el campo "Foto de Perfil"
3. La imagen aparecerá automáticamente en sidebar y navbar

### Para desarrolladores:
- Las variables `user_profile` y `user_has_photo` están disponibles en todos los templates
- Los estilos están centralizados en `static/css/att-global.css`
- El sistema es automático y no requiere configuración adicional

## Estructura de Archivos
```
INVENTARIO_NETWORK_APP/
├── apps/usuarios/
│   ├── context_processors.py     # Context processor global
│   ├── models.py                 # Modelo PerfilUsuario
│   └── views.py                  # Vistas de perfil
├── templates/
│   ├── base.html                 # Template ejecutivo
│   ├── base_att.html             # Template simple
│   └── usuarios/perfil.html      # Página de perfil
├── static/css/
│   └── att-global.css            # Estilos de avatares
└── media/perfiles/               # Carpeta de imágenes
```

## Compatibilidad
- ✅ Funciona con ambos templates base
- ✅ Compatible con usuarios con y sin foto
- ✅ Responsive en móviles y desktop
- ✅ Accesible con alt text
- ✅ Fallback seguro a íconos FontAwesome 