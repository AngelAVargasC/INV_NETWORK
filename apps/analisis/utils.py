"""
Utilidades para el procesamiento de análisis de inventario
Adaptación de la lógica original de Flet para Django
"""

import os
import pandas as pd
import numpy as np
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
import tempfile
import logging
from .diccionario import cols_inventario_agin, pipeline, oracle_cols, OUTPUT_COLUMNS_ORDER
from .models import ProcesamientoAnalisis, LogProcesamiento

logger = logging.getLogger(__name__)

class InventoryProcessor:
    """
    Clase que maneja toda la lógica de procesamiento de archivos de inventario.
    Combina datos de aging, pipeline y oracle para adicionar datos a la tabla de inventario.
    Adaptada para Django desde la aplicación Flet original.
    """
    
    def __init__(self, user=None, procesamiento_id=None):
        self.user = user
        self.procesamiento_id = procesamiento_id
        self.procesamiento_obj = None
        self.processing_logs = []
        
        # Rutas de archivos temporales
        self.agin_file_path = None
        self.pipeline_file_path = None
        self.oracle_file_path = None
        
        # Resultados
        self.merged_df = None
        self.unmatched_df = None
        
        if procesamiento_id:
            try:
                self.procesamiento_obj = ProcesamientoAnalisis.objects.get(id=procesamiento_id)
            except ProcesamientoAnalisis.DoesNotExist:
                pass
    
    def _log(self, message: str, level: str = "INFO"):
        """Registra un mensaje en los logs del procesamiento."""
        timestamp = timezone.now()
        log_entry = f"[{timestamp.strftime('%H:%M:%S')}] {level}: {message}"
        self.processing_logs.append(log_entry)
        
        # Log en Django logger
        logger.info(f"Procesamiento {self.procesamiento_id}: {message}")
        
        # Guardar en base de datos si hay un objeto de procesamiento
        if self.procesamiento_obj:
            LogProcesamiento.objects.create(
                procesamiento=self.procesamiento_obj,
                nivel=level,
                mensaje=message
            )
        
        print(log_entry)  # También imprimir para debugging
    
    def set_file_paths(self, agin_path: str, pipeline_path: str, oracle_path: str):
        """Establece las rutas de los archivos a procesar."""
        self.agin_file_path = agin_path
        self.pipeline_file_path = pipeline_path
        self.oracle_file_path = oracle_path
        
        self._log(f"Archivos configurados: AGING={os.path.basename(agin_path)}, "
                  f"PIPELINE={os.path.basename(pipeline_path)}, "
                  f"ORACLE={os.path.basename(oracle_path)}")
    
    def load_excel_files(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Carga y limpia los tres archivos de Excel.
        Returns: (agin_df, pipeline_df, oracle_df)
        """
        self._log("Iniciando carga de archivos Excel...")
        
        try:
            # Cargar archivo AGING
            self._log(f"Cargando archivo AGING: {os.path.basename(self.agin_file_path)}")
            agin_df = pd.read_excel(
                self.agin_file_path, 
                sheet_name="Detalle de aging", 
                usecols=cols_inventario_agin, 
                header=3
            )
            self._log(f"✓ AGING cargado: {len(agin_df)} filas, {len(agin_df.columns)} columnas")
            
            # Cargar archivo PIPELINE
            self._log(f"Cargando archivo PIPELINE: {os.path.basename(self.pipeline_file_path)}")
            pipeline_df = pd.read_excel(
                self.pipeline_file_path, 
                sheet_name="Pipeline 2025", 
                usecols=pipeline, 
                header=10
            )
            self._log(f"✓ PIPELINE cargado: {len(pipeline_df)} filas, {len(pipeline_df.columns)} columnas")
            
            # Cargar archivo ORACLE
            self._log(f"Cargando archivo ORACLE: {os.path.basename(self.oracle_file_path)}")
            oracle_df = pd.read_excel(
                self.oracle_file_path, 
                sheet_name="Hoja1", 
                usecols=oracle_cols, 
                header=0
            )
            self._log(f"✓ ORACLE cargado: {len(oracle_df)} filas, {len(oracle_df.columns)} columnas")
            
            # Limpiar nombres de columnas (eliminar espacios)
            self._log("Limpiando nombres de columnas...")
            agin_df.columns = agin_df.columns.str.strip()
            pipeline_df.columns = pipeline_df.columns.str.strip()
            oracle_df.columns = oracle_df.columns.str.strip()
            
            # Rellenar valores nulos según la nueva lógica
            pipeline_df['Program / Product'] = pipeline_df['Program / Product'].fillna('N/A')
            oracle_df['ID PMO'] = oracle_df['ID PMO'].fillna('N/A')
            oracle_df['Program Manager'] = oracle_df['Program Manager'].fillna('N/A')
            
            # Actualizar estatus PMO según las condiciones
            self._log("Aplicando reglas de negocio para Estatus PMO...")
            agin_df.loc[
                (agin_df['Existencia Actual'] == 0) & 
                (agin_df['Estatus PMO'] != 'Instalado'), 
                'Estatus PMO'
            ] = 'Instalado'
            
            # Reorganizar columnas según el orden especificado
            agin_df = agin_df[OUTPUT_COLUMNS_ORDER]
            
            self._log("✓ Nombres de columnas limpiados y datos preparados")
            
            # Actualizar estadísticas en el modelo
            if self.procesamiento_obj:
                self.procesamiento_obj.total_registros_aging = len(agin_df)
                self.procesamiento_obj.total_registros_pipeline = len(pipeline_df)
                self.procesamiento_obj.total_registros_oracle = len(oracle_df)
                self.procesamiento_obj.save()
            
            return agin_df, pipeline_df, oracle_df
            
        except Exception as e:
            error_msg = f"Error al cargar archivos Excel: {str(e)}"
            self._log(error_msg, "ERROR")
            raise Exception(error_msg)
    
    def merge_data(self, agin_df: pd.DataFrame, pipeline_df: pd.DataFrame, oracle_df: pd.DataFrame) -> pd.DataFrame:
        """
        Combina los datos usando la lógica de procesamiento.
        
        Proceso:
        1. Combina AGING con PIPELINE por 'Orden de Compra' <-> 'PO Actual'
        2. Actualiza campos en AGING directamente con datos de PIPELINE
        3. Para órdenes no encontradas en PIPELINE, busca en ORACLE
        4. Aplica reglas especiales para órdenes IT
        """
        
        self._log("Iniciando proceso de combinación de datos...")
        
        # PASO 1: Combinar AGING con PIPELINE
        self._log("PASO 1: Combinando AGING con PIPELINE...")
        combinar_agin_pipe = agin_df.merge(
            pipeline_df,   
            left_on='Orden de Compra',   
            right_on='PO Actual',   
            how='left',   
            suffixes=('', '_pipeline')  
        )
        
        # Actualizar AGING con datos de PIPELINE
        matches_pipeline = 0
        for _, row in combinar_agin_pipe.iterrows():
            if pd.notna(row['IDPMO']): 
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'ID de PMO'] = row['IDPMO']
                matches_pipeline += 1
            if pd.notna(row['Nombre de Proyecto_pipeline']):
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Nombre de Proyecto'] = row['Nombre de Proyecto_pipeline']    
            if row['Program / Product'] != 'N/A':
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Program Manager'] = row['Program / Product']
            if pd.notna(row['Macro CAT']):
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Tipo'] = row['Macro CAT']
        
        self._log(f"✓ AGING-PIPELINE: {matches_pipeline} órdenes actualizadas con datos de PIPELINE")
        
        # PASO 2: Procesar órdenes no encontradas en PIPELINE
        self._log("PASO 2: Procesando órdenes no encontradas en PIPELINE...")
        unmatched_df = agin_df[~agin_df['Orden de Compra'].isin(pipeline_df['PO Actual'])]
        unmatched_unique_df = unmatched_df[['Orden de Compra']].drop_duplicates()
        
        # Usar solo la primera ocurrencia de cada orden en ORACLE para evitar duplicados
        oracle_df_first = oracle_df.drop_duplicates(subset='Orden de compra', keep='first')
        unmatched_in_oracle_df = unmatched_unique_df.merge(  
            oracle_df_first,  
            left_on='Orden de Compra',  
            right_on='Orden de compra', 
            how='left',  
            suffixes=('', '_oracle')  
        )
        
        # Actualizar AGING con datos de ORACLE para órdenes no encontradas en PIPELINE
        matches_oracle = 0
        for _, row in unmatched_in_oracle_df.iterrows():
            if pd.notna(row['ID PMO']):  
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'ID de PMO'] = row['ID PMO'] 
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Program Manager'] = row['Program Manager']
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'AVP'] = row['AVP']
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Fabrica'] = row['FABRICA']
                agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Nombre de Proyecto'] = row['Descripción']
                matches_oracle += 1
                
                # Aplicar reglas especiales para órdenes IT
                if row['ID PMO'] == 'N/A':
                    agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Estatus PMO'] = 'IT'
                    agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Historial'] = '-'
                    agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Observaciones'] = '-'
                    agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Retrasos en salida'] = '-'
                    agin_df.loc[agin_df['Orden de Compra'] == row['Orden de Compra'], 'Tipo'] = 'IT'
        
        self._log(f"✓ AGING-ORACLE: {matches_oracle} órdenes actualizadas con datos de ORACLE")
        
        # Actualizar estadísticas en el modelo
        if self.procesamiento_obj:
            self.procesamiento_obj.registros_actualizados_pipeline = matches_pipeline
            self.procesamiento_obj.registros_actualizados_oracle = matches_oracle
            self.procesamiento_obj.save()
        
        return agin_df
    
    def generate_unmatched_data(self, agin_df: pd.DataFrame, pipeline_df: pd.DataFrame, oracle_df: pd.DataFrame) -> pd.DataFrame:
        """
        Genera DataFrame con órdenes de compra que no encontraron match en ningún sistema.
        """
        self._log("Generando datos no coincidentes...")
        final_unmatched_df = agin_df[
            ~agin_df['Orden de Compra'].isin(pipeline_df['PO Actual']) & 
            ~agin_df['Orden de Compra'].isin(oracle_df['Orden de compra'])
        ]
        final_unmatched_df = final_unmatched_df[['Orden de Compra']].drop_duplicates()
        
        self._log(f"✓ Órdenes sin coincidencias en Pipeline ni Oracle: {len(final_unmatched_df)}")
        
        # Actualizar estadísticas en el modelo
        if self.procesamiento_obj:
            self.procesamiento_obj.registros_no_coincidentes = len(final_unmatched_df)
            self.procesamiento_obj.save()
        
        return final_unmatched_df
    
    def save_results_to_media(self, merged_df: pd.DataFrame, unmatched_df: pd.DataFrame) -> tuple[str, str]:
        """
        Guarda los resultados en archivos en el directorio media de Django
        """
        self._log("Guardando resultados en archivos...")
        
        try:
            # Crear directorio para resultados con timestamp
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            results_dir = f"analisis_resultados/{timestamp}"
            
            # Crear el directorio en media
            media_path = os.path.join(settings.MEDIA_ROOT, results_dir)
            os.makedirs(media_path, exist_ok=True)
            
            # Nombres de archivos
            updated_filename = f"Updated_Agin_{timestamp}.xlsx"
            unmatched_filename = f"Final_Unmatched_Agin_{timestamp}.xlsx"
            
            # Rutas completas
            updated_file_path = os.path.join(media_path, updated_filename)
            unmatched_file_path = os.path.join(media_path, unmatched_filename)
            
            # Guardar archivos
            merged_df.to_excel(updated_file_path, index=False)
            unmatched_df.to_excel(unmatched_file_path, index=False)
            
            # Rutas relativas para guardar en el modelo
            updated_relative_path = os.path.join(results_dir, updated_filename)
            unmatched_relative_path = os.path.join(results_dir, unmatched_filename)
            
            self._log(f"✓ Archivo principal guardado: {updated_filename} ({len(merged_df)} filas)")
            self._log(f"✓ Archivo no coincidentes guardado: {unmatched_filename} ({len(unmatched_df)} filas)")
            
            # Actualizar modelo con rutas de archivos
            if self.procesamiento_obj:
                self.procesamiento_obj.archivo_resultado = updated_relative_path
                self.procesamiento_obj.archivo_no_coincidentes = unmatched_relative_path
                self.procesamiento_obj.save()
            
            return updated_relative_path, unmatched_relative_path
            
        except Exception as e:
            error_msg = f"Error al guardar resultados: {str(e)}"
            self._log(error_msg, "ERROR")
            raise Exception(error_msg)
    
    def process_files(self) -> dict:
        """
        Procesa todos los archivos y retorna los resultados
        """
        start_time = timezone.now()
        
        try:
            self._log("=== INICIANDO PROCESAMIENTO DE INVENTARIO ===")
            
            # Cargar archivos
            agin_df, pipeline_df, oracle_df = self.load_excel_files()
            
            # Procesar datos
            merged_df = self.merge_data(agin_df, pipeline_df, oracle_df)
            unmatched_df = self.generate_unmatched_data(agin_df, pipeline_df, oracle_df)
            
            # Guardar resultados
            updated_path, unmatched_path = self.save_results_to_media(merged_df, unmatched_df)
            
            # Calcular tiempo de procesamiento
            end_time = timezone.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Actualizar estado del procesamiento
            if self.procesamiento_obj:
                self.procesamiento_obj.estado = 'completado'
                self.procesamiento_obj.tiempo_procesamiento = processing_time
                self.procesamiento_obj.logs_procesamiento = '\n'.join(self.processing_logs)
                self.procesamiento_obj.save()
            
            self._log(f"=== PROCESAMIENTO COMPLETADO EN {processing_time:.2f} segundos ===")
            
            return {
                'success': True,
                'merged_df': merged_df,
                'unmatched_df': unmatched_df,
                'updated_file_path': updated_path,
                'unmatched_file_path': unmatched_path,
                'processing_time': processing_time,
                'logs': self.processing_logs
            }
            
        except Exception as e:
            # Manejar errores
            if self.procesamiento_obj:
                self.procesamiento_obj.estado = 'error'
                self.procesamiento_obj.logs_procesamiento = '\n'.join(self.processing_logs)
                self.procesamiento_obj.save()
            
            error_msg = f"Error durante el procesamiento: {str(e)}"
            self._log(error_msg, "ERROR")
            
            return {
                'success': False,
                'error': error_msg,
                'logs': self.processing_logs
            }

def save_uploaded_file_to_temp(uploaded_file) -> str:
    """
    Guarda un archivo subido de Django en un archivo temporal
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)
        return tmp_file.name 