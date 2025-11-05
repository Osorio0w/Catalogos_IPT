# =====================================
# main.py - versión corregida 1.4.0 
# python3 main.py
# source myenv/bin/activate
# =====================================
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import os
import re
from footer import draw_footer
from encabezados import (
    cargar_fuentes,
    get_font_name,
    draw_header_page1,
    draw_header_pageN,
    get_logo_path
)

# -------------------------------
# CONFIG
# -------------------------------
EXCEL_FILE = "productos.xlsx"
OUTPUT_FILE = "catalogo.pdf"
PAGE_WIDTH, PAGE_HEIGHT = A4
PAGE2_START_Y_OFFSET = 6.4 * cm

# Detectar si estamos en Codespaces
IN_CODESPACES = 'CODESPACES' in os.environ or not os.environ.get('DISPLAY')


# -------------------------------
# FUNCIONES DE TEXTO Y TARJETAS
# -------------------------------
def dividir_texto_en_lineas(texto, ancho_max, fuente, tamaño_fuente, max_lineas=2):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    palabras = str(texto).split()
    lineas, linea_actual = [], ""
    for palabra in palabras:
        prueba_linea = linea_actual + " " + palabra if linea_actual else palabra
        if stringWidth(prueba_linea, fuente, tamaño_fuente) <= ancho_max:
            linea_actual = prueba_linea
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
            if len(lineas) >= max_lineas:
                break
    if linea_actual and len(lineas) < max_lineas:
        lineas.append(linea_actual)
    return lineas[:max_lineas]


def dibujar_texto_con_saltos(c, x, y, texto, ancho_max, fuente, tamaño_fuente, max_lineas=2):
    lineas = dividir_texto_en_lineas(texto, ancho_max, fuente, tamaño_fuente, max_lineas)
    c.setFont(fuente, tamaño_fuente)
    espaciado = tamaño_fuente * 0.9
    for i, linea in enumerate(lineas):
        c.drawCentredString(x, y - i * espaciado, linea)


def draw_code_background(c, x, y, card_width, card_height):
    """Fondo negro del código, perfectamente alineado dentro del cuadro del producto."""
    c.setFillColor(colors.black)
    code_width = 3.8 * cm
    code_height = 0.8 * cm
    # Alineado a la esquina superior izquierda del cuadro
    c.rect(x, y + card_height - code_height, code_width, code_height, fill=True, stroke=False)


def draw_triangle(c, x, y, size, color):
    c.setFillColor(color)
    path = c.beginPath()
    path.moveTo(x, y)
    path.lineTo(x - size, y)
    path.lineTo(x, y + size)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def draw_product_card(c, x, y, producto, triangle_color):
    """Dibuja una tarjeta de producto correctamente alineada y en orden de capas."""
    card_width = 6.0 * cm
    card_height = 6.0 * cm

    # 1️⃣ Marco del producto
    c.setStrokeColor(colors.black)
    c.rect(x, y, card_width, card_height)

    # 2️⃣ Franja negra del código
    draw_code_background(c, x, y, card_width, card_height)

    # 3️⃣ Texto del código (encima de la franja)
    c.setFillColor(colors.white)
    c.setFont(get_font_name('bold'), 13)
    c.drawCentredString(x + 1.9 * cm, y + card_height - 0.5 * cm, producto.get("codigo", ""))

    # 4️⃣ Imagen del producto
    try:
        img = ImageReader(producto.get("imagen", ""))
        c.drawImage(
            img,
            x + 0.5 * cm,
            y + 1.7 * cm,
            width=5.0 * cm,
            height=2.6 * cm,
            preserveAspectRatio=True,
            mask='auto'
        )
    except Exception:
        c.setFillColor(colors.black)
        c.setFont(get_font_name('regular'), 7)
        c.drawCentredString(x + card_width / 2, y + 2.8 * cm, "[Imagen no encontrada]")

    # 5️⃣ Descripción (debajo de la imagen)
    descripcion_x = x + card_width / 2
    descripcion_y = y + 1.4 * cm
    dibujar_texto_con_saltos(
        c,
        descripcion_x,
        descripcion_y,
        producto.get("descripcion", ""),
        card_width - 1.2 * cm,
        get_font_name('bold'),
        9,
        max_lineas=3
    )

    # 6️⃣ Triángulo decorativo
    draw_triangle(c, x + card_width, y, 1.4 * cm, triangle_color)


# -------------------------------
# GENERACIÓN DEL CATÁLOGO
# -------------------------------
def generar_catalogo(category_text, header_color):
    cargar_fuentes()
    logo_path = get_logo_path()
    df = pd.read_excel(EXCEL_FILE)
    c = canvas.Canvas(OUTPUT_FILE, pagesize=A4)
    triangle_color = header_color

    x_positions = [1.5 * cm, 8.0 * cm, 14.5 * cm]
    row_step = 6.7 * cm  # leve aumento para más espacio entre filas
    first_page_limit = 9
    other_pages_limit = 12

    header_height = draw_header_page1(c, category_text, header_color, logo_path)
    y = PAGE_HEIGHT - header_height - 6 * cm
    col, products_on_page, page_limit = 0, 0, first_page_limit

    for _, row in df.iterrows():
        imagen_nombre = str(row.get("imagen", "")).strip()
        imagen_path = os.path.join("imagenes", imagen_nombre) if imagen_nombre else ""

        producto = {
            "codigo": str(row.get("codigo", "")),
            "descripcion": str(row.get("descripcion", "")),
            "imagen": imagen_path
        }

        draw_product_card(c, x_positions[col], y, producto, triangle_color)
        col += 1
        products_on_page += 1

        if col == 3:
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
# INTERFAZ DE CONSOLA (Codespaces)
# -------------------------------
def modo_consola():
    print("=" * 60)
    print("GENERADOR DE CATÁLOGO - MODO CONSOLA")
    print("=" * 60)

    titulo = "BOLSAS"
    color_hex = "#63B7FF"

    while True:
        print(f"\nConfiguración actual:")
        print(f"1. Título: {titulo}")
        print(f"2. Color HEX: {color_hex}")
        print("3. Generar catálogo")
        print("4. Salir")

        opcion = input("\nSelecciona una opción (1-4): ").strip()

        if opcion == "1":
            nuevo_titulo = input("Nuevo título (ENTER para mantener actual): ").strip()
            if nuevo_titulo:
                titulo = nuevo_titulo
            print(f"✅ Título actualizado: {titulo}")

        elif opcion == "2":
            nuevo_color = input("Nuevo color HEX (ej: #3AA8FF): ").strip()
            if nuevo_color:
                if not re.match(r"^#?[0-9A-Fa-f]{6}$", nuevo_color):
                    print("❌ Error: Formato HEX inválido. Usa formato como #3AA8FF")
                    continue
                if not nuevo_color.startswith("#"):
                    nuevo_color = "#" + nuevo_color
                color_hex = nuevo_color
            print(f"✅ Color actualizado: {color_hex}")

        elif opcion == "3":
            try:
                print(f"\n🚀 Generando catálogo...")
                print(f"   - Título: {titulo}")
                print(f"   - Color: {color_hex}")
                color_obj = colors.HexColor(color_hex)
                generar_catalogo(titulo, color_obj)
                print(f"✅ ¡Catálogo generado exitosamente! 📄 {OUTPUT_FILE}")
                break
            except FileNotFoundError:
                print("❌ Error: No se encuentra el archivo productos.xlsx")
            except Exception as e:
                print(f"❌ Error al generar el catálogo: {e}")

        elif opcion == "4":
            print("👋 ¡Hasta luego!")
            break

        else:
            print("❌ Opción no válida. Por favor selecciona 1-4.")


# -------------------------------
# INTERFAZ GRÁFICA LOCAL
# -------------------------------
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
                messagebox.showerror("Error", "Formato HEX inválido. Usa formato como #3AA8FF.")
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
        print("🔧 Modo Codespaces detectado - Ejecutando interfaz de consola")
        modo_consola()
    else:
        print("🖥️  Modo local detectado - Ejecutando interfaz gráfica")
        ui_grafica()
