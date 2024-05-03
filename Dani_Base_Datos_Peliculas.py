import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Configuración de la base de datos
fecha_actual = datetime.now().strftime("%Y-%m-%d")
nombre_db = f"Dani_{fecha_actual}.db"
conn = sqlite3.connect(nombre_db)
cursor = conn.cursor()

# Crear las tablas si no existen
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS plataformas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS peliculas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        ano_estreno INTEGER,
        director TEXT,
        plataforma_id INTEGER,
        FOREIGN KEY (plataforma_id) REFERENCES plataformas(id)
    )
    """
)
conn.commit()

# Insertar datos por defecto en las plataformas
plataformas_por_defecto = ["Netflix", "Amazon Prime", "HBO Max", "Disney+", "Apple TV+", "Otros"]
cursor.executemany(
    "INSERT INTO plataformas (nombre) VALUES (?) ON CONFLICT(nombre) DO NOTHING",
    [(p,) for p in plataformas_por_defecto],
)
conn.commit()

# Insertar datos por defecto en las películas
peliculas_por_defecto = [
    ("El Padrino", 1972, "Francis Ford Coppola",1),
    ("Matrix", 1999, "Lana Wachowski",2),
    ("Pulp Fiction", 1994, "Quentin Tarantino",1),
    ("Django", 2012, "Quentin Tarantino",1),
    ("El Resplandor", 1980, "Stanley Kubrick",2),
    ("Forrest Gump", 1994, "Robert Zemeckis",1),
    ("Blade Runner", 1982, "Ridley Scott",3),
    ("Psicosis", 1960, "Alfred Hitchcock",2),
    ("Tiburón", 1975, "Steven Spielberg",1),
    ("American History X", 1998, "Tony Kaye",3),
    ("La milla verde", 1999, "Frank Darabont",2),
    ("Cadena perpetua", 1994, "Frank Darabont",3),
    ("V de Vendetta", 2005, "James McTeigue",3),
]

if cursor.execute("SELECT COUNT(*) FROM peliculas").fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO peliculas (nombre, ano_estreno, director, plataforma_id) VALUES (?, ?, ?, ?)",
        peliculas_por_defecto,
    )
    conn.commit()

# Función para abrir el formulario de entrada de datos
def abrir_formulario(ventana_principal):
    form_ventana = tk.Toplevel(ventana_principal)
    form_ventana.title("Introducir Datos")
    form_ventana.geometry(centrar_ventana(500, 500, form_ventana))
    form_ventana.transient(ventana_principal)
    form_ventana.grab_set()
    form_ventana.focus_set()

    # Entradas de datos
    tk.Label(form_ventana, text="Nombre:").pack()
    entry_nombre = tk.Entry(form_ventana)
    entry_nombre.pack()

    tk.Label(form_ventana, text="Año de estreno:").pack()
    entry_ano_estreno = tk.Entry(form_ventana)
    entry_ano_estreno.pack()

    tk.Label(form_ventana, text="Director:").pack()
    entry_director = tk.Entry(form_ventana)
    entry_director.pack()

    # Menú desplegable para selección de plataformas de streaming
    tk.Label(form_ventana, text="Streaming:").pack()
    plataformas_streaming = cursor.execute(
        "SELECT nombre FROM plataformas"
    ).fetchall()

    plataformas_streaming = [p[0] for p in plataformas_streaming]

    var_streaming = tk.StringVar(form_ventana)
    var_streaming.set(plataformas_streaming[0])  # Valor por defecto
    menu_streaming = tk.OptionMenu(form_ventana, var_streaming, *plataformas_streaming)
    menu_streaming.pack()

    # Botón para guardar datos
    tk.Button(
        form_ventana, text="Guardar Datos", command=lambda: guardar_datos(
            entry_nombre, entry_ano_estreno, entry_director, var_streaming, form_ventana
        )
    ).pack(pady=5)

# Función para guardar datos en la base de datos
def guardar_datos(entry_nombre, entry_ano_estreno, entry_director, var_streaming, parent_window):
    nombre = entry_nombre.get()
    ano_estreno = entry_ano_estreno.get()
    director = entry_director.get()
    plataforma_nombre = var_streaming.get()

    try:
        # Obtener el ID de la plataforma
        plataforma_id = cursor.execute(
            "SELECT id FROM plataformas WHERE nombre = ?", (plataforma_nombre,)
        ).fetchone()[0]

        cursor.execute(
            "INSERT INTO peliculas (nombre, ano_estreno, director, plataforma_id) VALUES (?, ?, ?, ?)",
            (nombre, int(ano_estreno), director, plataforma_id),
        )
        conn.commit()
        messagebox.showinfo("Éxito", "Datos guardados correctamente", parent=parent_window)
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}", parent=parent_window)

# Función para ver películas
def ver_peliculas():
    def eliminar_pelicula():
        seleccion = lista.curselection()
        if seleccion:
            index = seleccion[0]
            pelicula_id = peliculas[index][0]
            confirm = messagebox.askyesno(
                "Confirmación",
                f"¿Desea eliminar la película?",
                parent=ventana_ver,
            )
            if confirm:
                cursor.execute("DELETE FROM peliculas WHERE id = ?", (pelicula_id,))
                conn.commit()
                cargar_peliculas()

    def cargar_peliculas():
        lista.delete(0, tk.END)
        global peliculas
        peliculas = cursor.execute(
            "SELECT peliculas.id, peliculas.nombre, peliculas.ano_estreno, peliculas.director, plataformas.nombre AS streaming "
            "FROM peliculas "
            "JOIN plataformas ON peliculas.plataforma_id = plataformas.id"
        ).fetchall()

        for pelicula in peliculas:
            lista.insert(tk.END, f"Nombre: {pelicula[1]}, Año: {pelicula[2]}, Director: {pelicula[3]}, Streaming: {pelicula[4]}")

    ventana_ver = tk.Toplevel(ventana)
    ventana_ver.title("Películas registradas")
    ventana_ver.geometry(centrar_ventana(375, 375, ventana_ver))
    ventana_ver.transient(ventana)
    ventana_ver.grab_set()

    lista = tk.Listbox(ventana_ver, width=45, height=15)
    lista.pack(pady=10)

    cargar_peliculas()

    eliminar_btn = tk.Button(
        ventana_ver, text="Eliminar", command=eliminar_pelicula
    )
    eliminar_btn.pack(pady=5)

# Función para buscar películas
def buscar_peliculas():
    def realizar_busqueda():
        termino_busqueda = entry_busqueda.get()
        criterio = var_criterio.get()

        try:
            if criterio == "Nombre":
                resultado = cursor.execute(
                    "SELECT peliculas.id, peliculas.nombre, peliculas.ano_estreno, peliculas.director, plataformas.nombre AS streaming "
                    "FROM peliculas "
                    "JOIN plataformas ON peliculas.plataforma_id = plataformas.id "
                    "WHERE peliculas.nombre LIKE ?",
                    (f"%{termino_busqueda}%",),
                ).fetchall()
            elif criterio == "Director":
                resultado = cursor.execute(
                    "SELECT peliculas.id, peliculas.nombre, peliculas.ano_estreno, peliculas.director, plataformas.nombre AS streaming "
                    "FROM peliculas "
                    "JOIN plataformas ON peliculas.plataforma_id = plataformas.id "
                    "WHERE peliculas.director LIKE ?",
                    (f"%{termino_busqueda}%",),
                ).fetchall()
            elif criterio == "Streaming":
                resultado = cursor.execute(
                    "SELECT peliculas.id, peliculas.nombre, peliculas.ano_estreno, peliculas.director, plataformas.nombre AS streaming "
                    "FROM peliculas "
                    "JOIN plataformas ON peliculas.plataforma_id = plataformas.id "
                    "WHERE plataformas.nombre LIKE ?",
                    (f"%{termino_busqueda}%",),
                ).fetchall()
            elif criterio == "Año de estreno":
                resultado = cursor.execute(
                    "SELECT peliculas.id, peliculas.nombre, peliculas.ano_estreno, peliculas.director, plataformas.nombre AS streaming "
                    "FROM peliculas "
                    "JOIN plataformas ON peliculas.plataforma_id = plataformas.id "
                    "WHERE peliculas.ano_estreno = ?",
                    (int(termino_busqueda),),
                ).fetchall()

            # Mostrar resultados en la lista
            lista_resultado.delete(0, tk.END)
            if resultado:
                for pelicula in resultado:
                    lista_resultado.insert(tk.END, f"Nombre: {pelicula[1]}, Año: {pelicula[2]}, Director: {pelicula[3]}, Streaming: {pelicula[4]}")
            else:
                lista_resultado.insert(tk.END, "No se encontraron resultados")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}", parent=ventana_busqueda)

    ventana_busqueda = tk.Toplevel(ventana)
    ventana_busqueda.title("Buscar películas")
    ventana_busqueda.geometry(centrar_ventana(375, 375, ventana_busqueda))
    ventana_busqueda.transient(ventana)
    ventana_busqueda.grab_set()

    var_criterio = tk.StringVar(ventana_busqueda)
    var_criterio.set("Nombre")

    tk.Label(ventana_busqueda, text="Buscar por:").pack()
    tk.Radiobutton(ventana_busqueda, text="Nombre", variable=var_criterio, value="Nombre").pack()
    tk.Radiobutton(ventana_busqueda, text="Director", variable=var_criterio, value="Director").pack()
    tk.Radiobutton(ventana_busqueda, text="Streaming", variable=var_criterio, value="Streaming").pack()
    tk.Radiobutton(ventana_busqueda, text="Año de estreno", variable=var_criterio, value="Año de estreno").pack()

    tk.Label(ventana_busqueda, text="Término de búsqueda").pack()
    entry_busqueda = tk.Entry(ventana_busqueda)
    entry_busqueda.pack()

    tk.Button(ventana_busqueda, text="Buscar", command=realizar_busqueda).pack(pady=10)

    lista_resultado = tk.Listbox(ventana_busqueda, width=45, height=15)
    lista_resultado.pack(pady=10)

# Función para centrar ventanas
def centrar_ventana(ancho, alto, ventana):
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    x_ventana = (ancho_pantalla // 2) - (ancho // 2)
    y_ventana = (alto_pantalla // 2) - (alto // 2)
    return f"{ancho}x{alto}+{x_ventana}+{y_ventana}"

# Función para cerrar la ventana principal y abrir la de despedida
def cerrar_ventana_principal():
    ventana.quit()  # Cerrar la ventana principal
    ventana.destroy()  # Destruir para limpiar recursos

    despedida_ventana = tk.Tk()
    despedida_ventana.title("Despedida")
    despedida_ventana.geometry(centrar_ventana(300, 200, despedida_ventana))

    tk.Label(despedida_ventana, text="Gracias por usar la aplicación. ¡Hasta luego!").pack(pady=10)

    # Cerrar automáticamente después de 3 segundos
    despedida_ventana.after(3000, lambda: despedida_ventana.quit())

# Ventana de bienvenida
ventana_bienvenida = tk.Tk()
ventana_bienvenida.title("Bienvenida")
ventana_bienvenida.geometry(centrar_ventana(400, 200, ventana_bienvenida))

tk.Label(ventana_bienvenida, text="Bienvenido a la gestión de las pelis de Dani").pack(pady=10)
tk.Label(ventana_bienvenida, text="Por favor, espere mientras se carga la aplicación...").pack(pady=10)

ventana_bienvenida.after(3000, lambda: (
    ventana_bienvenida.quit(),  # Cerrar la ventana de bienvenida
    ventana_bienvenida.destroy(),  # Destruir para liberar recursos
    abrir_ventana_principal()  # Abrir la ventana principal
))

# Ventana principal
def abrir_ventana_principal():
    global ventana  # Hacer la ventana principal global para accesibilidad
    ventana = tk.Tk()
    ventana.title("Gestión de Base de Datos")
    ventana.geometry(centrar_ventana(400, 400, ventana))
    
    # Configurar cierre para abrir ventana de despedida
    ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana_principal)

    # Frame para botones
    botones_frame = tk.Frame(ventana)
    botones_frame.pack(pady=5)

    tk.Button(botones_frame, text="Introducir Datos", command=lambda: abrir_formulario(ventana)).pack(pady=5)
    tk.Button(botones_frame, text="Ver Películas", command=ver_peliculas).pack(pady=5)
    tk.Button(botones_frame, text="Buscar Películas", command=buscar_peliculas).pack(pady=5)

    ventana.mainloop()

# Iniciar el ciclo principal de Tkinter
tk.mainloop()
