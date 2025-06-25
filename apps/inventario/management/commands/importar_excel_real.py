from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.inventario.models import Fabrica, EstatusPMO, Categoria, Articulo
from apps.inventario.utils import ImportadorDatos
import os

class Command(BaseCommand):
    help = 'Importar datos reales desde el archivo Updated_Agin.xlsx'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            default='Updated_Agin.xlsx',
            help='Nombre del archivo Excel a importar'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Limpiar datos existentes antes de importar'
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=100,
            help='Número máximo de registros a importar (default: 100)'
        )

    def handle(self, *args, **options):
        archivo = options['archivo']
        limite = options['limite']
        
        # Verificar que el archivo existe
        if not os.path.exists(archivo):
            self.stdout.write(
                self.style.ERROR(f'El archivo {archivo} no existe en el directorio actual')
            )
            return

        if options['limpiar']:
            self.stdout.write(self.style.WARNING('Limpiando datos existentes...'))
            Articulo.objects.all().delete()
            Fabrica.objects.all().delete()
            EstatusPMO.objects.all().delete()
            Categoria.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Datos limpiados'))

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

        try:
            # Crear importador con límite de registros
            importador = ImportadorDatos(archivo, usuario)
            
            # Modificar temporalmente el procesamiento para limitar registros
            import pandas as pd
            df_original = pd.read_excel(archivo)
            
            self.stdout.write(f'📊 Archivo encontrado: {len(df_original)} registros totales')
            self.stdout.write(f'📥 Importando primeros {limite} registros...')
            
            # Tomar solo los primeros N registros
            df_limitado = df_original.head(limite)
            
            # Guardar temporalmente
            archivo_temp = f'temp_{archivo}'
            df_limitado.to_excel(archivo_temp, index=False)
            
            # Procesar archivo limitado
            importador_temp = ImportadorDatos(archivo_temp, usuario)
            resultado = importador_temp.procesar_archivo()
            
            self.stdout.write(f'\n✅ IMPORTACIÓN COMPLETADA')
            self.stdout.write(f'  📈 Artículos creados: {resultado["articulos_creados"]}')
            self.stdout.write(f'  🔄 Artículos actualizados: {resultado["articulos_actualizados"]}')
            self.stdout.write(f'  ❌ Errores: {resultado["errores"]}')
            
            if resultado["errores"] > 0:
                self.stdout.write(f'  ⚠️  Detalles de errores en logs')
            
            # Mostrar estadísticas finales
            self.stdout.write(f'\n📊 ESTADÍSTICAS FINALES:')
            self.stdout.write(f'  🏭 Fábricas: {Fabrica.objects.count()}')
            self.stdout.write(f'  📋 Categorías: {Categoria.objects.count()}')
            self.stdout.write(f'  🚦 Estatus PMO: {EstatusPMO.objects.count()}')
            self.stdout.write(f'  📦 Artículos: {Articulo.objects.count()}')
            
            # Mostrar distribución por estatus
            self.stdout.write(f'\n📈 DISTRIBUCIÓN POR ESTATUS:')
            for estatus in EstatusPMO.objects.all():
                count = Articulo.objects.filter(estatus_pmo=estatus).count()
                self.stdout.write(f'  {estatus.descripcion}: {count} proyectos')
            
            # Mostrar distribución por fábrica
            self.stdout.write(f'\n🏭 DISTRIBUCIÓN POR FÁBRICA:')
            for fabrica in Fabrica.objects.all():
                count = Articulo.objects.filter(fabrica=fabrica).count()
                self.stdout.write(f'  {fabrica.nombre}: {count} proyectos')
            
            # Limpiar archivo temporal
            if os.path.exists(archivo_temp):
                os.remove(archivo_temp)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la importación: {str(e)}')
            )
            # Limpiar archivo temporal en caso de error
            archivo_temp = f'temp_{archivo}'
            if os.path.exists(archivo_temp):
                os.remove(archivo_temp)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Importación completada desde {archivo}'
            )
        ) 