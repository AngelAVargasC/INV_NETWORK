from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.inventario.models import Fabrica, EstatusPMO, Categoria, Articulo
from apps.usuarios.models import PerfilUsuario
from datetime import date, timedelta
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el sistema de inventario PMO'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=50,
            help='Cantidad de artículos a crear'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        
        self.stdout.write(
            self.style.SUCCESS(f'Creando datos de ejemplo para el sistema PMO...')
        )
        
        # Crear fábricas
        fabricas_data = [
            {'nombre': 'Fábrica México Central', 'codigo': 'MX_CENTRAL', 'ubicacion': 'Ciudad de México, México'},
            {'nombre': 'SOFOLES Norte', 'codigo': 'SOFOLES_N', 'ubicacion': 'Monterrey, México'},
            {'nombre': 'Planta Occidente', 'codigo': 'PLANTA_OCC', 'ubicacion': 'Guadalajara, México'},
            {'nombre': 'División Sureste', 'codigo': 'DIV_SE', 'ubicacion': 'Mérida, México'},
            {'nombre': 'Centro Operativo Bajío', 'codigo': 'CO_BAJIO', 'ubicacion': 'León, México'},
        ]
        
        fabricas = []
        for fab_data in fabricas_data:
            fabrica, created = Fabrica.objects.get_or_create(
                codigo=fab_data['codigo'],
                defaults=fab_data
            )
            fabricas.append(fabrica)
            if created:
                self.stdout.write(f'  ✓ Fábrica creada: {fabrica.nombre}')
        
        # Crear estados PMO
        estados_data = [
            {'estado': 'PLANIFICACION', 'descripcion': 'Proyecto en fase de planificación', 'color': '#6c757d', 'orden': 1},
            {'estado': 'APROBADO', 'descripcion': 'Proyecto aprobado para ejecución', 'color': '#007bff', 'orden': 2},
            {'estado': 'EN_PROCESO', 'descripcion': 'Proyecto en desarrollo activo', 'color': '#fd7e14', 'orden': 3},
            {'estado': 'REVISION', 'descripcion': 'Proyecto en revisión de calidad', 'color': '#ffc107', 'orden': 4},
            {'estado': 'COMPLETADO', 'descripcion': 'Proyecto finalizado exitosamente', 'color': '#28a745', 'orden': 5},
            {'estado': 'PENDIENTE', 'descripcion': 'Proyecto en espera de recursos', 'color': '#dc3545', 'orden': 6},
            {'estado': 'CANCELADO', 'descripcion': 'Proyecto cancelado', 'color': '#6f42c1', 'orden': 7},
            {'estado': 'SUSPENDIDO', 'descripcion': 'Proyecto temporalmente suspendido', 'color': '#e83e8c', 'orden': 8},
        ]
        
        estados = []
        for estado_data in estados_data:
            estado, created = EstatusPMO.objects.get_or_create(
                estado=estado_data['estado'],
                defaults=estado_data
            )
            estados.append(estado)
            if created:
                self.stdout.write(f'  ✓ Estado PMO creado: {estado.get_estado_display()}')
        
        # Crear categorías
        categorias_data = [
            {'nombre': 'Infraestructura Tecnológica', 'codigo': 'INFRA_TEC'},
            {'nombre': 'Desarrollo de Software', 'codigo': 'DEV_SOFT'},
            {'nombre': 'Mantenimiento Industrial', 'codigo': 'MANT_IND'},
            {'nombre': 'Equipos de Producción', 'codigo': 'EQUIP_PROD'},
            {'nombre': 'Sistemas de Calidad', 'codigo': 'SIS_CALIDAD'},
            {'nombre': 'Seguridad y Cumplimiento', 'codigo': 'SEG_CUMPL'},
            {'nombre': 'Capacitación del Personal', 'codigo': 'CAP_PERS'},
            {'nombre': 'Mejora de Procesos', 'codigo': 'MEJ_PROC'},
        ]
        
        categorias = []
        for cat_data in categorias_data:
            categoria, created = Categoria.objects.get_or_create(
                codigo=cat_data['codigo'],
                defaults=cat_data
            )
            categorias.append(categoria)
            if created:
                self.stdout.write(f'  ✓ Categoría creada: {categoria.nombre}')
        
        # Obtener usuarios para asignar como responsables
        usuarios = list(User.objects.all())
        if not usuarios:
            self.stdout.write(
                self.style.WARNING('No hay usuarios en el sistema. Creando usuario de ejemplo...')
            )
            usuario_ejemplo = User.objects.create_user(
                username='admin_pmo',
                email='admin@pmo.com',
                password='password123',
                first_name='Admin',
                last_name='PMO'
            )
            usuarios = [usuario_ejemplo]
        
        # Crear artículos de ejemplo
        self.stdout.write(f'Creando {cantidad} artículos de ejemplo...')
        
        denominaciones_base = [
            'Implementación sistema ERP',
            'Actualización infraestructura de red',
            'Desarrollo plataforma web',
            'Modernización línea de producción',
            'Certificación ISO 9001',
            'Capacitación en nuevas tecnologías',
            'Mejora proceso de calidad',
            'Instalación equipos de seguridad',
            'Optimización base de datos',
            'Actualización sistema HVAC',
            'Desarrollo aplicación móvil',
            'Implementación metodología ágil',
            'Renovación equipos de cómputo',
            'Capacitación en normativas',
            'Mejora layout de planta',
        ]
        
        areas_choices = [choice[0] for choice in PerfilUsuario.AREAS_CHOICES]
        prioridades = ['BAJA', 'MEDIA', 'ALTA', 'CRITICA']
        monedas = ['MXN', 'USD', 'EUR']
        
        articulos_creados = 0
        
        for i in range(cantidad):
            año = random.choice([2023, 2024, 2025])
            codigo = f"ART-{año}-{str(i+1).zfill(4)}"
            
            # Verificar que no exista el código
            if Articulo.objects.filter(codigo_articulo=codigo).exists():
                codigo = f"ART-{año}-{str(i+1000).zfill(4)}"
            
            denominacion = f"{random.choice(denominaciones_base)} - Fase {random.randint(1, 3)}"
            
            # Fechas
            fecha_inicio = date(año, random.randint(1, 12), random.randint(1, 28))
            dias_proyecto = random.randint(30, 365)
            fecha_estimada_fin = fecha_inicio + timedelta(days=dias_proyecto)
            
            # Determinar si está completado
            esta_completado = random.choice([True, False, False])  # 33% completados
            fecha_real_fin = None
            progreso = random.randint(0, 100)
            
            if esta_completado:
                fecha_real_fin = fecha_estimada_fin + timedelta(days=random.randint(-10, 30))
                progreso = 100
            
            # Costos
            costo_base = random.uniform(10000, 500000)
            costo_estimado = Decimal(str(round(costo_base, 2)))
            costo_real = None
            if esta_completado or progreso > 50:
                variacion = random.uniform(0.8, 1.3)  # Variación del 80% al 130%
                costo_real = Decimal(str(round(costo_base * variacion, 2)))
            
            try:
                articulo = Articulo.objects.create(
                    codigo_articulo=codigo,
                    denominacion=denominacion,
                    descripcion=f"Descripción detallada del proyecto {denominacion}. "
                               f"Este proyecto abarca múltiples aspectos técnicos y operativos.",
                    fabrica=random.choice(fabricas),
                    categoria=random.choice(categorias),
                    estatus_pmo=random.choice(estados),
                    responsable=random.choice(usuarios),
                    area_responsable=random.choice(areas_choices),
                    año=año,
                    fecha_inicio=fecha_inicio,
                    fecha_estimada_fin=fecha_estimada_fin,
                    fecha_real_fin=fecha_real_fin,
                    costo_estimado=costo_estimado,
                    costo_real=costo_real,
                    moneda=random.choice(monedas),
                    codigo_interno=f"INT-{random.randint(1000, 9999)}",
                    codigo_externo=f"EXT-{random.randint(1000, 9999)}",
                    codigo_proveedor=f"PROV-{random.randint(100, 999)}",
                    progreso_porcentaje=progreso,
                    prioridad=random.choice(prioridades),
                    creado_por=random.choice(usuarios),
                )
                articulos_creados += 1
                
                if articulos_creados % 10 == 0:
                    self.stdout.write(f'  ✓ {articulos_creados} artículos creados...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creando artículo {codigo}: {str(e)}')
                )
        
        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('DATOS DE EJEMPLO CREADOS EXITOSAMENTE'))
        self.stdout.write('='*50)
        self.stdout.write(f'📊 Fábricas: {Fabrica.objects.count()}')
        self.stdout.write(f'🎯 Estados PMO: {EstatusPMO.objects.count()}')
        self.stdout.write(f'📋 Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'📦 Artículos: {articulos_creados} nuevos (Total: {Articulo.objects.count()})')
        self.stdout.write('\n🚀 ¡El sistema está listo para usar!')
        self.stdout.write('👉 Accede al admin en: http://localhost:8000/admin/')
        self.stdout.write('👉 Dashboard principal: http://localhost:8000/')
        self.stdout.write('👉 Inventario PMO: http://localhost:8000/inventario/')
        self.stdout.write('='*50) 