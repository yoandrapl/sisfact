import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

df = None

# Cargar archivo Excel
def cargar_excel():
    global df
    archivo = filedialog.askopenfilename(
        filetypes=[("Archivos CSV", "*.csv")]
    )
    if archivo:
        try:
            columnas = ["Fecha", "Código", "Identificación", "Cliente", "Modelo", "Tipo", "Base imp.","Cuota", "Importe"]
            df = pd.read_csv(archivo,sep=";", usecols=columnas)
            
            # Convertir campos numéricos
            for campo in ["Base imp.", "Cuota", "Importe"]:
                df[campo] = (
                    df[campo]
                    .astype(str)
                    .str.replace(",", ".", regex=False)
                    .str.replace("$", "", regex=False)
                )
                df[campo] = pd.to_numeric(df[campo], errors="coerce")
            
            mostrar_datos(df)
            actualizar_total(df)

        except Exception as e:
            messagebox.showerror("Error", str(e))

# Mostrar datos en la tabla
def mostrar_datos(data):
    tabla.delete(*tabla.get_children())
    for _, fila in data.iterrows():
        tabla.insert("", "end", values=list(fila))

# Aplicar filtros
def filtrar():
    if df is None:
        messagebox.showwarning("Aviso", "Cargue un archivo Excel primero")
        return

    cliente = entry_cliente.get()
    ventas = entry_ventas.get()
    tipo = entry_tipo.get()
    matricula = entry_matricula.get()

    filtrado = df.copy()

    if cliente:
        filtrado = filtrado[filtrado["Cliente"].str.contains(cliente, case=False)]

    if ventas:
        filtrado = filtrado[filtrado["Importe"] >= float(ventas)]
        
    if tipo:
        filtrado = filtrado[filtrado["Tipo"].str.contains(tipo, case=False)]
        
    if matricula:
        filtrado = filtrado[filtrado["Identificación"].str.contains(matricula, case=False, na=False)]
        
        

    mostrar_datos(filtrado)
    actualizar_total(filtrado)
    
# Actualizar Total
def actualizar_total(data):
    
    total = data["Importe"].sum()
    lbl_total.config(text=f"Total facturas: {total:,.2f} €")
    
# Guardar en base de datos
def guardar_en_bd(data):
    conn = sqlite3.connect("facturas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            Fecha TEXT,
            Codigo TEXT,
            Identificacion TEXT,
            Cliente TEXT,
            Modelo TEXT,
            Tipo TEXT,
            Base REAL,      
            Cuota REAL,
            Importe REAL
        )
    """)
    for _, fila in data.iterrows():
        cursor.execute("""
            INSERT INTO facturas
            (Fecha, Codigo, Identificacion, Cliente, Modelo, Tipo, Base, Cuota, Importe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fila["Fecha"],
            fila["Código"],
            fila["Identificación"],
            fila["Cliente"],
            fila["Modelo"],
            fila["Tipo"],
            fila["Base imp."],
            fila["Cuota"],
            fila["Importe"]
        ))
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Datos guardados en la base de datos")

# Cargar datos desde la base de datos
def cargar_desde_bd():
    global df
    try:
        conn = sqlite3.connect("facturas.db")
        df = pd.read_sql_query("SELECT * FROM facturas", conn)
        conn.close()
        
        # Renombrar columnas para que coincidan con el formato esperado
        df.columns = ["Fecha", "Código", "Identificación", "Cliente", "Modelo", "Tipo", "Base imp.", "Cuota", "Importe"]
        
        mostrar_datos(df)
        actualizar_total(df)
        messagebox.showinfo("Éxito", f"Se cargaron {len(df)} registros desde la base de datos")
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar desde BD: {str(e)}")

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Sistema de Importación y Filtros")
ventana.geometry("700x400")

lbl_total = tk.Label(ventana, text="Total facturas: 0 €", font=("Arial", 12, "bold"))
lbl_total.pack(pady=5)


btn_cargar = tk.Button(ventana, text="Cargar CSV", command=cargar_excel)
btn_cargar.pack(pady=5)

btn_guardar = tk.Button(
    ventana,
    text="Guardar en Base de Datos",
    command=lambda: guardar_en_bd(df) if df is not None else messagebox.showwarning("Aviso", "Primero cargue un archivo CSV")
)
btn_guardar.pack(pady=5)

btn_cargar_bd = tk.Button(ventana, text="Cargar desde Base de Datos", command=cargar_desde_bd)
btn_cargar_bd.pack(pady=5)

frame_filtros = tk.Frame(ventana)
frame_filtros.pack()

tk.Label(frame_filtros, text="Cliente:").grid(row=0, column=0)
entry_cliente = tk.Entry(frame_filtros)
entry_cliente.grid(row=0, column=1)

tk.Label(frame_filtros, text="Ventas mínimas:").grid(row=0, column=2)
entry_ventas = tk.Entry(frame_filtros)
entry_ventas.grid(row=0, column=3)

tk.Label(frame_filtros, text="Tipo Factura:").grid(row=0, column=4)
entry_tipo = tk.Entry(frame_filtros)
entry_tipo.grid(row=0, column=5)

tk.Label(frame_filtros, text="Matrícula:").grid(row=0, column=6)
entry_matricula = tk.Entry(frame_filtros)
entry_matricula.grid(row=0, column=7)

btn_filtrar = tk.Button(ventana, text="Filtrar", command=filtrar)
btn_filtrar.pack(pady=5)

# Tabla
tabla = ttk.Treeview(ventana, columns=("FECHA", "FACTURA", "MATRICULA", "CLIENTE", "MODELO", "TIPO", "BASE IMP.","IVA", "IMPORTE" ), show="headings")
for col in tabla["columns"]:
    tabla.heading(col, text=col)

tabla.pack(expand=True, fill="both")

ventana.mainloop()
