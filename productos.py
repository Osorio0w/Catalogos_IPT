# =====================================
# productos.py - versión mejorada 1.6.0
# =====================================
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from encabezados import get_font_name


# -------------------------------
# UTILIDADES DE TEXTO
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


# -------------------------------
# COMPONENTES GRÁFICOS
# -------------------------------
def draw_code_background(c, x, y, card_width, card_height):
    """Franja negra superior con borde derecho puntiagudo."""
    c.setFillColor(colors.black)
    code_width = 3.6 * cm
    code_height = 0.8 * cm
    punta_longitud = 0.2 * cm  # tamaño de la punta

    base_y = y + card_height - code_height
    base_x = x

    pts = [
        (base_x, base_y),
        (base_x + code_width, base_y),
        (base_x + code_width + punta_longitud, base_y + code_height / 2),
        (base_x + code_width, base_y + code_height),
        (base_x, base_y + code_height),
    ]

    path = c.beginPath()
    path.moveTo(pts[0][0], pts[0][1])
    for px, py in pts[1:]:
        path.lineTo(px, py)
    path.close()

    c.drawPath(path, fill=1, stroke=0)


def draw_triangle(c, x, y, size, color):
    """Triángulo decorativo en la esquina inferior derecha."""
    c.setFillColor(color)
    path = c.beginPath()
    path.moveTo(x, y)
    path.lineTo(x - size, y)
    path.lineTo(x, y + size)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


# -------------------------------
# TARJETA DE PRODUCTO
# -------------------------------
def draw_product_card(c, x, y, producto, triangle_color):
    """Dibuja una tarjeta individual de producto."""
    card_width = 6.0 * cm
    card_height = 6.0 * cm

    # 1️⃣ Marco del producto
    c.setStrokeColor(colors.black)
    c.rect(x, y, card_width, card_height)

    # 2️⃣ Franja negra del código
    draw_code_background(c, x, y, card_width, card_height)

    # 3️⃣ Texto del código
    c.setFillColor(colors.white)
    c.setFont(get_font_name('bold'), 13)
    c.drawCentredString(x + 1.4 * cm, y + card_height - 0.55 * cm, producto.get("codigo", ""))

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

    # 5️⃣ Descripción
    descripcion_x = x + card_width / 2
    descripcion_y = y + card_height - 1.1 * cm
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

    # 6️⃣ Tabla de detalles (sin bordes visibles)
    tabla_y = y
    tabla_h = 0.6 * cm
    columnas = ["UND", "BULTO", "UND.VENTA"]
    valores = [
        producto.get("und", ""),
        producto.get("bulto", ""),
        producto.get("und_venta", "")
    ]
    col_width = card_width / 3

    # Fondo (gris claro sin bordes)
    c.setFillColor(colors.whitesmoke)
    c.rect(x, tabla_y, card_width, tabla_h, fill=1, stroke=0)

    # Texto: títulos y valores (fuente CanvaSans-Bold, tamaño 10)
    font_name = get_font_name('bold')
    c.setFont(font_name, 10)
    c.setFillColor(colors.black)

    # Títulos
    for i, titulo in enumerate(columnas):
        c.drawCentredString(x + (i * col_width) + col_width / 2,
                            tabla_y + tabla_h + 0.25 * cm,
                            titulo)

    # Valores
    for i, valor in enumerate(valores):
        c.drawCentredString(x + (i * col_width) + col_width / 2,
                            tabla_y + 0.18 * cm,
                            valor)

    # 7️⃣ Triángulo decorativo
    draw_triangle(c, x + card_width, y, 1.4 * cm, triangle_color)
