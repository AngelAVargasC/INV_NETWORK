import pandas as pd

# Leer el archivo
df = pd.read_excel('Updated_Agin.xlsx')

print("=== ANÁLISIS DE DUPLICADOS ===")
print(f"Total filas: {len(df)}")
print(f"ID de PMO únicos: {df['ID de PMO'].nunique()}")
print(f"ID de PMO nulos: {df['ID de PMO'].isnull().sum()}")
print(f"Artículos únicos: {df['Articulo'].nunique()}")

print("\n=== PRIMEROS 10 ID DE PMO ===")
ids_unicos = df['ID de PMO'].dropna().unique()[:10]
for i, id_pmo in enumerate(ids_unicos):
    count = len(df[df['ID de PMO'] == id_pmo])
    print(f"{i+1}. {id_pmo} -> {count} repeticiones")

print("\n=== ANÁLISIS DE NULOS ===")
print(f"Filas con ID de PMO nulo: {df['ID de PMO'].isnull().sum()}")
print(f"Filas con Articulo nulo: {df['Articulo'].isnull().sum()}")

print("\n=== MUESTRA DE DATOS CON ID PMO NULO ===")
nulos = df[df['ID de PMO'].isnull()].head(3)
for col in ['Articulo', 'Nombre de Proyecto', 'Estatus PMO']:
    print(f"{col}: {nulos[col].tolist()}")

print("\n=== RESUMEN DEL PROBLEMA ===")
print(f"Solo hay {df['ID de PMO'].nunique()} ID de PMO únicos de {len(df)} filas totales")
print("Esto explica por qué solo se crean ~77 registros únicos") 