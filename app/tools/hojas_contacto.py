# -*- coding: utf-8 -*-
"""
hojas_contacto.py — Genera hojas de revisión con todas las ilustraciones.

Cada hoja muestra 25 imágenes en rejilla, con su palabra debajo, para poder
revisarlas de un vistazo.

Uso:
    python app/tools/hojas_contacto.py
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
IMG = os.path.join(APP, "www", "assets", "img")
SALIDA = os.path.join(RAIZ, "docs", "revision")

CELDA = 200
COLS, FILAS = 5, 5
MARGEN = 12
PIE = 26
FONDO = (250, 247, 240)
TINTA = (43, 45, 66)


def fuente(tam):
    for ruta in (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf",
                 r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, tam)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    os.makedirs(SALIDA, exist_ok=True)
    palabras = sorted(f[:-5] for f in os.listdir(IMG) if f.endswith(".webp"))
    f_txt = fuente(15)
    f_tit = fuente(20)

    por_hoja = COLS * FILAS
    hojas = [palabras[i:i + por_hoja] for i in range(0, len(palabras), por_hoja)]
    print("imágenes: %d · hojas: %d" % (len(palabras), len(hojas)))

    for n, grupo in enumerate(hojas, 1):
        ancho = COLS * CELDA + MARGEN * (COLS + 1)
        alto = FILAS * (CELDA + PIE) + MARGEN * (FILAS + 1) + 34
        hoja = Image.new("RGB", (ancho, alto), FONDO)
        d = ImageDraw.Draw(hoja)
        d.text((MARGEN, 6), "Hoja %d de %d · %d imágenes" % (n, len(hojas), len(palabras)),
               font=f_tit, fill=TINTA)
        for i, palabra in enumerate(grupo):
            cx = MARGEN + (i % COLS) * (CELDA + MARGEN)
            cy = 34 + MARGEN + (i // COLS) * (CELDA + PIE + MARGEN)
            d.rectangle([cx, cy, cx + CELDA, cy + CELDA], fill=(255, 255, 255),
                        outline=(224, 216, 200), width=2)
            try:
                im = Image.open(os.path.join(IMG, palabra + ".webp")).convert("RGB")
                im.thumbnail((CELDA - 8, CELDA - 8), Image.LANCZOS)
                hoja.paste(im, (cx + (CELDA - im.width) // 2, cy + (CELDA - im.height) // 2))
            except Exception as e:
                d.text((cx + 6, cy + CELDA // 2), "ERROR", font=f_txt, fill=(200, 0, 0))
            d.text((cx + 4, cy + CELDA + 3), palabra[:26], font=f_txt, fill=TINTA)
        ruta = os.path.join(SALIDA, "r%02d.png" % n)
        hoja.save(ruta)
    print("hojas en %s" % SALIDA)


if __name__ == "__main__":
    main()
