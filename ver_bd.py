import sqlite3
import pandas as pd

conn = sqlite3.connect('facturas.db')
df = pd.read_sql_query('SELECT * FROM facturas', conn)
conn.close()

print(f'Total registros: {len(df)}')
print(f'Total Base Imponible: {df["Base"].sum():,.2f} €')
print(f'Total IVA: {df["Cuota"].sum():,.2f} €')
print(f'Total Importes: {df["Importe"].sum():,.2f} €')
print(f'\nPrimeras 10 facturas:')
print(df.head(10)[['Fecha', 'Codigo', 'Cliente', 'Importe']].to_string())
