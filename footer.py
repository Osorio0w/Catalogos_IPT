# =====================================
# footer.py
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
INSTAGRAM_ICON = "icon_instagram.png"  # Ícono en la carpeta raíz del programa
CANVA_SANS_BOLD = "fuentes/CanvaSans-Bold.ttf"
CANVA_SANS_REGULAR = "fuentes/CanvaSans-Regular.ttf"

# Tamaño del footer
FOOTER_WIDTH = 13 * cm
FOOTER_HEIGHT = 2 * cm


# -------------------------------
# FUENTES
# -------------------------------
def cargar_fuentes_footer():
    """Carga las fuentes necesarias si están disponibles."""
    try:
        os.makedirs("fuentes", exist_ok=True)
        if os.path.exists(CANVA_SANS_REGULAR):
            pdfmetrics.registerFont(TTFont('CanvaSans', CANVA_SANS_REGULAR))
        if os.path.exists(CANVA_SANS_BOLD):
            pdfmetrics.registerFont(TTFont('CanvaSans-Bold', CANVA_SANS_BOLD))
    except Exception as e:
        print(f"⚠️ Error al cargar fuentes (footer): {e}")


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
# FOOTER
# -------------------------------
def draw_footer(c, footer_color=colors.black):
    """
    Dibuja un footer en la parte inferior de la página:
    - Bloque de color personalizado (13x2 cm), pegado al borde inferior izquierdo.
    - Ícono de Instagram centrado junto con el texto '@insumosparatodo'.
    """
    cargar_fuentes_footer()

    # Posición del footer (pegado a la esquina inferior izquierda)
    footer_x = 0 * cm
    footer_y = 0 * cm

    # Fondo del footer (color del encabezado)
    c.setFillColor(footer_color)
    c.rect(footer_x, footer_y, FOOTER_WIDTH, FOOTER_HEIGHT, fill=1, stroke=0)

    # Dimensiones del ícono
    icon_size = 1.2 * cm
    spacing = 0.5 * cm  # espacio entre el ícono y el texto

    # Texto
    c.setFont(get_font_name('bold'), 14)
    text = "@insumosparatodo"
    text_width = pdfmetrics.stringWidth(text, get_font_name('bold'), 14)

    # Ancho total (icono + espacio + texto)
    total_width = icon_size + spacing + text_width

    # Posicionar todo el conjunto centrado horizontalmente dentro del footer
    start_x = footer_x + (FOOTER_WIDTH - total_width) / 2
    icon_x = start_x
    text_x = icon_x + icon_size + spacing

    # Centrar verticalmente el ícono y el texto
    icon_y = footer_y + (FOOTER_HEIGHT - icon_size) / 2
    text_y = footer_y + (FOOTER_HEIGHT / 2) - 0.35 * cm

    # Dibujar el ícono
    if os.path.exists(INSTAGRAM_ICON):
        try:
            img = ImageReader(INSTAGRAM_ICON)
            c.drawImage(img, icon_x, icon_y, width=icon_size, height=icon_size,
                        preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"⚠️ Error al cargar ícono Instagram: {e}")
    else:
        c.setFillColor(colors.white)
        c.setFont(get_font_name('bold'), 10)
        c.drawString(icon_x, icon_y + 0.3 * cm, "[IG]")

    # Dibujar el texto
    c.setFillColor(colors.white)
    c.drawString(text_x, text_y, text)
