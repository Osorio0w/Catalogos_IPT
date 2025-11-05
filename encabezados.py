# =====================================
# encabezados.py
# =====================================
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -------------------------------
# CONFIG
# -------------------------------
LOGO_FILE_NAMES = ["logo2.png", "insumosparatodo_logo.png"]
CANVA_SANS_BOLD = "fuentes/CanvaSans-Bold.ttf"
CANVA_SANS_REGULAR = "fuentes/CanvaSans-Regular.ttf"

PAGE_WIDTH, PAGE_HEIGHT = (595.27, 841.89)  # A4 en puntos
FIRST_HEADER_HEIGHT = 7.3 * cm
OTHER_HEADER_HEIGHT = 2 * cm


# -------------------------------
# FUENTES
# -------------------------------
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


# -------------------------------
# LOGO
# -------------------------------
def get_logo_path():
    for name in LOGO_FILE_NAMES:
        if os.path.exists(name):
            return name
    return ""


def draw_logo_block(c, x, y, h, logo_path):
    """
    Dibuja el bloque negro con el logo de IPT, pegado en la esquina superior izquierda.
    El bloque es rectangular con un borde derecho puntiagudo.
    """
    block_h = h
    block_w = h * 1.3

    # Coordenadas de la forma (rectángulo con punta)
    pts = [
        (x, y),
        (x + block_w * 0.8, y),
        (x + block_w, y + block_h / 2.0),
        (x + block_w * 0.8, y + block_h),
        (x, y + block_h),
    ]

    # Dibujo del bloque negro
    c.setFillColor(colors.black)
    path = c.beginPath()
    path.moveTo(pts[0][0], pts[0][1])
    for px, py in pts[1:]:
        path.lineTo(px, py)
    path.close()
    c.drawPath(path, fill=1, stroke=0)

    # Logo interno
    margin = 0.01 * block_h
    inner_x = x + margin - 0.1 * cm
    inner_y = y + margin
    inner_w = block_w * 0.95 - 0.9 * margin
    inner_h = block_h - 2 * margin

    if logo_path and os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, inner_x, inner_y,
                        width=inner_w, height=inner_h,
                        preserveAspectRatio=True, mask='auto')
            return
        except Exception:
            pass

    # Fallback (texto si no hay logo)
    c.setFillColor(colors.white)
    c.setFont(get_font_name('bold'), 12)
    c.drawCentredString(inner_x + inner_w / 2, inner_y + inner_h / 2 - 4, "INSUMOSPARA:TODO")


# -------------------------------
# ENCABEZADOS
# -------------------------------
def draw_header_page1(c, category_text, header_color, logo_path):
    """
    Dibuja el encabezado de la primera página:
    - Fondo recto perfectamente alineado.
    - Solo la esquina INFERIOR DERECHA queda redondeada.
    - Bloque negro con logo pegado en la esquina superior izquierda,
      y franja negra con el texto "Nuestra línea de productos disponibles".
    """
    header_h = FIRST_HEADER_HEIGHT
    fondo_w = 17.6 * cm  # ancho fijo (tal como pediste)
    fondo_h = header_h + 1 * cm
    fondo_x = 1.3 * cm
    fondo_y = PAGE_HEIGHT - fondo_h + 1 * cm

    # radio en puntos para la esquina redondeada (ajustable)
    radius = 20  # puedes aumentar o disminuir (puntos)

    # 1) Dibujamos un rounded rect completo (todos los bordes redondeados)
    c.setFillColor(header_color)
    c.roundRect(fondo_x, fondo_y, fondo_w, fondo_h, radius, fill=1, stroke=0)

    # 2) "Cuadramos" las tres esquinas que NO deben quedar redondeadas
    #    (superior-izquierda, superior-derecha, inferior-izquierda)
    #    Dibujamos rectángulos del mismo color encima del roundRect para revertir
    #    el redondeado en esas esquinas. Esto asegura que el bloque quede recto
    #    excepto en la esquina inferior derecha.
    # esquina superior-izq
    c.rect(fondo_x, PAGE_HEIGHT - radius, radius, radius, fill=1, stroke=0)
    # esquina superior-der
    c.rect(fondo_x + fondo_w - radius, PAGE_HEIGHT - radius, radius, radius, fill=1, stroke=0)
    # esquina inferior-izq
    c.rect(fondo_x, fondo_y, radius, radius, fill=1, stroke=0)

    # (Opcional) si tu página es más ancha que fondo_w y quieres que el bloque
    # esté alineado a la izquierda, dejamos fondo_w como ancho fijo.
    # Si prefieres que el bloque se extienda hasta el borde derecho de la página,
    # cambia fondo_w por PAGE_WIDTH.

    # 3) Bloque negro con el logo, pegado a la esquina superior izquierda
    #    (tal y como habíamos definido en draw_logo_block)
    draw_logo_block(c, 0 * cm, fondo_y + 3.7 * cm, (fondo_h / 2), logo_path)

    # 4) Títulos (CATÁLOGO + categoría grande)
    c.setFillColor(colors.white)
    c.setFont(get_font_name('bold'), 30)
    c.drawCentredString(fondo_x + fondo_w / 2, PAGE_HEIGHT - fondo_h / 2 + 1.8 * cm, "CATÁLOGO")
    c.setFont(get_font_name('bold'), 64)
    c.drawCentredString(fondo_x + fondo_w / 2, PAGE_HEIGHT - fondo_h / 2 - 0.6 * cm, category_text.upper())

    # 5) Franja negra pegada al borde inferior izquierdo del encabezado
    franja_w = 9 * cm
    franja_h = 0.9 * cm
    franja_x = fondo_x
    franja_y = fondo_y
    c.setFillColor(colors.black)
    c.rect(franja_x, franja_y, franja_w, franja_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(get_font_name('CanvaSans'), 13)
    c.drawString(fondo_x + 0.2 * cm, franja_y + 0.28 * cm, "Nuestra línea de productos disponibles")

    return fondo_h

def draw_header_pageN(c, category_text, header_color, logo_path):
    """
    Encabezado de páginas siguientes:
    - Franja del color del usuario (no ocupa toda la página, deja 4 cm antes del borde derecho).
    - Solo la esquina inferior derecha está redondeada.
    - Bloque negro con el logo, pegado a la esquina superior izquierda y más ancho.
    - Punta más suave en el borde derecho.
    - Logo más grande dentro del bloque.
    - Texto centrado con el nombre de la categoría.
    """
    h = OTHER_HEADER_HEIGHT

    # -----------------------------
    # Fondo del encabezado
    # -----------------------------
    fondo_margin_right = 4 * cm
    fondo_w = PAGE_WIDTH - fondo_margin_right
    fondo_x = 1.8 * cm
    fondo_y = PAGE_HEIGHT - h
    radius = 20

    c.setFillColor(header_color)
    c.roundRect(fondo_x, fondo_y, fondo_w, h, radius, fill=1, stroke=0)

    # Recuadrar las esquinas que no deben ser redondeadas
    c.rect(fondo_x, PAGE_HEIGHT - radius, radius, radius, fill=1, stroke=0)
    c.rect(fondo_x + fondo_w - radius, PAGE_HEIGHT - radius, radius, radius, fill=1, stroke=0)
    c.rect(fondo_x, fondo_y, radius, radius, fill=1, stroke=0)

    # -----------------------------
    # Bloque negro con el logo
    # -----------------------------
    block_h = h
    block_w = block_h * 2.7
    block_x = 0
    block_y = PAGE_HEIGHT - block_h

    # 🔸 Punta menos aguda (0.9 → más corta)
    pts = [
        (block_x, block_y),
        (block_x + block_w * 0.85, block_y),
        (block_x + block_w * 0.95, block_y + (block_h / 2.0) + 1),  # <-- punta menos aguda
        (block_x + block_w * 0.85, block_y + block_h),
        (block_x, block_y + block_h),
    ]
    c.setFillColor(colors.black)
    path = c.beginPath()
    path.moveTo(pts[0][0], pts[0][1])
    for px, py in pts[1:]:
        path.lineTo(px, py)
    path.close()
    c.drawPath(path, fill=1, stroke=0)

    # -----------------------------
    # Logo dentro del bloque
    # -----------------------------
    margin = 0.05 * block_h
    inner_x = block_x + margin + 0.2 * cm
    inner_y = block_y + margin
    inner_w = block_w * 0.8  # ligeramente más grande
    inner_h = block_h - margin * 1.5

    if logo_path and os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, inner_x, inner_y,
                        width=inner_w, height=inner_h,
                        preserveAspectRatio=True, mask='auto')
        except:
            pass
    else:
        c.setFillColor(colors.white)
        c.setFont(get_font_name('bold'), 12)
        c.drawCentredString(inner_x + inner_w / 2, inner_y + inner_h / 2 - 4, "INSUMOSPARA:TODO")

    # -----------------------------
    # Texto centrado (categoría)
    # -----------------------------
    c.setFillColor(colors.white)
    c.setFont(get_font_name('bold'), 45)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - h / 2 - 15, category_text.upper())

    return h