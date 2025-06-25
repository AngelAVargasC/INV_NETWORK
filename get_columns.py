import pandas as pd

df = pd.read_excel('Updated_Agin.xlsx')
print('COLUMNAS EN TU ARCHIVO:')
for i, col in enumerate(df.columns, 1):
    print(f'{i:2d}. {col}')
    
print(f'\nTotal columnas: {len(df.columns)}')
print(f'Total filas: {len(df)}') 