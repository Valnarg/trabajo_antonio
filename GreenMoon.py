import tkinter as tk
import sqlite3
import os
import sys
from tkinter import messagebox
from tkinter import ttk  
from tkinter import PhotoImage
from PIL import Image, ImageTk
from datetime import datetime
from shutil import copyfile


# Rutas de los archivos necesarios

# Rutas de los archivos necesarios
if getattr(sys, 'frozen', False):
    # Si el script está empaquetado como .exe, obtenemos el directorio donde se ejecuta el .exe
    script_dir = os.path.dirname(sys.executable)
    # Utiliza _MEIPASS para acceder a los archivos empaquetados
    image_path = os.path.join(script_dir, 'imagen1.jpg')
    log_path = os.path.join(script_dir, 'log.txt')
    db_path = os.path.join(script_dir, 'inventario.db')
else:
    # Si es un script normal, obtenemos el directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, 'imagen1.jpg')
    log_path = os.path.join(script_dir, 'log.txt')
    db_path = os.path.join(script_dir, 'inventario.db')

# Ruta para la carpeta 'Inventario Diario'
carpeta_inventarios = os.path.join(script_dir, "Inventario Diario")

# Verificar si la carpeta ya existe antes de crearla
if not os.path.exists(carpeta_inventarios):
    os.makedirs(carpeta_inventarios)
    print(f"Carpeta '{carpeta_inventarios}' creada.")  # Solo para depuración
fecha_actual = datetime.now().strftime("%d-%m-%Y")
# Ruta para el archivo de inventario dentro de la carpeta 'Inventario Diario'
nombre_archivo = os.path.join(carpeta_inventarios, f"{fecha_actual} Inventario.txt")


# Función para copiar los archivos necesarios desde el paquete empaquetado al directorio de ejecución
def copiar_archivos():
    if not os.path.exists(db_path):  # Si la base de datos no existe en el directorio de trabajo
        if getattr(sys, 'frozen', False):
            # Copia la base de datos desde el archivo empaquetado
            base_db_path = os.path.join(sys._MEIPASS, 'inventario.db')
            copyfile(base_db_path, db_path)

# Llamar a la función para copiar los archivos si es necesario
copiar_archivos()

# Crear la base de datos si no existe
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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

    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        nombre TEXT PRIMARY KEY
    );''')

    conn.commit()

## LOG + inventario diario

# Crear el archivo de log si no existe
def crear_log():
    if not os.path.exists(log_path):
        with open(log_path, 'w') as log_file:
            log_file.write("Log de acciones\n")
            

def registrar_log(usuario, accion, detalles):
    # Obtener la fecha y hora actuales con el formato deseado
    fecha_hora = datetime.now().strftime("%d-%m-%Y a las %H:%M")
    
    # Escribir en el archivo de log
    with open(log_path, "a") as log:
        log.write(f"{fecha_hora} El usuario {usuario} {accion}: {detalles}\n")


# Función para generar el archivo de inventario
def generar_inventario():
    print("Generando inventario...")  # Para depurar

    # Obtener la fecha actual para usarla en el nombre del archivo
    fecha_actual = datetime.now().strftime("%d-%m-%Y")
    
    # Ruta de la carpeta "Inventario Diario"
    carpeta_inventarios = os.path.join(script_dir, "Inventario Diario")
    
    # Crear la carpeta si no existe
    if not os.path.exists(carpeta_inventarios):
        os.makedirs(carpeta_inventarios)
        print(f"Carpeta '{carpeta_inventarios}' creada.")  # Para depurar
    
    # Ruta completa del archivo dentro de la carpeta
    nombre_archivo = os.path.join(carpeta_inventarios, f"{fecha_actual} Inventario.txt")
    
    # Verificar si el archivo ya existe (en ese caso, se sobrescribe)
    if os.path.exists(nombre_archivo):
        print(f"El archivo {nombre_archivo} ya existe. Se eliminará.")  # Para depurar
        os.remove(nombre_archivo)  # Eliminar el archivo viejo si existe

    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Consultar las categorías, nombres de productos y cantidades
    query = """
    SELECT categoria, nombre, cantidad FROM productos
    """
    cursor.execute(query)

    # Obtener todos los resultados
    inventario = cursor.fetchall()

    # Crear y escribir en el archivo de texto
    with open(nombre_archivo, 'w') as file:
        file.write("Inventario del día " + fecha_actual + "\n")
        file.write("=" * 40 + "\n")
        
        # Escribir los datos de cada producto
        for categoria, nombre_producto, cantidad in inventario:
            file.write(f"{categoria}: {nombre_producto} - {cantidad} unidades\n")

    # Cerrar la conexión a la base de datos
    conn.close()

    print(f"Inventario generado en el archivo {nombre_archivo}")  # Para depurar


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
    
    # Preguntar confirmación antes de eliminar
    respuesta = messagebox.askyesno("Confirmación", f"¿Estás seguro de que deseas eliminar el usuario '{usuario}'?")
    if respuesta:  # Si el usuario selecciona "Sí"
        cursor.execute("DELETE FROM usuarios WHERE nombre = ?", (usuario,))
        conn.commit()
        actualizar_combo_usuarios()
        entry_usuario.delete(0, tk.END)  # Limpiar el campo después de eliminar
        registrar_log(usuario, "Eliminó usuario", usuario)
        messagebox.showinfo("Éxito", f"Usuario '{usuario}' eliminado correctamente!")
    else:
        messagebox.showinfo("Acción cancelada", "Eliminación de usuario cancelada.")

    conn.commit()
   

def actualizar_combo_usuarios():
    usuarios = [usuario[0] for usuario in cursor.execute("SELECT nombre FROM usuarios").fetchall()]
    combo_usuarios["values"] = usuarios
    if usuarios:
        combo_usuarios.set(usuarios[0])
# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Green Moon: Gestión de Inventario")

# Obtener el tamaño de la pantalla y ajustar la geometría de la ventana
pantalla_ancho = ventana.winfo_screenwidth()
pantalla_alto = ventana.winfo_screenheight()
ventana.geometry(f"{int(pantalla_ancho * 0.8)}x{int(pantalla_alto * 0.8)}")




ventana.configure(bg="black" )

ventana.columnconfigure(0, weight=1)
ventana.rowconfigure(0, weight=1)


# Establecer estilo global
style = ttk.Style()

# Estilos para los frames, etiquetas y entradas
style.configure("TFrame", background="black")
style.configure("TLabel", background="black", foreground="#00FF00")  # Estilo para las etiquetas
style.configure("TEntry", background="black", foreground="black")  # Estilo para las entradas

# Estilo para las pestañas del notebook
style.configure("TNotebook", background="black")  # Fondo negro para todo el área del notebook
style.configure("TNotebook.Tab", background="black", foreground="black", font=("Arial", 12, "bold"))
style.map("TNotebook.Tab", background=[('selected', 'green')], foreground=[('selected', 'black')])  # Color cuando la pestaña está seleccionada



#IMAGEN DE FONDO


# Cargar la imagen de fondo 
#fondo_imagen = Image.open(image_path)   
#fondo_imagen = fondo_imagen.resize((ventana.winfo_screenwidth(), ventana.winfo_screenheight()), Image.LANCZOS)  # Ajustar tamaño al de la pantalla
# Convertir a un formato compatible con Tkinter
#fondo_imagen_tk = ImageTk.PhotoImage(fondo_imagen)

# Crear un label para mostrar la imagen de fondo
#label_fondo = tk.Label(ventana, image=fondo_imagen_tk)
#label_fondo.place(x=0, y=0, relwidth=1, relheight=1)  # Colocar imagen en toda la ventana

# Importante: mantener una referencia a la imagen
#label_fondo.image = fondo_imagen_tk

#GESTION DE USUARIOS

# Frame de gestión de usuarios
frame_usuarios = ttk.Frame(ventana, style="TFrame")
frame_usuarios.pack(pady=10, fill=tk.BOTH, expand=True)

# Estilo para el frame
ventana.tk_setPalette(background="black")
style = ttk.Style()
style.configure("TFrame",background="black")

# Widgets para la gestión de usuarios
ttk.Label(frame_usuarios, text="Usuario activo:", background="black", foreground="#00FF00", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

# Combobox de usuarios
combo_usuarios = ttk.Combobox(frame_usuarios, background="black", foreground="black", font=("Arial", 12), width=20)
combo_usuarios.pack(side=tk.LEFT, padx=5)
# Llamar a la función para actualizar el combo de usuarios (si existe)
actualizar_combo_usuarios()

# Entry para añadir usuario
entry_usuario = ttk.Entry(frame_usuarios, font=("Arial", 12), )
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
    
    # Preguntar confirmación antes de eliminar
    respuesta = messagebox.askyesno("Confirmación", f"¿Estás seguro de que deseas eliminar el producto '{item}' de la categoría '{categoria}'?")
    if respuesta:  # Si el usuario selecciona "Sí"
        cursor.execute("DELETE FROM productos WHERE nombre = ? AND categoria = ?", (item, categoria))
        conn.commit()
        listbox.delete(seleccion[0])
        usuario = obtener_usuario_activo()
        registrar_log(usuario, "Eliminó producto", f"'{item}' de la categoría '{categoria}'")
        messagebox.showinfo("Éxito", f"Producto '{item}' eliminado correctamente.")
        mostrar_productos(categoria, listbox)
    else:
        messagebox.showinfo("Acción cancelada", "Eliminación de producto cancelada.")
    conn.commit()
    
#funcion para convertir valores
def convertir_a_float(valor):
    """Convierte un string a float de manera segura."""
    try:
        return float(valor)
    except ValueError:
        return None  # Retorna None si no se puede convertir

def extraer_valor_operador(entrada):
    """Extrae operador y valor de la entrada del usuario."""
    if not entrada:
        return None, None
    
    operadores = {'+', '-', '*', '/'}
    
    if entrada[0] in operadores:
        operador = entrada[0]
        valor = convertir_a_float(entrada[1:])
    else:
        operador = 'set'
        valor = convertir_a_float(entrada)
    
    return operador, valor


# Función para modificar nombre, cantidad y umbral (con soporte para modificaciones independientes)
def modificar_producto(categoria, listbox, entry_nombre, entry_cantidad, entry_umbral):
    seleccion = listbox.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Seleccione un producto para modificar.")
        return
    
    item = listbox.get(seleccion[0]).split(" -")[0]

    nuevo_nombre = None
    nueva_cantidad = None
    nuevo_umbral = None
    mensaje_log = ""

    nombre_ingresado = entry_nombre.get().strip()
    if nombre_ingresado:
        cursor.execute("UPDATE productos SET nombre = ? WHERE nombre = ? AND categoria = ?", 
                       (nombre_ingresado, item, categoria))
        nuevo_nombre = nombre_ingresado
        mensaje_log += f"El usuario {obtener_usuario_activo()} ha modificado el nombre de '{item}' a '{nuevo_nombre}'. "

    cantidad_ingresada = entry_cantidad.get().strip()
    if cantidad_ingresada:
        operador, valor = extraer_valor_operador(cantidad_ingresada)
        if valor is None:
            messagebox.showwarning("Advertencia", "Ingrese un número válido para la cantidad.")
            return
        if operador not in ['+', '-', '*', '/', 'set']:
            messagebox.showwarning("Advertencia", "El operador debe ser uno de los siguientes: +, -, *, /.")
            return

        cursor.execute("SELECT cantidad FROM productos WHERE nombre = ? AND categoria = ?", (item, categoria))
        cantidad_actual = cursor.fetchone()
        if cantidad_actual is None:
            messagebox.showwarning("Advertencia", "El producto seleccionado no existe en la base de datos.")
            return
        cantidad_actual = cantidad_actual[0]
        cantidad_anterior = cantidad_actual

        if operador == 'set':
            nueva_cantidad = valor
        elif operador == '+':
            nueva_cantidad = cantidad_actual + valor
        elif operador == '-':
            nueva_cantidad = cantidad_actual - valor
        elif operador == '*':
            nueva_cantidad = cantidad_actual * valor
        elif operador == '/':
            if valor == 0:
                messagebox.showwarning("Advertencia", "No se puede dividir por cero.")
                return
            nueva_cantidad = cantidad_actual / valor

        if nueva_cantidad < 0:
            messagebox.showwarning("Advertencia", "La cantidad no puede ser negativa.")
            return

        cursor.execute("UPDATE productos SET cantidad = ? WHERE nombre = ? AND categoria = ?", 
                       (nueva_cantidad, item, categoria))
        mensaje_log += f"Se modificó la cantidad de {cantidad_anterior} a {nueva_cantidad}. "

    umbral_ingresado = entry_umbral.get().strip()
    if umbral_ingresado:
        operador, valor_umbral = extraer_valor_operador(umbral_ingresado)
        if valor_umbral is None:
            messagebox.showwarning("Advertencia", "Ingrese un número válido para el umbral.")
            return
        if operador not in ['+', '-', '*', '/', 'set']:
            messagebox.showwarning("Advertencia", "El operador del umbral debe ser uno de los siguientes: +, -, *, /." )
            return

        cursor.execute("SELECT umbral_minimo FROM productos WHERE nombre = ? AND categoria = ?", (item, categoria))
        umbral_actual = cursor.fetchone()
        if umbral_actual is None:
            messagebox.showwarning("Advertencia", "El producto seleccionado no existe en la base de datos.")
            return
        umbral_actual = umbral_actual[0]
        umbral_anterior = umbral_actual

        if operador == 'set':
            nuevo_umbral = valor_umbral
        elif operador == '+':
            nuevo_umbral = umbral_actual + valor_umbral
        elif operador == '-':
            nuevo_umbral = umbral_actual - valor_umbral
        elif operador == '*':
            nuevo_umbral = umbral_actual * valor_umbral
        elif operador == '/':
            if valor_umbral == 0:
                messagebox.showwarning("Advertencia", "No se puede dividir el umbral por cero.")
                return
            nuevo_umbral = umbral_actual / valor_umbral

        if nuevo_umbral < 0:
            messagebox.showwarning("Advertencia", "El umbral no puede ser negativo.")
            return

        cursor.execute("UPDATE productos SET umbral_minimo = ? WHERE nombre = ? AND categoria = ?", 
                       (nuevo_umbral, item, categoria))
        mensaje_log += f"Se modificó el umbral de {umbral_anterior} a {nuevo_umbral}. "

    if not (nuevo_nombre or nueva_cantidad or nuevo_umbral):
        messagebox.showwarning("Advertencia", "Debe ingresar al menos un valor para modificar.")
        return

    conn.commit()
    mostrar_productos(categoria, listbox)
    mensaje_log = f"{item} - {mensaje_log} - Categoría: {categoria}"
    registrar_log(obtener_usuario_activo(), "Modificó producto", mensaje_log)
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
    
    # Verificar si la categoría tiene productos asociados
    cursor.execute("SELECT COUNT(*) FROM productos WHERE categoria = ?", (categoria_a_eliminar,))
    cantidad_productos = cursor.fetchone()[0]
    
    if cantidad_productos > 0:
        respuesta = messagebox.askyesno("Confirmación", f"¡Atención! La categoría '{categoria_a_eliminar}' tiene productos asociados. ¿Estás seguro de que deseas eliminarla?")
        if not respuesta:
            messagebox.showinfo("Acción cancelada", "Eliminación de categoría cancelada.")
            return
    
    # Preguntar confirmación antes de eliminar la categoría
    respuesta = messagebox.askyesno("Confirmación", f"¿Estás seguro de que deseas eliminar la categoría '{categoria_a_eliminar}'?")
    if respuesta:  # Si el usuario selecciona "Sí"
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
    else:
        messagebox.showinfo("Acción cancelada", "Eliminación de categoría cancelada.")
    conn.commit()

def actualizar_combo_categorias():
    categorias = [categoria[0] for categoria in cursor.execute("SELECT nombre FROM categorias").fetchall()]
    combo_categorias["values"] = categorias
    if categorias:
        combo_categorias.set(categorias[0])



# Crear el widget Notebook para las pestañas de categorías
notebook = ttk.Notebook(ventana ,style="TNotebook")
notebook.pack(pady=10, expand=True, fill=tk.BOTH)

# Frame para crear nueva categoría
frame_nueva_categoria = ttk.Frame(ventana,style="TFrame")
frame_nueva_categoria.pack(pady=10, fill=tk.BOTH, expand=True)


# Widgets para la gestión de categorías
entry_categoria = ttk.Entry(frame_nueva_categoria, font=("Arial", 12))
entry_categoria.pack(side=tk.LEFT, padx=5)
tk.Button(frame_nueva_categoria, text="Crear Categoría", command=lambda: crear_categoria(entry_categoria), font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

combo_categorias = ttk.Combobox(frame_nueva_categoria, font=("Arial", 12), width=20)
combo_categorias.pack(side=tk.LEFT, padx=5)
tk.Button(frame_nueva_categoria, text="Eliminar Categoría", command=lambda: eliminar_categoria(combo_categorias), font=("Arial", 12, "bold"), bg="#FF5733", fg="white").pack(side=tk.LEFT, padx=5)


# Función para crear la pestaña de una nueva categoría
def crear_pestana_categoria(categoria):
    pestaña = ttk.Frame(notebook)
    notebook.add(pestaña, text=categoria)

    # Crear el frame para productos con fondo negro
    frame_productos = ttk.Frame(pestaña, style="TFrame")
    frame_productos.pack(pady=10, fill=tk.BOTH, expand=True)

    # Lista de productos
    listbox = tk.Listbox(frame_productos, width=50, height=15, font=("Arial", 12), foreground="#00FF00", background="black")
    listbox.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

    # Frame para el formulario de productos
    frame_formulario = ttk.Frame(frame_productos, style="TFrame")
    frame_formulario.pack(side=tk.LEFT, padx=10, fill=tk.Y, expand=True)

    # Etiqueta y entrada para Nombre
    tk.Label(frame_formulario, text="Nombre:", font=("Arial", 12), foreground="#00FF00", background="black").pack(pady=5)
    entry_nombre = ttk.Entry(frame_formulario, font=("Arial", 12), foreground="black", background="black")
    entry_nombre.pack(pady=5)

    # Etiqueta y entrada para Cantidad
    tk.Label(frame_formulario, text="Cantidad:", font=("Arial", 12), foreground="#00FF00", background="black").pack(pady=5)
    entry_cantidad = ttk.Entry(frame_formulario, font=("Arial", 12), foreground="black", background="black")
    entry_cantidad.pack(pady=5)

    # Etiqueta y entrada para Umbral Mínimo
    tk.Label(frame_formulario, text="Umbral Mínimo:", font=("Arial", 12), foreground="#00FF00", background="black").pack(pady=5)
    entry_umbral = ttk.Entry(frame_formulario, font=("Arial", 12), foreground="black", background="black")
    entry_umbral.pack(pady=5)
    
    
    tk.Button(frame_formulario, text="Añadir Producto", 
               command=lambda: añadir_producto(categoria, entry_nombre, entry_cantidad, entry_umbral, listbox), 
               font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").pack(pady=5)
    
    tk.Button(frame_formulario, text="Eliminar Producto", 
               command=lambda: eliminar_producto(categoria, listbox), 
               font=("Arial", 12, "bold"), bg="#FF5733", fg="white").pack(pady=5)
    
    tk.Button(frame_formulario, text="Modificar Producto", 
               command=lambda: modificar_producto(categoria, listbox, entry_nombre, entry_cantidad, entry_umbral), 
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
    generar_inventario()
    # Mostrar el mensaje de stock bajo al finalizar el programa
    mensaje_stock_bajo = verificar_stock_bajo()
    if mensaje_stock_bajo:
        messagebox.showwarning("¡Atención! Stock bajo", mensaje_stock_bajo)
    
    ventana.destroy()

# Iniciar la interfaz
cargar_categorias_y_productos()
ventana.protocol("WM_DELETE_WINDOW", on_closing)
ventana.mainloop()
