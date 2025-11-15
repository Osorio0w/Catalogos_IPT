# =====================================
# productos.py - versión mejorada 1.6.4
# Integración con imagenes.py (reescalado automático)
# =====================================
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from encabezados import get_font_name
from imagenes import preparar_imagen  # 👈 nuevo import


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
    alineacion_x = x - (ancho_max / 2) + 0.1 * cm  # posición inicial a la izquierda del bloque
    for i, linea in enumerate(lineas):
        c.drawString(alineacion_x, y - i * espaciado, linea)


# -------------------------------
# COMPONENTES GRÁFICOS
# -------------------------------
def draw_code_background(c, x, y, card_width, card_height):
    """Franja negra superior con borde derecho puntiagudo."""
    c.setFillColor(colors.black)
    code_width = 3.6 * cm
    code_height = 0.8 * cm
    punta_longitud = 0.2 * cm

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

def formatear_numero(valor):
    """
    Convierte el valor a número y devuelve una cadena con 2 decimales y '$' al final.
    Si el valor no es numérico, lo devuelve tal cual.
    """
    try:
        numero = float(valor)
        return f"{numero:.2f}$"
    except:
        return str(valor)


# -------------------------------
# TARJETA DE PRODUCTO
# -------------------------------
# -------------------------------
# TARJETA DE PRODUCTO (versión mejorada de manejo de imagen)
# -------------------------------
def draw_product_card(c, x, y, producto, triangle_color):
    """Dibuja una tarjeta individual de producto (mejor manejo de imágenes)."""
    card_width = 6.0 * cm
    card_height = 6.0 * cm

    # Marco
    c.setStrokeColor(colors.black)
    c.rect(x, y, card_width, card_height)

    # Franja negra superior
    draw_code_background(c, x, y, card_width, card_height)

    # Código del producto
    c.setFillColor(colors.white)
    c.setFont(get_font_name('bold'), 13)
    c.drawCentredString(x + 1.4 * cm, y + card_height - 0.55 * cm, str(producto.get("codigo", "")))

    # --- Imagen del producto ---
    imagen_path = producto.get("imagen", "")
    if imagen_path:
        if imagen_path.lower().startswith("images/"):
            imagen_path = imagen_path.replace("images/", "imagenes/")

        try:
            # Preparamos la imagen (ImageReader + dimensiones en píxeles)
            img_reader, img_w_px, img_h_px = preparar_imagen(imagen_path)

            # Caja máxima disponible para la imagen (en puntos)
            max_w_pt = 5.0 * cm
            max_h_pt = 3.8 * cm

            # Relación ancho/alto de la imagen
            img_ratio = img_w_px / float(img_h_px) if img_h_px != 0 else 1.0
            box_ratio = max_w_pt / float(max_h_pt)

            # Calcular tamaño de dibujo manteniendo proporción (fit within box)
            if img_ratio > box_ratio:
                # La imagen es relativamente más ancha -> limitamos por ancho
                draw_w = max_w_pt
                draw_h = max_w_pt / img_ratio
            else:
                # La imagen es relativamente más alta -> limitamos por alto
                draw_h = max_h_pt
                draw_w = max_h_pt * img_ratio

            # Centrar la imagen dentro de la caja de 5.0 x 2.6 cm
            box_x = x + 0.5 * cm
            box_y = y + 1.7 * cm
            x_img = box_x + (max_w_pt - draw_w) / 2
            y_img = (box_y + (max_h_pt - draw_h) / 2) - 0.8 * cm

            # Dibujar la imagen con las dimensiones calculadas
            c.drawImage(
                img_reader,
                x_img,
                y_img,
                width=draw_w,
                height=draw_h,
                preserveAspectRatio=True,
                mask='auto'
            )

        except FileNotFoundError:
            c.setFillColor(colors.black)
            c.setFont(get_font_name('regular'), 7)
            c.drawCentredString(x + card_width / 2, y + 2.8 * cm, "[Imagen no encontrada]")
        except Exception as e:
            # Mensaje de fallback y log en consola
            print(f"⚠️ Error al preparar/dibujar imagen '{imagen_path}': {e}")
            c.setFillColor(colors.black)
            c.setFont(get_font_name('regular'), 7)
            c.drawCentredString(x + card_width / 2, y + 2.8 * cm, "[Error imagen]")

    else:
        c.setFont(get_font_name('regular'), 7)
        c.drawCentredString(x + card_width / 2, y + 2.8 * cm, "[Sin imagen]")

    # --- Descripción del producto ---
    descripcion_x = x + card_width / 2
    descripcion_y = y + card_height - 1.13 * cm
    c.setFillColor(colors.black)
    dibujar_texto_con_saltos(
        c,
        descripcion_x,
        descripcion_y,
        str(producto.get("descripcion", "")),
        card_width * 1,
        get_font_name('bold'),
        9,
        max_lineas=3
    )

    # --- Tabla de detalles ---
    tabla_y = y
    tabla_h = 0.6 * cm
    columnas = ["UND:", "BULTO:", "UND.VENTA:"]
    valores = [
        formatear_numero(producto.get("und", "")),
        formatear_numero(producto.get("bulto", "")),
        (producto.get("und_venta", ""))
    ]


    col_widths = [1.5 * cm, 1.5 * cm, 2.6 * cm]
    total_width = sum(col_widths)
    start_x = x + (card_width - total_width) / 2

    c.setFillColor(colors.whitesmoke)
    c.rect(start_x, tabla_y, total_width, tabla_h, fill=1, stroke=0)

    font_name = get_font_name('bold')
    c.setFont(font_name, 10)
    c.setFillColor(colors.black)

    offset = start_x
    for i, titulo in enumerate(columnas):
        c.drawCentredString((offset + col_widths[i] / 2) - 0.4 * cm, tabla_y + tabla_h + 0.05 * cm, titulo)
        offset += col_widths[i]

    offset = start_x
    for i, valor in enumerate(valores):
        c.drawCentredString((offset + col_widths[i] / 2) - 0.4 * cm, tabla_y + 0.18 * cm, valor)
        offset += col_widths[i]

    # Triángulo decorativo
    draw_triangle(c, x + card_width, y, 1.4 * cm, triangle_color)
