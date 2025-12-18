import sqlite3
import pandas as pd

# Conectar a la base de datos
conn = sqlite3.connect('facturas.db')

# Leer todos los datos
df = pd.read_sql_query('SELECT * FROM facturas', conn)
conn.close()

# Exportar a CSV
df.to_csv('facturas_exportadas.csv', index=False, sep=';', encoding='utf-8-sig')
print(f'✓ Datos exportados a facturas_exportadas.csv ({len(df)} registros)')

# Mostrar resumen
print(f'\nResumen:')
print(f'Total registros: {len(df)}')
print(f'Total Importe: {df["Importe"].sum():,.2f} €')
