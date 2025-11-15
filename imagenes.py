# =====================================
# imagenes.py - versión 1.1.0 (mejorada)
# Manejo y reescalado de imágenes (sin pérdida innecesaria)
# =====================================
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os

# -------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------
def preparar_imagen(ruta, max_long_side_px=2500):
    """
    Prepara una imagen para ReportLab y devuelve:
      - image_reader: ImageReader listo para c.drawImage(...)
      - img_w_px, img_h_px: tamaño original (o reducido) en píxeles

    Estrategia:
    - Si la imagen existe y su lado más largo es <= max_long_side_px -> devolvemos ImageReader(file_path)
      (no re-encodeamos ni comprimimos; esto preserva la calidad original).
    - Si es muy grande (> max_long_side_px) la redimensionamos proporcionalmente
      hasta max_long_side_px en su lado mayor usando LANCZOS, la guardamos en memoria como PNG
      (sin pérdida por compresión JPEG) y devolvemos un ImageReader desde ese buffer.
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Imagen no encontrada: {ruta}")

    # Obtener tamaño real con Pillow
    with Image.open(ruta) as pil_img:
        pil_img = pil_img.convert("RGB")
        w_px, h_px = pil_img.size
        long_side = max(w_px, h_px)

        # Si la imagen no es excesivamente grande, devolver ImageReader directo (sin re-encode)
        if long_side <= max_long_side_px:
            # ImageReader puede abrir desde la ruta directamente (evita recomprimir)
            return ImageReader(ruta), w_px, h_px

        # Si es demasiado grande, redimensionamos manteniendo proporción
        ratio = max_long_side_px / float(long_side)
        new_w = int(w_px * ratio)
        new_h = int(h_px * ratio)

        pil_resized = pil_img.resize((new_w, new_h), Image.LANCZOS)

        # Guardamos a buffer en PNG (mejor calidad y sin artefactos JPEG)
        buffer = io.BytesIO()
        pil_resized.save(buffer, format="PNG")
        buffer.seek(0)

        return ImageReader(buffer), new_w, new_h
