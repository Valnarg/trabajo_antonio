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

# Crear las tablas de productos si no existen
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

# Función para añadir un producto
def añadir_producto(categoria, entry_nombre, entry_cantidad, entry_umbral):
    nombre = entry_nombre.get().lower()  # Convertir el nombre a minúsculas
    
    # Validar que el campo de cantidad no esté vacío
    cantidad_texto = entry_cantidad.get()
    if not cantidad_texto.isdigit():  # Verificar si es un número válido
        messagebox.showwarning("Advertencia", "Por favor, ingresa una cantidad válida.")
        return  # Salir de la función si la cantidad no es válida
    
    cantidad = int(cantidad_texto)
    
    # Validar que el campo de umbral no esté vacío
    umbral_texto = entry_umbral.get()
    if not umbral_texto.isdigit():
        messagebox.showwarning("Advertencia", "Por favor, ingresa un umbral mínimo válido.")
        return  # Salir de la función si el umbral no es válido
    
    umbral_minimo = int(umbral_texto)

    # Verificar si el producto ya existe en la base de datos, ignorando mayúsculas/minúsculas
    cursor.execute('SELECT * FROM productos WHERE LOWER(nombre) = ? AND categoria = ?', (nombre, categoria))
    producto_existente = cursor.fetchone()

    if producto_existente:
        messagebox.showwarning("Advertencia", f"El producto '{nombre.capitalize()}' ya existe en la categoría '{categoria}'.")
    else:
        cursor.execute('''
        INSERT INTO productos (nombre, categoria, cantidad, umbral_minimo)
        VALUES (?, ?, ?, ?)
        ''', (nombre.capitalize(), categoria, cantidad, umbral_minimo))
        conn.commit()
        messagebox.showinfo("Éxito", f"Producto {nombre.capitalize()} añadido correctamente!")

# Función para mostrar los productos de una categoría
def mostrar_productos(categoria, listbox):
    # Limpiar la lista antes de mostrar nuevos productos
    listbox.delete(0, tk.END)  
    cursor.execute('SELECT * FROM productos WHERE categoria = ?', (categoria,))
    productos = cursor.fetchall()
    if productos:
        for producto in productos:
            listbox.insert(tk.END, f"{producto[1]} - Cantidad: {producto[3]}")
    else:
        listbox.insert(tk.END, f"No hay productos en la categoría '{categoria}'.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Inventario")

# Crear el widget Notebook para las pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(pady=10, padx=10, expand=True)

# Crear las pestañas
pestaña_bebidas = ttk.Frame(notebook)
pestaña_comidas = ttk.Frame(notebook)
pestaña_varios = ttk.Frame(notebook)

# Añadir las pestañas al Notebook
notebook.add(pestaña_bebidas, text="Bebidas")
notebook.add(pestaña_comidas, text="Comidas")
notebook.add(pestaña_varios, text="Varios")

# Crear los widgets para las pestañas (Bebidas)
label_nombre_bebidas = tk.Label(pestaña_bebidas, text="Nombre del Producto:")
label_nombre_bebidas.grid(row=0, column=0)

entry_nombre_bebidas = tk.Entry(pestaña_bebidas)
entry_nombre_bebidas.grid(row=0, column=1)

label_cantidad_bebidas = tk.Label(pestaña_bebidas, text="Cantidad:")
label_cantidad_bebidas.grid(row=1, column=0)

entry_cantidad_bebidas = tk.Entry(pestaña_bebidas)
entry_cantidad_bebidas.grid(row=1, column=1)

label_umbral_bebidas = tk.Label(pestaña_bebidas, text="Umbral Mínimo:")
label_umbral_bebidas.grid(row=2, column=0)

entry_umbral_bebidas = tk.Entry(pestaña_bebidas)
entry_umbral_bebidas.grid(row=2, column=1)

# Botón para añadir productos en bebidas
boton_añadir_bebidas = tk.Button(pestaña_bebidas, text="Añadir Bebida", command=lambda: añadir_producto("Bebidas", entry_nombre_bebidas, entry_cantidad_bebidas, entry_umbral_bebidas))
boton_añadir_bebidas.grid(row=3, column=0, columnspan=2)

# Listbox para mostrar los productos en bebidas
listbox_bebidas = tk.Listbox(pestaña_bebidas, width=50)
listbox_bebidas.grid(row=4, column=0, columnspan=2)

# Botón para mostrar productos en bebidas
boton_mostrar_bebidas = tk.Button(pestaña_bebidas, text="Mostrar Bebidas", command=lambda: mostrar_productos("Bebidas", listbox_bebidas))
boton_mostrar_bebidas.grid(row=5, column=0, columnspan=2)

# Funciones similares para las otras pestañas (Comidas y Varios)
# Pestaña Comidas
label_nombre_comidas = tk.Label(pestaña_comidas, text="Nombre del Producto:")
label_nombre_comidas.grid(row=0, column=0)

entry_nombre_comidas = tk.Entry(pestaña_comidas)
entry_nombre_comidas.grid(row=0, column=1)

label_cantidad_comidas = tk.Label(pestaña_comidas, text="Cantidad:")
label_cantidad_comidas.grid(row=1, column=0)

entry_cantidad_comidas = tk.Entry(pestaña_comidas)
entry_cantidad_comidas.grid(row=1, column=1)

label_umbral_comidas = tk.Label(pestaña_comidas, text="Umbral Mínimo:")
label_umbral_comidas.grid(row=2, column=0)

entry_umbral_comidas = tk.Entry(pestaña_comidas)
entry_umbral_comidas.grid(row=2, column=1)

# Botón para añadir productos en comidas
boton_añadir_comidas = tk.Button(pestaña_comidas, text="Añadir Comida", command=lambda: añadir_producto("Comidas", entry_nombre_comidas, entry_cantidad_comidas, entry_umbral_comidas))
boton_añadir_comidas.grid(row=3, column=0, columnspan=2)

# Listbox para mostrar los productos en comidas
listbox_comidas = tk.Listbox(pestaña_comidas, width=50)
listbox_comidas.grid(row=4, column=0, columnspan=2)

# Botón para mostrar productos en comidas
boton_mostrar_comidas = tk.Button(pestaña_comidas, text="Mostrar Comidas", command=lambda: mostrar_productos("Comidas", listbox_comidas))
boton_mostrar_comidas.grid(row=5, column=0, columnspan=2)

# Pestaña Varios
label_nombre_varios = tk.Label(pestaña_varios, text="Nombre del Producto:")
label_nombre_varios.grid(row=0, column=0)

entry_nombre_varios = tk.Entry(pestaña_varios)
entry_nombre_varios.grid(row=0, column=1)

label_cantidad_varios = tk.Label(pestaña_varios, text="Cantidad:")
label_cantidad_varios.grid(row=1, column=0)

entry_cantidad_varios = tk.Entry(pestaña_varios)
entry_cantidad_varios.grid(row=1, column=1)

label_umbral_varios = tk.Label(pestaña_varios, text="Umbral Mínimo:")
label_umbral_varios.grid(row=2, column=0)

entry_umbral_varios = tk.Entry(pestaña_varios)
entry_umbral_varios.grid(row=2, column=1)

# Botón para añadir productos en varios
boton_añadir_varios = tk.Button(pestaña_varios, text="Añadir Varios", command=lambda: añadir_producto("Varios", entry_nombre_varios, entry_cantidad_varios, entry_umbral_varios))
boton_añadir_varios.grid(row=3, column=0, columnspan=2)

# Listbox para mostrar los productos en varios
listbox_varios = tk.Listbox(pestaña_varios, width=50)
listbox_varios.grid(row=4, column=0, columnspan=2)

# Botón para mostrar productos en varios
boton_mostrar_varios = tk.Button(pestaña_varios, text="Mostrar Varios", command=lambda: mostrar_productos("Varios", listbox_varios))
boton_mostrar_varios.grid(row=5, column=0, columnspan=2)

# Ejecutar la interfaz
ventana.mainloop()
