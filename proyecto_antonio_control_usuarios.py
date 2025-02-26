import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  
import sqlite3
import os
from datetime import datetime

# Obtener la ruta del directorio actual del script
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'inventario.db')
log_path = os.path.join(script_dir, 'log.txt')

# Conexión a la base de datos SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear las tablas necesarias si no existen
cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,  
    cantidad INTEGER NOT NULL,
    umbral_minimo INTEGER NOT NULL
);
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS categorias (
    nombre TEXT PRIMARY KEY
);
''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    nombre TEXT PRIMARY KEY
);''')
conn.commit()

# LOG

# Función para registrar en el log
def registrar_log(usuario, accion, detalles):
    with open(log_path, "a") as log:
        log.write(f"[{datetime.now()}] Usuario: {usuario} - {accion} - {detalles}\n")

# USUARIOS

# Función para obtener usuario activo
def obtener_usuario_activo():
    return combo_usuarios.get() if combo_usuarios.get() else "Desconocido"

# Función para añadir usuarios
def añadir_usuario(entry_usuario):
    usuario = entry_usuario.get().strip()
    if not usuario:
        messagebox.showwarning("Advertencia", "Ingrese un nombre de usuario.")
        return
    cursor.execute("INSERT OR IGNORE INTO usuarios (nombre) VALUES (?)", (usuario,))
    conn.commit()
    actualizar_combo_usuarios()
    registrar_log(usuario, "Añadió usuario", usuario)
    messagebox.showinfo("Éxito", f"Usuario '{usuario}' añadido correctamente!")

# Función para eliminar usuarios
def eliminar_usuario():
    usuario = combo_usuarios.get()
    if not usuario:
        messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar.")
        return
    cursor.execute("DELETE FROM usuarios WHERE nombre = ?", (usuario,))
    conn.commit()
    actualizar_combo_usuarios()
    registrar_log(usuario, "Eliminó usuario", usuario)
    messagebox.showinfo("Éxito", f"Usuario '{usuario}' eliminado correctamente!")

# Función para actualizar el ComboBox de usuarios
def actualizar_combo_usuarios():
    usuarios = [usuario[0] for usuario in cursor.execute("SELECT nombre FROM usuarios").fetchall()]
    combo_usuarios["values"] = usuarios
    if usuarios:
        combo_usuarios.set(usuarios[0])

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Inventario")
ventana.geometry("800x600")
ventana.configure(bg="#f2f2f2")

# Centrado en la ventana
ventana.columnconfigure(0, weight=1)
ventana.rowconfigure(0, weight=1)

## Frame de gestión de usuarios
frame_usuarios = ttk.Frame(ventana)
frame_usuarios.pack(pady=10)

# Widgets para la gestión de usuarios
ttk.Label(frame_usuarios, text="Usuario activo:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
combo_usuarios = ttk.Combobox(frame_usuarios, font=("Arial", 12), width=20)
combo_usuarios.pack(side=tk.LEFT, padx=5)
actualizar_combo_usuarios()

entry_usuario = ttk.Entry(frame_usuarios, font=("Arial", 12))
entry_usuario.pack(side=tk.LEFT, padx=5)

tk.Button(frame_usuarios, text="Añadir Usuario", command=lambda: añadir_usuario(entry_usuario), font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(frame_usuarios, text="Eliminar Usuario", command=eliminar_usuario, font=("Arial", 12, "bold"), bg="#FF5733", fg="white").pack(side=tk.LEFT, padx=5)

# Función para verificar el stock bajo
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

# Función para crear una nueva categoría
def crear_categoria(entry_categoria):
    nueva_categoria = entry_categoria.get().strip().lower()
    
    if not nueva_categoria:
        messagebox.showwarning("Advertencia", "El nombre de la categoría no puede estar vacío.")
        return
    
    cursor.execute("SELECT * FROM categorias WHERE nombre = ?", (nueva_categoria,))
    if cursor.fetchone():
        messagebox.showwarning("Advertencia", f"La categoría '{nueva_categoria}' ya existe.")
    else:
        cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nueva_categoria,))
        conn.commit()
        actualizar_combo_categorias()
        crear_pestana_categoria(nueva_categoria)
        messagebox.showinfo("Éxito", f"Categoría '{nueva_categoria}' creada correctamente.")

# Función para eliminar una categoría
def eliminar_categoria(combo_categorias):
    categoria_a_eliminar = combo_categorias.get().strip().lower()
    
    if not categoria_a_eliminar:
        messagebox.showwarning("Advertencia", "Seleccione una categoría para eliminar.")
        return
    
    cursor.execute("DELETE FROM categorias WHERE nombre = ?", (categoria_a_eliminar,))
    cursor.execute("DELETE FROM productos WHERE categoria = ?", (categoria_a_eliminar,))
    conn.commit()
    actualizar_combo_categorias()
    eliminar_pestana_categoria(categoria_a_eliminar)
    messagebox.showinfo("Éxito", f"Categoría '{categoria_a_eliminar}' eliminada correctamente.")

# Función para actualizar el ComboBox de categorías
def actualizar_combo_categorias():
    categorias = [categoria[0] for categoria in cursor.execute("SELECT nombre FROM categorias").fetchall()]
    combo_categorias['values'] = categorias
    if categorias:
        combo_categorias.set(categorias[0])

# Función para crear la pestaña de una nueva categoría
def crear_pestana_categoria(categoria):
    pestaña = ttk.Frame(notebook)
    notebook.add(pestaña, text=categoria)

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

# Función para eliminar una pestaña de categoría
def eliminar_pestana_categoria(categoria):
    for tab in notebook.tabs():
        if notebook.tab(tab, "text") == categoria:
            notebook.forget(tab)
            break



# Centrado en la ventana
ventana.columnconfigure(0, weight=1)
ventana.rowconfigure(0, weight=1)

# Frame para creación y eliminación de categorías
frame_categoria = ttk.Frame(ventana)
frame_categoria.pack(pady=10)

ttk.Label(frame_categoria, text="Crear Nueva Categoría:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
entry_categoria = ttk.Entry(frame_categoria, font=("Arial", 12))
entry_categoria.pack(side=tk.LEFT, padx=5)

tk.Button(frame_categoria, text="Crear Categoría", command=lambda: crear_categoria(entry_categoria), font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

ttk.Label(frame_categoria, text="Eliminar Categoría:", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

# Cargar las categorías desde la base de datos
categorias = [categoria[0] for categoria in cursor.execute("SELECT nombre FROM categorias").fetchall()]
combo_categorias = ttk.Combobox(frame_categoria, values=categorias, font=("Arial", 12), width=20)
combo_categorias.pack(side=tk.LEFT, padx=5)

tk.Button(frame_categoria, text="Eliminar Categoría", command=lambda: eliminar_categoria(combo_categorias), font=("Arial", 12, "bold"), bg="#FF5733", fg="white").pack(side=tk.LEFT, padx=5)

# Crear el Notebook (Pestañas)
notebook = ttk.Notebook(ventana)
notebook.pack(pady=10, padx=10, expand=True)

# Crear las pestañas iniciales de las categorías existentes
categorias_iniciales = [categoria[0] for categoria in cursor.execute("SELECT nombre FROM categorias").fetchall()]
for categoria in categorias_iniciales:
    crear_pestana_categoria(categoria)

# Ejecutar la aplicación
ventana.mainloop()
