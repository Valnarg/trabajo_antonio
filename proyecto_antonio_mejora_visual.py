import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  
import sqlite3
import os

# Obtener la ruta del directorio actual del script
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'inventario.db')

# Conexión a la base de datos SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,  
    cantidad INTEGER NOT NULL,
    umbral_minimo INTEGER NOT NULL
);
''')
conn.commit()

# Función para mostrar una alerta si el stock es bajo
def verificar_stock_bajo():
    cursor.execute("SELECT nombre, cantidad, umbral_minimo FROM productos WHERE cantidad < umbral_minimo")
    productos_bajos = cursor.fetchall()
    
    if productos_bajos:
        mensaje = "⚠️ Productos con stock bajo:\n\n"
        for nombre, cantidad, umbral in productos_bajos:
            mensaje += f"🔴 {nombre} - Cantidad: {cantidad}, Umbral: {umbral}\n"
        messagebox.showwarning("¡Atención! Stock bajo", mensaje)

# Función para añadir un producto
def añadir_producto(categoria, entry_nombre, entry_cantidad, entry_umbral):
    nombre = entry_nombre.get().strip().lower()
    
    if not entry_cantidad.get().isdigit() or not entry_umbral.get().isdigit():
        messagebox.showwarning("Advertencia", "Ingrese números válidos en Cantidad y Umbral.")
        return
    
    cantidad = int(entry_cantidad.get())
    umbral_minimo = int(entry_umbral.get())

    cursor.execute('SELECT * FROM productos WHERE LOWER(nombre) = ? AND categoria = ?', (nombre, categoria))
    if cursor.fetchone():
        messagebox.showwarning("Advertencia", f"El producto '{nombre.capitalize()}' ya existe.")
    else:
        cursor.execute('INSERT INTO productos (nombre, categoria, cantidad, umbral_minimo) VALUES (?, ?, ?, ?)', 
                       (nombre.capitalize(), categoria, cantidad, umbral_minimo))
        conn.commit()
        verificar_stock_bajo()
        messagebox.showinfo("Éxito", f"Producto '{nombre.capitalize()}' añadido correctamente!")

# Función para mostrar productos y marcar en rojo los de stock bajo
def mostrar_productos(categoria, listbox):
    listbox.delete(0, tk.END)  
    cursor.execute('SELECT nombre, cantidad, umbral_minimo FROM productos WHERE categoria = ?', (categoria,))
    productos = cursor.fetchall()

    if productos:
        for nombre, cantidad, umbral in productos:
            texto = f"{nombre} - Cantidad: {cantidad}, Umbral: {umbral}"
            listbox.insert(tk.END, texto)
            if cantidad < umbral:
                listbox.itemconfig(tk.END, {'fg': 'red'})  # Marcar en rojo si el stock es bajo
    else:
        listbox.insert(tk.END, "No hay productos.")

# Función para eliminar producto
def eliminar_producto(categoria, listbox):
    seleccion = listbox.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar.")
        return
    
    item = listbox.get(seleccion[0]).split(" -")[0]  
    cursor.execute("DELETE FROM productos WHERE nombre = ? AND categoria = ?", (item, categoria))
    conn.commit()
    
    listbox.delete(seleccion[0])
    messagebox.showinfo("Éxito", f"Producto '{item}' eliminado correctamente.")

# Función para modificar cantidad y umbral
def modificar_producto(categoria, listbox, entry_cantidad, entry_umbral):
    seleccion = listbox.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un producto para modificar.")
        return
    
    if not entry_cantidad.get().isdigit() or not entry_umbral.get().isdigit():
        messagebox.showwarning("Advertencia", "Ingrese números válidos.")
        return

    item = listbox.get(seleccion[0]).split(" -")[0]  
    nueva_cantidad = int(entry_cantidad.get())
    nuevo_umbral = int(entry_umbral.get())

    cursor.execute("UPDATE productos SET cantidad = ?, umbral_minimo = ? WHERE nombre = ? AND categoria = ?",
                   (nueva_cantidad, nuevo_umbral, item, categoria))
    conn.commit()
    
    mostrar_productos(categoria, listbox)
    verificar_stock_bajo()
    messagebox.showinfo("Éxito", f"Producto '{item}' actualizado correctamente.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Inventario")
ventana.geometry("600x600")
ventana.configure(bg="#f2f2f2")

# Aplicar un tema de estilo más moderno
style = ttk.Style()
style.theme_use("clam")

# Crear el Notebook (Pestañas)
notebook = ttk.Notebook(ventana)
notebook.pack(pady=10, padx=10, expand=True)

# Crear las pestañas
categorias = ["Bebidas", "Comidas", "Varios"]
pestañas = {}

for categoria in categorias:
    pestaña = ttk.Frame(notebook)
    notebook.add(pestaña, text=categoria)
    pestañas[categoria] = pestaña

    ttk.Label(pestaña, text="Nombre:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nombre = ttk.Entry(pestaña, font=("Arial", 12), width=20)
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(pestaña, text="Cantidad:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_cantidad = ttk.Entry(pestaña, font=("Arial", 12), width=10)
    entry_cantidad.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(pestaña, text="Umbral Mínimo:", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_umbral = ttk.Entry(pestaña, font=("Arial", 12), width=10)
    entry_umbral.grid(row=2, column=1, padx=5, pady=5)

    # Botón para añadir productos
    tk.Button(pestaña, text=f"Añadir {categoria}",
              command=lambda c=categoria, en=entry_nombre, ec=entry_cantidad, eu=entry_umbral:
              añadir_producto(c, en, ec, eu),
              font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5).grid(row=3, column=0, columnspan=2, pady=5)

    # Listbox para mostrar productos
    listbox = tk.Listbox(pestaña, font=("Arial", 12), width=45, height=6)
    listbox.grid(row=4, column=0, columnspan=2, pady=5)

    # Botón para mostrar productos
    tk.Button(pestaña, text=f"Mostrar {categoria}",
              command=lambda c=categoria, lb=listbox: mostrar_productos(c, lb),
              font=("Arial", 12, "bold"), bg="#008CBA", fg="white", padx=10, pady=5).grid(row=5, column=0, columnspan=2, pady=5)

    # Botones de eliminar y modificar
    tk.Button(pestaña, text="Eliminar", command=lambda c=categoria, lb=listbox: eliminar_producto(c, lb),
              font=("Arial", 12, "bold"), bg="#FF5733", fg="white", padx=10, pady=5).grid(row=6, column=0, pady=5)

    tk.Button(pestaña, text="Modificar", command=lambda c=categoria, lb=listbox, ec=entry_cantidad, eu=entry_umbral:
              modificar_producto(c, lb, ec, eu),
              font=("Arial", 12, "bold"), bg="#FFC300", fg="black", padx=10, pady=5).grid(row=6, column=1, pady=5)

# Ejecutar la aplicación
ventana.mainloop()
