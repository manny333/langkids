# -*- coding: utf-8 -*-
"""
hojas_v2.py — Hojas de revisión de la tanda nueva (con el nombre debajo).

Genera PNGs en docs/revision/ con las ilustraciones de app/www/assets/img-v2,
cada una con su palabra escrita, para poder revisarlas de un vistazo y cazar
imágenes cruzadas o mal recortadas.

Uso:
    python app/tools/hojas_v2.py            # todas
    python app/tools/hojas_v2.py --desde 0 --hasta 60
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
V2 = os.path.join(APP, "www", "assets", "img-v2")
if not os.path.isdir(V2):
    V2 = os.path.join(APP, "www", "assets", "img")
SALIDA = os.path.join(RAIZ, "docs", "revision")

COLS, FILAS = 6, 5
CELDA = 210
ETIQUETA = 30


def fuente(tam):
    for ruta in (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, tam)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    os.makedirs(SALIDA, exist_ok=True)
    palabras = sorted(f[:-5] for f in os.listdir(V2) if f.endswith(".webp"))
    desde = int(sys.argv[sys.argv.index("--desde") + 1]) if "--desde" in sys.argv else 0
    hasta = int(sys.argv[sys.argv.index("--hasta") + 1]) if "--hasta" in sys.argv else len(palabras)
    palabras = palabras[desde:hasta]

    por_hoja = COLS * FILAS
    fuente_txt = fuente(18)
    hojas = 0
    for inicio in range(0, len(palabras), por_hoja):
        grupo = palabras[inicio:inicio + por_hoja]
        ancho = COLS * CELDA
        alto = FILAS * (CELDA + ETIQUETA)
        hoja = Image.new("RGB", (ancho, alto), (250, 247, 240))
        dib = ImageDraw.Draw(hoja)
        for i, palabra in enumerate(grupo):
            f, c = divmod(i, COLS)
            x = c * CELDA
            y = f * (CELDA + ETIQUETA)
            try:
                im = Image.open(os.path.join(V2, palabra + ".webp")).convert("RGB")
            except Exception:
                continue
            im.thumbnail((CELDA - 16, CELDA - 16), Image.LANCZOS)
            hoja.paste(im, (x + (CELDA - im.width) // 2, y + (CELDA - im.height) // 2))
            tw = dib.textlength(palabra, font=fuente_txt)
            dib.text((x + (CELDA - tw) / 2, y + CELDA + 4), palabra,
                     fill=(43, 45, 66), font=fuente_txt)
        n = (desde + inicio) // por_hoja + 1
        ruta = os.path.join(SALIDA, "v2-%02d.png" % n)
        hoja.save(ruta, "PNG")
        hojas += 1
        print("hoja %s  (%d palabras)" % (ruta, len(grupo)))
    print("\n%d hojas generadas en %s" % (hojas, SALIDA))


if __name__ == "__main__":
    main()
