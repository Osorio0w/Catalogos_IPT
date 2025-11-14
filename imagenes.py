# =====================================
# imagenes.py - versión 1.0.0
# Módulo para manejo y reescalado de imágenes
# =====================================
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os

# -------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------
def preparar_imagen(ruta, ancho_cm, alto_cm):
    """
    Abre una imagen desde 'ruta', la redimensiona a las dimensiones
    indicadas (en centímetros) manteniendo su proporción, y devuelve
    un objeto ImageReader listo para reportlab.
    """
    from reportlab.lib.units import cm

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Imagen no encontrada: {ruta}")

    # Abre la imagen con Pillow
    with Image.open(ruta) as img:
        img = img.convert("RGB")

        # Tamaño en píxeles equivalente al tamaño en cm
        ancho_px = int(ancho_cm * 28.35)  # 1 cm = 28.35 puntos = ~28 px
        alto_px = int(alto_cm * 28.35)

        # Redimensiona manteniendo proporciones
        img.thumbnail((ancho_px, alto_px), Image.LANCZOS)

        # Pasa la imagen a un buffer de memoria
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)

    return ImageReader(buffer)
