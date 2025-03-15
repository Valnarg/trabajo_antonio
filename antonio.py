import tkinter as tk
import sqlite3
import os
from tkinter import messagebox
from tkinter import ttk  
from tkinter import PhotoImage
from PIL import Image, ImageTk
from datetime import datetime


# Obtener la ruta del directorio actual del script
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'inventario.db')
log_path = os.path.join(script_dir, 'log.txt')

# Conexión a la base de datos SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear las tablas necesarias si no existen
cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,  
    cantidad REAL NOT NULL,  
    umbral_minimo REAL NOT NULL  
);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS categorias (
    nombre TEXT PRIMARY KEY
);''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    nombre TEXT PRIMARY KEY
);''')
conn.commit()




# LOG
def registrar_log(usuario, accion, detalles):
    # Obtener la fecha y hora actuales con el formato deseado
    fecha_hora = datetime.now().strftime("%d-%m-%Y a las %H:%M")
    
    # Escribir en el archivo de log
    with open(log_path, "a") as log:
        log.write(f"{fecha_hora} El usuario {usuario} {accion}: {detalles}\n")

# USUARIOS
def obtener_usuario_activo():
    return combo_usuarios.get() if combo_usuarios.get() else "Desconocido"

def añadir_usuario(entry_usuario):
    usuario = entry_usuario.get().strip()
    if not usuario:
        messagebox.showwarning("Advertencia", "Ingrese un nombre de usuario.")
        return
    cursor.execute("INSERT OR IGNORE INTO usuarios (nombre) VALUES (?)", (usuario,))
    conn.commit()
    actualizar_combo_usuarios()
    entry_usuario.delete(0, tk.END)  # Limpiar el campo después de añadir
    registrar_log(usuario, "Añadió usuario", usuario)
    messagebox.showinfo("Éxito", f"Usuario '{usuario}' añadido correctamente!")

def eliminar_usuario(entry_usuario):
    usuario = entry_usuario.get().strip()
    if not usuario:
        messagebox.showwarning("Advertencia", "Ingrese un nombre de usuario para eliminar.")
        return
    cursor.execute("DELETE FROM usuarios WHERE nombre = ?", (usuario,))
    conn.commit()
    actualizar_combo_usuarios()
    entry_usuario.delete(0, tk.END)  # Limpiar el campo después de eliminar
    registrar_log(usuario, "Eliminó usuario", usuario)
    messagebox.showinfo("Éxito", f"Usuario '{usuario}' eliminado correctamente!")

def actualizar_combo_usuarios():
    usuarios = [usuario[0] for usuario in cursor.execute("SELECT nombre FROM usuarios").fetchall()]
    combo_usuarios["values"] = usuarios
    if usuarios:
        combo_usuarios.set(usuarios[0])

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Inventario")


# Obtener el tamaño de la pantalla y ajustar la geometría de la ventana
pantalla_ancho = ventana.winfo_screenwidth()
pantalla_alto = ventana.winfo_screenheight()
ventana.geometry(f"{int(pantalla_ancho * 0.8)}x{int(pantalla_alto * 0.8)}")




ventana.configure(bg="white")

ventana.columnconfigure(0, weight=1)
ventana.rowconfigure(0, weight=1)


#IMAGEN DE FONDO


# Cargar la imagen de fondo 
fondo_imagen = Image.open("imagen1.jpg")  # Cargar imagen JPEG    
fondo_imagen = fondo_imagen.resize((ventana.winfo_screenwidth(), ventana.winfo_screenheight()), Image.LANCZOS)  # Ajustar tamaño al de la pantalla
# Convertir a un formato compatible con Tkinter
fondo_imagen_tk = ImageTk.PhotoImage(fondo_imagen)

# Crear un label para mostrar la imagen de fondo
label_fondo = tk.Label(ventana, image=fondo_imagen_tk)
label_fondo.place(x=0, y=0, relwidth=1, relheight=1)  # Colocar imagen en toda la ventana

# Importante: mantener una referencia a la imagen
label_fondo.image = fondo_imagen_tk

#GESTION DE USUARIOS

# Frame de gestión de usuarios
frame_usuarios = ttk.Frame(ventana)
frame_usuarios.pack(pady=10, fill=tk.BOTH, expand=True)

# Widgets para la gestión de usuarios
ttk.Label(frame_usuarios, text="Usuario activo:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
combo_usuarios = ttk.Combobox(frame_usuarios, font=("Arial", 12), width=20)
combo_usuarios.pack(side=tk.LEFT, padx=5)
actualizar_combo_usuarios()

entry_usuario = ttk.Entry(frame_usuarios, font=("Arial", 12))
entry_usuario.pack(side=tk.LEFT, padx=5)

tk.Button(frame_usuarios, text="Añadir Usuario", command=lambda: añadir_usuario(entry_usuario), font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(frame_usuarios, text="Eliminar Usuario", command=lambda: eliminar_usuario(entry_usuario), font=("Arial", 12, "bold"), bg="#FF5733", fg="white").pack(side=tk.LEFT, padx=5)

# Función para verificar el stock bajo
def verificar_stock_bajo():
    cursor.execute("SELECT nombre, cantidad, umbral_minimo FROM productos WHERE cantidad < umbral_minimo")
    productos_bajos = cursor.fetchall()
    
    if productos_bajos:
        mensaje = "⚠️ Productos con stock bajo:\n\n"
        for nombre, cantidad, umbral in productos_bajos:
            mensaje += f"🔴 {nombre} - Cantidad: {cantidad}, Umbral: {umbral}\n"
        return mensaje
    return None

# Función para añadir un producto (con soporte para decimales)
def añadir_producto(categoria, entry_nombre, entry_cantidad, entry_umbral, listbox):
    nombre = entry_nombre.get().strip().lower()
    
    try:
        cantidad = float(entry_cantidad.get())  # Convertir a float para permitir decimales
        umbral_minimo = float(entry_umbral.get())  # Convertir a float para permitir decimales
    except ValueError:
        messagebox.showwarning("Advertencia", "Ingrese números válidos en Cantidad y Umbral.")
        return

    if cantidad < 0 or umbral_minimo < 0:
        messagebox.showwarning("Advertencia", "Cantidad y Umbral no pueden ser negativos.")
        return

    cursor.execute('SELECT * FROM productos WHERE LOWER(nombre) = ? AND categoria = ?', (nombre, categoria))
    if cursor.fetchone():
        messagebox.showwarning("Advertencia", f"El producto '{nombre.capitalize()}' ya existe.")
    else:
        cursor.execute('INSERT INTO productos (nombre, categoria, cantidad, umbral_minimo) VALUES (?, ?, ?, ?)', 
                       (nombre.capitalize(), categoria, cantidad, umbral_minimo))
        conn.commit()
        mostrar_productos(categoria, listbox)
        usuario = obtener_usuario_activo()
        registrar_log(usuario, "Añadió producto", f"'{nombre.capitalize()}' en categoría '{categoria}' con cantidad {cantidad} y umbral mínimo {umbral_minimo}")

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
    usuario = obtener_usuario_activo()
    registrar_log(usuario, "Eliminó producto", f"'{item}' de la categoría '{categoria}'")
    messagebox.showinfo("Éxito", f"Producto '{item}' eliminado correctamente.")
    mostrar_productos(categoria, listbox)

# Función para modificar cantidad y umbral (con soporte para decimales)
def modificar_producto(categoria, listbox, entry_cantidad, entry_umbral):
    seleccion = listbox.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un producto para modificar.")
        return
    
    try:
        nueva_cantidad = float(entry_cantidad.get())  # Convertir a float para permitir decimales
        nuevo_umbral = float(entry_umbral.get())  # Convertir a float para permitir decimales
    except ValueError:
        messagebox.showwarning("Advertencia", "Ingrese números válidos.")
        return

    if nueva_cantidad < 0 or nuevo_umbral < 0:
        messagebox.showwarning("Advertencia", "Cantidad y Umbral no pueden ser negativos.")
        return

    item = listbox.get(seleccion[0]).split(" -")[0]  
    cursor.execute("UPDATE productos SET cantidad = ?, umbral_minimo = ? WHERE nombre = ? AND categoria = ?",
                   (nueva_cantidad, nuevo_umbral, item, categoria))
    conn.commit()
    
    mostrar_productos(categoria, listbox)
    usuario = obtener_usuario_activo()
    registrar_log(usuario, "Modificó producto", f"'{item}' en categoría '{categoria}' con nueva cantidad {nueva_cantidad} y umbral mínimo {nuevo_umbral}")
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
        registrar_log(obtener_usuario_activo(), "Creó categoría", nueva_categoria)
        messagebox.showinfo("Éxito", f"Categoría '{nueva_categoria}' creada correctamente.")

# Función para eliminar una categoría
def eliminar_categoria(combo_categorias):
    categoria_a_eliminar = combo_categorias.get().strip().lower()
    
    if not categoria_a_eliminar:
        messagebox.showwarning("Advertencia", "Seleccione una categoría para eliminar.")
        return
    
    # Eliminar los productos asociados a la categoría
    cursor.execute("DELETE FROM productos WHERE categoria = ?", (categoria_a_eliminar,))
    conn.commit()
    
    # Eliminar la categoría de la base de datos
    cursor.execute("DELETE FROM categorias WHERE nombre = ?", (categoria_a_eliminar,))
    conn.commit()
    
    # Eliminar la pestaña correspondiente
    for tab in notebook.tabs():
        if notebook.tab(tab, "text").lower() == categoria_a_eliminar:
            notebook.forget(tab)
            break
    
    actualizar_combo_categorias()
    usuario = obtener_usuario_activo()
    registrar_log(usuario, "Eliminó categoría", categoria_a_eliminar)
    messagebox.showinfo("Éxito", f"Categoría '{categoria_a_eliminar}' eliminada correctamente.")

# Función para actualizar el combo de categorías
def actualizar_combo_categorias():
    categorias = [categoria[0] for categoria in cursor.execute("SELECT nombre FROM categorias").fetchall()]
    combo_categorias["values"] = categorias
    if categorias:
        combo_categorias.set(categorias[0])

# Crear el widget Notebook para las pestañas de categorías
notebook = ttk.Notebook(ventana)
notebook.pack(pady=10, expand=True, fill=tk.BOTH)

# Frame para crear nueva categoría
frame_nueva_categoria = ttk.Frame(ventana)
frame_nueva_categoria.pack(pady=10, fill=tk.BOTH, expand=True)

entry_categoria = ttk.Entry(frame_nueva_categoria, font=("Arial", 12))
entry_categoria.pack(side=tk.LEFT, padx=5)

combo_categorias = ttk.Combobox(frame_nueva_categoria, font=("Arial", 12), width=20)
combo_categorias.pack(side=tk.LEFT, padx=5)

tk.Button(frame_nueva_categoria, text="Crear Categoría", command=lambda: crear_categoria(entry_categoria), font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(frame_nueva_categoria, text="Eliminar Categoría", command=lambda: eliminar_categoria(combo_categorias), font=("Arial", 12, "bold"), bg="#FF5733", fg="white").pack(side=tk.LEFT, padx=5)

# Función para crear la pestaña de una nueva categoría
def crear_pestana_categoria(categoria):
    pestaña = ttk.Frame(notebook)
    notebook.add(pestaña, text=categoria)

    frame_productos = ttk.Frame(pestaña)
    frame_productos.pack(pady=10, fill=tk.BOTH, expand=True)
    
    listbox = tk.Listbox(frame_productos, width=50, height=15, font=("Arial", 12))
    listbox.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
    
    frame_formulario = ttk.Frame(frame_productos)
    frame_formulario.pack(side=tk.LEFT, padx=10, fill=tk.Y, expand=True)
    
    tk.Label(frame_formulario, text="Nombre:", font=("Arial", 12)).pack(pady=5)
    entry_nombre = ttk.Entry(frame_formulario, font=("Arial", 12))
    entry_nombre.pack(pady=5)

    tk.Label(frame_formulario, text="Cantidad:", font=("Arial", 12)).pack(pady=5)
    entry_cantidad = ttk.Entry(frame_formulario, font=("Arial", 12))
    entry_cantidad.pack(pady=5)

    tk.Label(frame_formulario, text="Umbral Mínimo:", font=("Arial", 12)).pack(pady=5)
    entry_umbral = ttk.Entry(frame_formulario, font=("Arial", 12))
    entry_umbral.pack(pady=5)
    
    tk.Button(frame_formulario, text="Añadir Producto", 
               command=lambda: añadir_producto(categoria, entry_nombre, entry_cantidad, entry_umbral, listbox), 
               font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").pack(pady=5)
    
    tk.Button(frame_formulario, text="Eliminar Producto", 
               command=lambda: eliminar_producto(categoria, listbox), 
               font=("Arial", 12, "bold"), bg="#FF5733", fg="white").pack(pady=5)
    
    tk.Button(frame_formulario, text="Modificar Producto", 
               command=lambda: modificar_producto(categoria, listbox, entry_cantidad, entry_umbral), 
               font=("Arial", 12, "bold"), bg="#FFD700", fg="white").pack(pady=5)

    mostrar_productos(categoria, listbox)

# Función para cargar las categorías y productos al iniciar
def cargar_categorias_y_productos():
    categorias = [categoria[0] for categoria in cursor.execute("SELECT nombre FROM categorias").fetchall()]
    
    # Crear pestañas para cada categoría
    for categoria in categorias:
        crear_pestana_categoria(categoria)

    # Mostrar el mensaje de stock bajo al inicio del programa
    mensaje_stock_bajo = verificar_stock_bajo()
    if mensaje_stock_bajo:
        messagebox.showwarning("¡Atención! Stock bajo", mensaje_stock_bajo)

# Función para manejar el cierre del programa
def on_closing():
    # Mostrar el mensaje de stock bajo al finalizar el programa
    mensaje_stock_bajo = verificar_stock_bajo()
    if mensaje_stock_bajo:
        messagebox.showwarning("¡Atención! Stock bajo", mensaje_stock_bajo)
    
    ventana.destroy()

# Iniciar la interfaz
cargar_categorias_y_productos()
ventana.protocol("WM_DELETE_WINDOW", on_closing)
ventana.mainloop()
