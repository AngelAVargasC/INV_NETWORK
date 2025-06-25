from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.inventario.models import Fabrica, EstatusPMO, Categoria, Articulo
from apps.inventario.utils import ImportadorDatos
import tempfile
import pandas as pd
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Crear datos de ejemplo con la estructura real del sistema PMO'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Limpiar datos existentes antes de crear nuevos'
        )

    def handle(self, *args, **options):
        if options['limpiar']:
            self.stdout.write(self.style.WARNING('Limpiando datos existentes...'))
            Articulo.objects.all().delete()
            Fabrica.objects.all().delete()
            EstatusPMO.objects.all().delete()
            Categoria.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Datos limpiados'))

        # Crear datos de ejemplo con estructura real
        self.crear_datos_reales()
        self.stdout.write(self.style.SUCCESS('✓ Datos de ejemplo creados exitosamente'))

    def crear_datos_reales(self):
        """Crea datos de ejemplo usando la estructura real compartida por el usuario"""
        
        # Datos de ejemplo basados en la estructura real
        datos_ejemplo = [
            {
                'Orden de Compra': '1202402350',
                'ID de PMO': '2024-CRIC-T&F-DATACOMMSEC-095',
                'Nombre de Proyecto': '2024-CRIC-T&F-DATACOMMSEC-095-Modernización de Red Core NOKIA fase 5',
                'Program Manager': 'Pablo Gómez Ramírez',
                'Estatus PMO': 'Instalado',
                'Fecha de Implementación Si/No': 'NO',
                'Historial': 'Pendiente por confirmar',
                'Observaciones': 'Proyecto completado exitosamente',
                'Retrasos en salida': 'Sin retrasos',
                'AVP': 'EXEC AND TRANS',
                'Tipo': 'Transporte (IP y Acceso)',
                'Fabrica': 'Transporte y FOPs',
                'COSTO UNITARIO DISTRIBUCION': '3092.79',
                'Cantidad Embarcada': '1',
                'Costo Salida $MXN': '62010.44',
                'Existencia Actual': '0',
                'Costo $MXN Existencias': '0',
                'Costo $USD Existencias': '0'
            },
            {
                'Orden de Compra': '1202402350',
                'ID de PMO': '2024-CRIC-T&F-DATACOMMSEC-096',
                'Nombre de Proyecto': '2024-CRIC-T&F-DATACOMMSEC-096-Actualización de Equipos de Red',
                'Program Manager': 'Pablo Gómez Ramírez',
                'Estatus PMO': 'Pendiente por confirmar',
                'Fecha de Implementación Si/No': 'NO',
                'Historial': 'En revisión técnica',
                'Observaciones': 'Pendiente validación de equipos',
                'Retrasos en salida': 'Retraso de 2 semanas',
                'AVP': 'EXEC AND TRANS',
                'Tipo': 'Transporte (IP y Acceso)',
                'Fabrica': 'Transporte y FOPs',
                'COSTO UNITARIO DISTRIBUCION': '7938.14',
                'Cantidad Embarcada': '0',
                'Costo Salida $MXN': '0',
                'Existencia Actual': '1',
                'Costo $MXN Existencias': '159159.71',
                'Costo $USD Existencias': '7938.14'
            },
            {
                'Orden de Compra': '1202403697',
                'ID de PMO': '2024-CRIC-RAN-IBS-073',
                'Nombre de Proyecto': '2024-CRIC-RAN-IBS-073-IBS-R&R Foro Sol',
                'Program Manager': 'Cristiani Abundez Bonfil',
                'Estatus PMO': 'Instalado',
                'Fecha de Implementación Si/No': 'SI',
                'Historial': 'Implementación exitosa',
                'Observaciones': 'Proyecto completado en tiempo',
                'Retrasos en salida': 'Sin retrasos',
                'AVP': 'EXEC AND TRANS',
                'Tipo': 'IBS',
                'Fabrica': 'RAN',
                'COSTO UNITARIO DISTRIBUCION': '26064.04',
                'Cantidad Embarcada': '1',
                'Costo Salida $MXN': '26064.04',
                'Existencia Actual': '0',
                'Costo $MXN Existencias': '0',
                'Costo $USD Existencias': '0'
            },
            {
                'Orden de Compra': '1202403698',
                'ID de PMO': '2024-CRIC-CORE-NET-074',
                'Nombre de Proyecto': '2024-CRIC-CORE-NET-074-Expansión de Capacidad Core Network',
                'Program Manager': 'Ana María Fernández',
                'Estatus PMO': 'En Proceso',
                'Fecha de Implementación Si/No': 'NO',
                'Historial': 'Fase de implementación',
                'Observaciones': 'Avance según cronograma',
                'Retrasos en salida': 'Sin retrasos',
                'AVP': 'NETWORK OPS',
                'Tipo': 'Core Network',
                'Fabrica': 'Core y Agregación',
                'COSTO UNITARIO DISTRIBUCION': '45000.00',
                'Cantidad Embarcada': '0',
                'Costo Salida $MXN': '0',
                'Existencia Actual': '2',
                'Costo $MXN Existencias': '90000.00',
                'Costo $USD Existencias': '4500.00'
            },
            {
                'Orden de Compra': '1202403699',
                'ID de PMO': '2024-CRIC-SECURITY-075',
                'Nombre de Proyecto': '2024-CRIC-SECURITY-075-Actualización de Sistemas de Seguridad',
                'Program Manager': 'Roberto Silva Mendoza',
                'Estatus PMO': 'Aprobado',
                'Fecha de Implementación Si/No': 'NO',
                'Historial': 'Proyecto aprobado por comité',
                'Observaciones': 'Esperando liberación de recursos',
                'Retrasos en salida': 'Sin retrasos',
                'AVP': 'SECURITY OPS',
                'Tipo': 'Ciberseguridad',
                'Fabrica': 'Seguridad y Monitoreo',
                'COSTO UNITARIO DISTRIBUCION': '12500.75',
                'Cantidad Embarcada': '0',
                'Costo Salida $MXN': '0',
                'Existencia Actual': '5',
                'Costo $MXN Existencias': '62503.75',
                'Costo $USD Existencias': '3125.19'
            },
            {
                'Orden de Compra': '1202403700',
                'ID de PMO': '2024-CRIC-RAN-SITE-076',
                'Nombre de Proyecto': '2024-CRIC-RAN-SITE-076-Modernización de Sitios RAN',
                'Program Manager': 'María Elena Castro',
                'Estatus PMO': 'Planificación',
                'Fecha de Implementación Si/No': 'NO',
                'Historial': 'En fase de planeación',
                'Observaciones': 'Definiendo alcance y recursos',
                'Retrasos en salida': 'Sin retrasos',
                'AVP': 'RAN OPS',
                'Tipo': 'RAN Modernization',
                'Fabrica': 'RAN',
                'COSTO UNITARIO DISTRIBUCION': '8750.25',
                'Cantidad Embarcada': '0',
                'Costo Salida $MXN': '0',
                'Existencia Actual': '10',
                'Costo $MXN Existencias': '87502.50',
                'Costo $USD Existencias': '4375.13'
            }
        ]

        # Crear archivo temporal para importación
        df = pd.DataFrame(datos_ejemplo)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp_file:
            df.to_csv(tmp_file.name, index=False)
            tmp_file_path = tmp_file.name

        try:
            # Obtener o crear usuario administrador
            usuario, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@pmo.com',
                    'first_name': 'Administrador',
                    'last_name': 'PMO',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                usuario.set_password('admin123')
                usuario.save()
                self.stdout.write(f'✓ Usuario administrador creado: admin/admin123')

            # Usar el importador para procesar los datos
            importador = ImportadorDatos(tmp_file_path, usuario)
            resultado = importador.procesar_archivo()
            
            self.stdout.write(f'✓ Importación completada:')
            self.stdout.write(f'  - Artículos creados: {resultado["articulos_creados"]}')
            self.stdout.write(f'  - Artículos actualizados: {resultado["articulos_actualizados"]}')
            self.stdout.write(f'  - Errores: {resultado["errores"]}')
            
            # Mostrar estadísticas de las entidades creadas
            self.stdout.write(f'\n✓ Entidades creadas:')
            self.stdout.write(f'  - Fábricas: {Fabrica.objects.count()}')
            self.stdout.write(f'  - Categorías: {Categoria.objects.count()}')
            self.stdout.write(f'  - Estatus PMO: {EstatusPMO.objects.count()}')
            self.stdout.write(f'  - Artículos: {Articulo.objects.count()}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error durante la importación: {str(e)}')
            )
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

        self.stdout.write(
            self.style.SUCCESS(
                '\n✓ Datos de ejemplo creados exitosamente con estructura real del PMO'
            )
        ) 