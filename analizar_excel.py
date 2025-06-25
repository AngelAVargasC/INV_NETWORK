import pandas as pd
import os

def analizar_excel():
    """Analizar estructura del archivo Excel"""
    archivo_path = "Updated_Agin.xlsx"
    
    if not os.path.exists(archivo_path):
        print(f"❌ Archivo {archivo_path} no encontrado")
        return
    
    try:
        # Leer el archivo Excel
        print(f"📊 Analizando archivo: {archivo_path}")
        df = pd.read_excel(archivo_path)
        
        print(f"\n📈 Dimensiones del archivo:")
        print(f"   - Filas: {len(df)}")
        print(f"   - Columnas: {len(df.columns)}")
        
        print(f"\n📋 Lista de columnas:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n🔍 Primeras 3 filas de datos:")
        print(df.head(3).to_string())
        
        print(f"\n📊 Información de tipos de datos:")
        print(df.dtypes)
        
        print(f"\n🔍 Valores únicos en columnas clave:")
        if 'Estatus PMO' in df.columns:
            print(f"   Estatus PMO: {df['Estatus PMO'].unique()}")
        if 'Fabrica' in df.columns:
            print(f"   Fábrica: {df['Fabrica'].unique()}")
        if 'Año' in df.columns:
            print(f"   Años: {df['Año'].unique()}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error al analizar archivo: {str(e)}")
        return None

if __name__ == "__main__":
    analizar_excel() 