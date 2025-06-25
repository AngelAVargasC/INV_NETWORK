from django.core.management.base import BaseCommand
import pandas as pd
from apps.inventario.models import Articulo, Fabrica, EstatusPMO
from decimal import Decimal
import logging

class Command(BaseCommand):
    help = 'Importa TODOS los datos del Excel sin filtros ni duplicados'

    def add_arguments(self, parser):
        parser.add_argument('--limpiar', action='store_true', help='Limpiar datos existentes')
        parser.add_argument('--archivo', type=str, default='Updated_Agin.xlsx', help='Archivo a importar')

    def handle(self, *args, **options):
        if options['limpiar']:
            self.stdout.write("🧹 Limpiando datos existentes...")
            Articulo.objects.all().delete()
            self.stdout.write("✅ Datos limpiados")

        archivo = options['archivo']
        self.stdout.write(f"📊 Leyendo archivo: {archivo}")
        
        try:
            df = pd.read_excel(archivo)
            total_filas = len(df)
            self.stdout.write(f"📥 Importando {total_filas} registros...")

            creados = 0
            errores = 0

            for index, row in df.iterrows():
                try:
                    # Crear artículo con TODOS los datos - sin filtros
                    articulo = Articulo.objects.create(
                        año=self._safe_int(row.get('Año', 2024)),
                        articulo=self._safe_text(row.get('Articulo', '')),
                        descripcion=self._safe_text(row.get('Descripción', '')),
                        proveedor=self._safe_text(row.get('Proveedor', '')),
                        nombre_proyecto_recibo=self._safe_text(row.get('Nombre de proyecto recibo', '')),
                        orden_compra=self._safe_text(row.get('Orden de Compra', '')),
                        id_pmo=self._safe_text(row.get('ID de PMO', f'PMO-{index+1}')),
                        nombre_proyecto=self._safe_text(row.get('Nombre de Proyecto', '')),
                        program_manager=self._safe_text(row.get('Program Manager', '')),
                        estatus_pmo_texto=self._safe_text(row.get('Estatus PMO', '')),
                        fecha_implementacion=self._safe_text(row.get('Fecha de Implementación Si/No', '')),
                        historial=self._safe_text(row.get('Historial', '')),
                        observaciones=self._safe_text(row.get('Observaciones', '')),
                        retrasos_salida=self._safe_text(row.get('Retrasos en salida', '')),
                        avp=self._safe_text(row.get('AVP', '')),
                        tipo=self._safe_text(row.get('Tipo', '')),
                        fabrica_texto=self._safe_text(row.get('Fabrica', '')),
                        costo_unitario_distribucion=self._safe_decimal(row.get('COSTO UNITARIO DISTRIBUCION')),
                        cantidad_embarcada=self._safe_decimal(row.get('Cantidad Embarcada')),
                        costo_salida_mxn=self._safe_decimal(row.get('Costo Salida $MXN')),
                        existencia_actual=self._safe_decimal(row.get('Existencia Actual')),
                        costo_mxn_existencias=self._safe_decimal(row.get('Costo $MXN Existencias')),
                        costo_usd_existencias=self._safe_decimal(row.get('Costo $USD Existencias')),
                    )
                    creados += 1
                    
                    if creados % 1000 == 0:
                        self.stdout.write(f"📈 Procesados: {creados}")
                        
                except Exception as e:
                    errores += 1
                    if errores <= 5:  # Solo mostrar primeros 5 errores
                        self.stdout.write(f"❌ Error en fila {index+1}: {str(e)}")

            self.stdout.write("\n✅ IMPORTACIÓN COMPLETADA")
            self.stdout.write(f"📊 Total registros: {total_filas}")
            self.stdout.write(f"✅ Creados: {creados}")
            self.stdout.write(f"❌ Errores: {errores}")
            
        except Exception as e:
            self.stdout.write(f"💥 Error al leer archivo: {str(e)}")

    def _safe_text(self, value):
        """Convierte valor a texto de forma segura"""
        if pd.isna(value) or value is None:
            return ''
        return str(value).strip()[:300]  # Limitar longitud

    def _safe_int(self, value):
        """Convierte valor a entero de forma segura"""
        try:
            if pd.isna(value):
                return 2024
            return int(float(value))
        except:
            return 2024

    def _safe_decimal(self, value):
        """Convierte valor a decimal de forma segura"""
        try:
            if pd.isna(value) or value is None or value == '':
                return None
            return Decimal(str(float(value)))
        except:
            return None 