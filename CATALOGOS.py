import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
import tkinter as tk
from tkinter import colorchooser, messagebox
import os
from PIL import Image
import re

# ================================
# CONFIGURACIÓN PRINCIPAL
# ================================
EXCEL_FILE = "productos.xlsx"
OUTPUT_FILE = "catalogo.pdf"
LOGO_FILE_NAMES = ["logo.png", "insumosparatodo_logo.png"]
CODE_BACKGROUND_PATH = "placeholder_codigos.png"
CANVA_SANS_BOLD = "fuentes/CanvaSans-Bold.ttf"
CANVA_SANS_REGULAR = "fuentes/CanvaSans-Regular.ttf"
PAGE_WIDTH, PAGE_HEIGHT = A4

PAGE2_START_Y_OFFSET = 6.4 * cm  # Offset página 2+
# Encabezado pedidos por ti:
HEADER_FIRST_W_CM = 17.6
HEADER_FIRST_H_CM = 7.3
HEADER_NEXT_W_CM = 17.6
HEADER_NEXT_H_CM = 2.5

# ================================
# FUNCIONES DE FUENTES
# ================================
def cargar_fuentes():
    try:
        os.makedirs("fuentes", exist_ok=True)
        if os.path.exists(CANVA_SANS_REGULAR):
            pdfmetrics.registerFont(TTFont('CanvaSans', CANVA_SANS_REGULAR))
        if os.path.exists(CANVA_SANS_BOLD):
            pdfmetrics.registerFont(TTFont('CanvaSans-Bold', CANVA_SANS_BOLD))
    except Exception as e:
        print(f"⚠️ Error al cargar fuentes: {e}")


def get_font_name(style='regular'):
    if style == 'bold':
        if 'CanvaSans-Bold' in pdfmetrics.getRegisteredFontNames():
            return 'CanvaSans-Bold'
        elif 'CanvaSans' in pdfmetrics.getRegisteredFontNames():
            return 'CanvaSans'
        else:
            return 'Helvetica-Bold'
    else:
        if 'CanvaSans' in pdfmetrics.getRegisteredFontNames():
            return 'CanvaSans'
        else:
            return 'Helvetica'


# ================================
# FUNCIONES DE TEXTO
# ================================
def dividir_texto_en_lineas(texto, ancho_max, fuente, tamaño_fuente, max_lineas=2):
    palabras = str(texto).split()
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        prueba_linea = linea_actual + " " + palabra if linea_actual else palabra
        ancho_prueba = stringWidth(prueba_linea, fuente, tamaño_fuente)

        if ancho_prueba <= ancho_max:
            linea_actual = prueba_linea
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
            if len(lineas) >= max_lineas:
                break

    if linea_actual and len(lineas) < max_lineas:
        lineas.append(linea_actual)

    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        ultima_linea = lineas[-1]
        while stringWidth(ultima_linea + "...", fuente, tamaño_fuente) > ancho_max and len(ultima_linea) > 3:
            ultima_linea = ultima_linea[:-1]
        lineas[-1] = ultima_linea + "..." if len(ultima_linea) > 3 else "..."

    return lineas


def dibujar_texto_con_saltos(c, x, y, texto, ancho_max, fuente, tamaño_fuente, max_lineas=2):
    lineas = dividir_texto_en_lineas(texto, ancho_max, fuente, tamaño_fuente, max_lineas)
    c.setFont(fuente, tamaño_fuente)
    espaciado_linea = tamaño_fuente * 0.9
    for i, linea in enumerate(lineas):
        c.drawCentredString(x, y - (i * espaciado_linea), linea)
    return len(lineas)


# ================================
# LOGO
# ================================
def get_logo_path():
    for name in LOGO_FILE_NAMES:
        if os.path.exists(name):
            return name
    return ""


# ================================
# DIBUJAR ENCABEZADOS (generativos)
# ================================
def _mask_round_except_lower_right(c, x, y, w, h, radius):
    """
    Dibuja máscara para que solo la esquina inferior derecha quede redondeada.
    We achieve effect: draw rounded rect then overlay white squares on three corners.
    """
    # We already drew rounded rect; here overlay rectangles to square off other corners:
    # top-left
    c.setFillColor(colors.white)
    c.rect(x, y + h - radius, radius, radius, stroke=0, fill=1)
    # top-right
    c.rect(x + w - radius, y + h - radius, radius, radius, stroke=0, fill=1)
    # bottom-left
    c.rect(x, y, radius, radius, stroke=0, fill=1)


def draw_first_page_header(c, header_color, logo_path):
    # Convert cm to points
    fondo_w = HEADER_FIRST_W_CM * cm
    fondo_h = HEADER_FIRST_H_CM * cm
    fondo_x = 0
    fondo_y = PAGE_HEIGHT - fondo_h

    # Draw rounded rectangle (will mask to keep only lower-right corner rounded)
    radius = 14  # points; tweak if needed
    c.setFillColor(header_color)
    c.roundRect(fondo_x, fondo_y, fondo_w, fondo_h, radius, fill=1, stroke=0)
    # mask to leave only lower-right rounded
    _mask_round_except_lower_right(c, fondo_x, fondo_y, fondo_w, fondo_h, radius)

    # Bloque negro pegado a esquina superior izquierda, rectangular con lado derecho puntiagudo
    # We'll make it flush with top of header (pegado a la esquina superior izquierda de la página)
    negro_h = 3.5 * cm  # altura aproximada (ajustable)
    negro_w = 9.0 * cm  # ancho aproximado (ajustable)
    negro_x = 0
    negro_y = PAGE_HEIGHT - negro_h
    c.setFillColor(colors.black)
    path = c.beginPath()
    path.moveTo(negro_x, negro_y)
    path.lineTo(negro_x + negro_w - 1.2 * cm, negro_y)
    path.lineTo(negro_x + negro_w, negro_y + negro_h / 2.0)
    path.lineTo(negro_x + negro_w - 1.2 * cm, negro_y + negro_h)
    path.lineTo(negro_x, negro_y + negro_h)
    path.close()
    c.drawPath(path, fill=1, stroke=0)

    # Dibujar logo dentro del bloque negro (pegado arriba a la izquierda)
    if logo_path and os.path.exists(logo_path):
        try:
            # Fit logo inside the left area of the block
            logo_h = 1.4 * cm
            logo_w = 6.5 * cm
            logo_x = 0.4 * cm
            logo_y = PAGE_HEIGHT - logo_h - 1.0 * cm  # slightly down from top to look centered
            c.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            # fallback text logo
            _draw_logo_text_fallback(c, 0.4 * cm, PAGE_HEIGHT - 2.4 * cm, 6.5 * cm, 1.4 * cm)
    else:
        _draw_logo_text_fallback(c, 0.4 * cm, PAGE_HEIGHT - 2.4 * cm, 6.5 * cm, 1.4 * cm)

    # Franja negra pegada al borde inferior izquierdo del encabezado con texto
    franja_w = 10.5 * cm
    franja_h = 1.2 * cm
    franja_x = 0
    franja_y = fondo_y  # pegada al fondo del header
    c.setFillColor(colors.black)
    c.rect(franja_x, franja_y, franja_w, franja_h, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont(get_font_name('bold'), 10)
    c.drawString(0.7 * cm, franja_y + 0.28 * cm, "Nuestra línea de productos disponibles")

    return fondo_h


def _draw_logo_text_fallback(c, x, y, w, h):
    # simple fallback that paints a white rounded box with text
    c.setFillColor(colors.white)
    c.roundRect(x, y, w, h, h*0.12, fill=1, stroke=0)
    c.setFillColor(colors.black)
    font = get_font_name('bold')
    size = 12
    while stringWidth("INSUMOSPARA:TODO", font, size) > w - 4 and size > 6:
        size -= 1
    c.setFont(font, size)
    c.drawCentredString(x + w/2, y + h/2 - size*0.3, "INSUMOSPARA:TODO")


def draw_next_page_header(c, header_color, logo_path):
    fondo_w = HEADER_NEXT_W_CM * cm
    fondo_h = HEADER_NEXT_H_CM * cm
    fondo_x = 0
    fondo_y = PAGE_HEIGHT - fondo_h
    radius = 12
    c.setFillColor(header_color)
    c.roundRect(fondo_x, fondo_y, fondo_w, fondo_h, radius, fill=1, stroke=0)
    _mask_round_except_lower_right(c, fondo_x, fondo_y, fondo_w, fondo_h, radius)

    # logo 4.7cm x 1.0cm (pegado a la izquierda inside black block)
    # We'll draw a small black block left and place the logo in it
    logo_block_h = 1.0 * cm
    logo_block_w = 4.7 * cm
    logo_x = 0.4 * cm
    logo_y = PAGE_HEIGHT - logo_block_h - 0.8 * cm
    if logo_path and os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, logo_x, logo_y, width=logo_block_w, height=logo_block_h, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            _draw_logo_text_fallback(c, logo_x, logo_y, logo_block_w, logo_block_h)
    else:
        _draw_logo_text_fallback(c, logo_x, logo_y, logo_block_w, logo_block_h)

    return fondo_h


# ================================
# FUNCIONES DIBUJO TARJETAS
# ================================
def draw_code_background(c, x, y, card_width, card_height):
    code_width = 3.80 * cm
    code_height = 0.80 * cm
    code_x = x - 0.05 * cm
    code_y = y + card_height - code_height + 0.05 * cm

    if os.path.exists(CODE_BACKGROUND_PATH):
        try:
            c.drawImage(CODE_BACKGROUND_PATH, code_x, code_y,
                        width=code_width, height=code_height,
                        preserveAspectRatio=False, mask='auto')
            return code_x, code_y
        except:
            pass

    c.setFillColor(colors.black)
    c.rect(code_x, code_y, code_width, code_height, fill=True, stroke=False)
    return code_x, code_y


def draw_triangle(c, x, y, size, color):
    c.setFillColor(color)
    path = c.beginPath()
    path.moveTo(x, y)
    path.lineTo(x - size, y)
    path.lineTo(x, y + size)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def draw_product_card(c, x, y, producto, triangle_color):
    # Mantengo tu implementación original para que todo siga igual
    card_width = 6.0 * cm
    card_height = 6.0 * cm

    # Marco
    c.setStrokeColor(colors.black)
    c.rect(x, y, card_width, card_height)

    # Fondo negro para código
    code_x, code_y = draw_code_background(c, x, y, card_width, card_height)

    # Código
    c.setFillColor(colors.white)
    c.setFont(get_font_name('bold'), 13)
    text_x = code_x + (4 * cm / 2.4)
    text_y = code_y + (0.9 * cm / 2) - 0.2 * cm
    c.drawCentredString(text_x, text_y, producto.get("codigo", ""))
    c.setFillColor(colors.black)

    # Descripción
    descripcion_x = x + card_width / 2
    descripcion_y = y + card_height - 1.2 * cm
    ancho_max_descripcion = card_width - 1.2 * cm
    fuente_descripcion = get_font_name('bold')
    tamaño_descripcion = 9
    dibujar_texto_con_saltos(c, descripcion_x, descripcion_y,
                             producto.get("descripcion", ""), ancho_max_descripcion,
                             fuente_descripcion, tamaño_descripcion, max_lineas=3)

    # Imagen
    try:
        img = ImageReader(producto.get("imagen", ""))
        c.drawImage(img, x + 0.5 * cm, y + 1.4 * cm,
                    width=5.0 * cm, height=2.5 * cm,
                    preserveAspectRatio=True, mask='auto')
    except:
        c.setFont(get_font_name('regular'), 7)
        c.drawCentredString(x + card_width / 2, y + 2.5 * cm, "[Imagen no encontrada]")

    # Tabla de precios (mantengo tu lógica)
    headers = []
    values = []
    if pd.notna(producto.get("und")) and str(producto.get("und")).strip():
        headers.append("UND:")
        values.append(producto.get("und"))
    if pd.notna(producto.get("und_bulto")) and str(producto.get("und_bulto")).strip():
        headers.append("BULTO:")
        values.append(producto.get("und_bulto"))
    if pd.notna(producto.get("und_venta")) and str(producto.get("und_venta")).strip():
        headers.append("UND.VENTA:")
        values.append(producto.get("und_venta"))

    if headers:
        col_width = card_width / len(headers)
        table_top = y + 0.5 * cm
        c.setFont(get_font_name('bold'), 9)
        for i, h in enumerate(headers):
            c.drawCentredString(x + col_width * (i + 0.5), table_top, h)
        c.setFont(get_font_name('bold'), 9)
        for i, v in enumerate(values):
            c.drawCentredString(x + col_width * (i + 0.5), table_top - 0.4 * cm, str(v))

    # Triángulo decorativo con color elegido
    draw_triangle(c, x + card_width, y, 0.6 * cm, triangle_color)


# ================================
# FUNCION PRINCIPAL
# ================================
def generar_catalogo(header_color_hex):
    cargar_fuentes()
    logo_path = get_logo_path()

    # convertir hex a color reportlab
    try:
        header_color = colors.HexColor(header_color_hex)
    except Exception:
        header_color = colors.HexColor("#63B7FF")

    df = pd.read_excel(EXCEL_FILE)
    c = canvas.Canvas(OUTPUT_FILE, pagesize=A4)

    x_positions = [1.5 * cm, 8.0 * cm, 14.5 * cm]
    row_step = 6.5 * cm
    first_page_limit = 9
    other_pages_limit = 12

    # Primera página: encabezado generativo
    header_h = draw_first_page_header(c, header_color, logo_path)
    start_y = PAGE_HEIGHT - header_h - 6 * cm
    y = start_y
    col = 0
    products_on_page = 0
    page_limit = first_page_limit
    page_number = 1

    for _, row in df.iterrows():
        imagen_nombre = str(row.get("imagen", "")).strip()
        if imagen_nombre:
            imagen_path = os.path.join("imagenes", imagen_nombre)
        else:
            imagen_path = ""

        producto = {
            "codigo": str(row.get("codigo", "")),
            "descripcion": str(row.get("descripcion", "")),
            "und": row.get("und"),
            "und_bulto": row.get("und_bulto"),
            "und_venta": row.get("und_venta"),
            "imagen": imagen_path
        }

        draw_product_card(c, x_positions[col], y, producto, header_color)

        col += 1
        products_on_page += 1

        if col == 3:
            col = 0
            y -= row_step

        if products_on_page >= page_limit:
            c.showPage()
            page_number += 1
            # encabezado reducido para siguientes páginas
            header_h = draw_next_page_header(c, header_color, logo_path)
            start_y = PAGE_HEIGHT - header_h - PAGE2_START_Y_OFFSET
            y = start_y
            col = 0
            products_on_page = 0
            page_limit = other_pages_limit

    c.save()
    print(f"✅ Catálogo generado: {OUTPUT_FILE}")


# ================================
# INTERFAZ TK PARA TÍTULO Y COLOR HEX
# ================================
def ui_main():
    root = tk.Tk()
    root.title("Generador de Catálogo v2.0.2 (fix)")
    root.geometry("420x260")

    tk.Label(root, text="Título del catálogo (no se usa por ahora):", font=("Arial", 10)).pack(pady=6)
    title_entry = tk.Entry(root, font=("Arial", 11))
    title_entry.insert(0, "BOLSAS")
    title_entry.pack()

    tk.Label(root, text="Color del encabezado (HEX) o seleccionar:", font=("Arial", 10)).pack(pady=6)

    color_var = tk.StringVar(value="#63B7FF")
    color_entry = tk.Entry(root, textvariable=color_var, font=("Arial", 11))
    color_entry.pack()

    def pick_color():
        chosen = colorchooser.askcolor(title="Elige color")[1]
        if chosen:
            color_var.set(chosen)

    tk.Button(root, text="Selector de color", command=pick_color, width=20).pack(pady=6)

    def start():
        hex_color = color_var.get().strip()
        if not re.match(r"^#?[0-9A-Fa-f]{6}$", hex_color):
            messagebox.showerror("Error", "Formato HEX inválido. Usa por ejemplo: #3AA8FF")
            return
        if not hex_color.startswith("#"):
            hex_color = "#" + hex_color
        root.destroy()
        generar_catalogo(hex_color)

    tk.Button(root, text="Generar catálogo", command=start, bg="#4CAF50", fg="white", width=20).pack(pady=12)
    root.mainloop()


# ================================
# RUN
# ================================
if __name__ == "__main__":
    ui_main()
