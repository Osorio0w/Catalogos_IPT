# =====================================
# main.py - versión modular corregida 1.7.0
# =====================================
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
import os
import re
from footer import draw_footer
from encabezados import (
    cargar_fuentes,
    draw_header_page1,
    draw_header_pageN,
    get_logo_path
)
from productos import draw_product_card

# -------------------------------
# CONFIG
# -------------------------------
EXCEL_FILE = "productos.xlsx"
OUTPUT_FILE = "catalogo.pdf"
PAGE_WIDTH, PAGE_HEIGHT = A4
PAGE2_START_Y_OFFSET = 6.4 * cm
IN_CODESPACES = 'CODESPACES' in os.environ or not os.environ.get('DISPLAY')


# -------------------------------
# GENERACIÓN DEL CATÁLOGO
# -------------------------------

def extraer_numero(valor):
    if pd.isna(valor):
        return 0
    texto = str(valor).strip()
    match = re.search(r"\d+(\.\d+)?", texto)
    if match:
        try:
            return float(match.group())
        except:
            return 0
    return 0


def generar_catalogo(category_text, header_color):

    # -------------------------------
    # LECTURA FLEXIBLE DEL EXCEL
    # -------------------------------
    df = pd.read_excel(EXCEL_FILE)

    # Normaliza nombres de columnas:
    # - sin espacios
    # - sin puntos
    # - minúsculas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(".", "_")
    )

    # Columnas que el programa realmente necesita
    COLUMNAS_NECESARIAS = ["codigo_catalogo", "descripcion", "imagen", "und", "bulto", "und_venta"]

    # Validación: si falta alguna columna, avisar de forma clara
    for col in COLUMNAS_NECESARIAS:
        if col not in df.columns:
            raise ValueError(f"❌ Falta la columna requerida en el Excel: '{col}'")

    # Quédate solo con las columnas necesarias
    df = df[COLUMNAS_NECESARIAS].fillna("")

    # -------------------------------
    # INICIALIZACIÓN DEL PDF
    # -------------------------------
    cargar_fuentes()
    logo_path = get_logo_path()
    c = canvas.Canvas(OUTPUT_FILE, pagesize=A4)
    triangle_color = header_color

    # -----------------------------------------
    # 📐 Cálculo automático de posiciones centradas
    # -----------------------------------------
    columnas = 3
    card_width = 6.0 * cm
    espacio = 0.6 * cm
    ancho_total = (card_width * columnas) + (espacio * (columnas - 1))
    x_inicio = (PAGE_WIDTH - ancho_total) / 2
    x_positions = [x_inicio + i * (card_width + espacio) for i in range(columnas)]

    # -----------------------------------------
    # Configuración vertical
    # -----------------------------------------
    row_step = 6.5 * cm
    first_page_limit = 9
    other_pages_limit = 12

    header_height = draw_header_page1(c, category_text, header_color, logo_path)
    y = PAGE_HEIGHT - header_height - 6 * cm
    col, products_on_page, page_limit = 0, 0, first_page_limit

    # -----------------------------------------
    # 🧱 Dibujo de tarjetas
    # -----------------------------------------
    for _, row in df.iterrows():

        # Procesar la ruta de imagen de forma segura
        imagen_nombre = str(row["imagen"]).strip().replace("\\", "/")

        if imagen_nombre.lower().startswith("images/"):
            imagen_nombre = imagen_nombre.replace("images/", "imagenes/", 1)

        # Si no existe, intenta dentro de /imagenes
        imagen_path = (
            imagen_nombre
            if os.path.exists(imagen_nombre)
            else os.path.join("imagenes", os.path.basename(imagen_nombre))
        )

        # Armar el diccionario esperado por productos.py
        producto = {
            "codigo": str(row["codigo_catalogo"]).strip(),
            "descripcion": str(row["descripcion"]).strip(),
            "imagen": imagen_path,
            "und": str(row["und"]).strip(),
            "bulto": str(row["bulto"]).strip(),
            "und_venta": str(row["und_venta"]).strip(),            # Se mostrará TAL CUAL en el PDF
            "und_venta_num": extraer_numero(row["und_venta"]),    # Valor numérico opcional

        }

        draw_product_card(c, x_positions[col], y, producto, triangle_color)

        col += 1
        products_on_page += 1

        if col == columnas:
            col = 0
            y -= row_step

        if products_on_page >= page_limit:
            draw_footer(c, header_color)
            c.showPage()
            header_height = draw_header_pageN(c, category_text, header_color, logo_path)
            y = PAGE_HEIGHT - header_height - PAGE2_START_Y_OFFSET
            col, products_on_page, page_limit = 0, 0, other_pages_limit

    draw_footer(c, header_color)
    c.save()
    print(f"✅ Catálogo generado: {OUTPUT_FILE}")


# -------------------------------
# INTERFAZ CONSOLA Y TK
# -------------------------------
def modo_consola():
    print("=" * 60)
    print("GENERADOR DE CATÁLOGO - MODO CONSOLA")
    print("=" * 60)
    titulo = "BOLSAS"
    color_hex = "#63B7FF"
    while True:
        print(f"\n1. Título: {titulo}")
        print(f"2. Color HEX: {color_hex}")
        print("3. Generar catálogo")
        print("4. Salir")
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        if opcion == "1":
            nuevo_titulo = input("Nuevo título: ").strip()
            if nuevo_titulo:
                titulo = nuevo_titulo
        elif opcion == "2":
            nuevo_color = input("Nuevo color HEX (#XXXXXX): ").strip()
            if not re.match(r"^#?[0-9A-Fa-f]{6}$", nuevo_color):
                print("❌ Color inválido.")
                continue
            if not nuevo_color.startswith("#"):
                nuevo_color = "#" + nuevo_color
            color_hex = nuevo_color
        elif opcion == "3":
            generar_catalogo(titulo, colors.HexColor(color_hex))
            break
        elif opcion == "4":
            print("👋 Adiós")
            break


def ui_grafica():
    from tkinter import Tk, Label, Entry, Button, colorchooser, messagebox
    root = Tk()
    root.title("Generador de Catálogo")
    root.geometry("420x300")

    Label(root, text="Título del catálogo:", font=("Arial", 11)).pack(pady=8)
    title_entry = Entry(root, font=("Arial", 11))
    title_entry.insert(0, "BOLSAS")
    title_entry.pack()

    Label(root, text="Color del encabezado:", font=("Arial", 11)).pack(pady=10)
    chosen_color = {"value": colors.HexColor("#63B7FF")}
    color_btn = Button(root, text="Elegir color", width=20)

    def choose_color():
        color_code = colorchooser.askcolor(title="Selecciona un color")[1]
        if color_code:
            chosen_color["value"] = colors.HexColor(color_code)
            color_btn.config(bg=color_code)
            color_entry.delete(0, "end")
            color_entry.insert(0, color_code)

    color_btn.config(command=choose_color)
    color_btn.pack()

    Label(root, text="O ingresa un color HEX (ej: #3AA8FF):", font=("Arial", 10)).pack(pady=5)
    color_entry = Entry(root, font=("Arial", 11))
    color_entry.insert(0, "#63B7FF")
    color_entry.pack()

    def start_generation():
        title = title_entry.get().strip() or "CATALOGO"
        manual_color = color_entry.get().strip()
        final_color = chosen_color["value"]
        if manual_color:
            if not re.match(r"^#?[0-9A-Fa-f]{6}$", manual_color):
                messagebox.showerror("Error", "Formato HEX inválido.")
                return
            if not manual_color.startswith("#"):
                manual_color = "#" + manual_color
            final_color = colors.HexColor(manual_color)
        generar_catalogo(title, final_color)
        messagebox.showinfo("Éxito", "Catálogo generado correctamente.")
        root.destroy()

    Button(root, text="Generar Catálogo", command=start_generation,
           font=("Arial", 12), bg="#4CAF50", fg="white", width=20).pack(pady=20)
    root.mainloop()


# -------------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------------
if __name__ == "__main__":
    if IN_CODESPACES:
        modo_consola()
    else:
        ui_grafica()
