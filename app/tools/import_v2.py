# -*- coding: utf-8 -*-
"""
import_v2.py — Prepara la tanda NUEVA de ilustraciones (img-ia-v2).

Toma las imágenes generadas una a una con el plugin de imagen, las recorta al
dibujo, las centra en un cuadrado de 512x512 y las guarda en
app/www/assets/img-v2/, además del manifiesto que usa la app para saber qué
palabras tienen versión nueva.

Uso:
    python app/tools/import_v2.py            # simulación
    python app/tools/import_v2.py --aplicar  # escribe imágenes y manifiesto
"""
import json
import os
import re
import sys
import unicodedata

import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
ORIGEN = os.path.join(RAIZ, "img-ia-v2")
DESTINO = os.path.join(APP, "www", "assets", "img-v2")
# Si la tanda ya se consolidó, se escribe directamente en assets/img
if not os.path.isdir(DESTINO):
    DESTINO = os.path.join(APP, "www", "assets", "img")
MANIFIESTO = os.path.join(APP, "www", "content", "imagenes-v2.js")

LADO = 512
CALIDAD = 88
MARGEN = 0.08


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = t.lower().replace("'", "").replace("’", "")
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def palabras_del_curso():
    ruta = os.path.join(APP, "content", "lessons.json")
    d = json.load(open(ruta, encoding="utf-8"))
    vistas = {}
    for nivel in d["levels"]:
        for unidad in nivel["units"]:
            for w in unidad["words"]:
                vistas[slug(w["en"])] = w["en"]
    return vistas


def caja_dibujo(im):
    """Caja del objeto: ignora el blanco del fondo."""
    a = np.array(im.convert("RGB")).astype(np.int16)
    mx, mn = a.max(axis=2), a.min(axis=2)
    luz = a.mean(axis=2)
    tinta = ((mx - mn) > 30) | (luz < 200)
    ys, xs = np.where(tinta)
    if len(xs) < 40:
        return None
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def preparar(ruta):
    im = Image.open(ruta).convert("RGB")
    caja = caja_dibujo(im)
    if caja is None:
        return None
    x0, y0, x1, y1 = caja
    recorte = im.crop(caja)
    ancho, alto = recorte.size
    lado = int(max(ancho, alto) * (1 + MARGEN * 2))
    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    lienzo.paste(recorte, ((lado - ancho) // 2, (lado - alto) // 2))
    return lienzo.resize((LADO, LADO), Image.LANCZOS)


def main():
    aplicar = "--aplicar" in sys.argv
    palabras = palabras_del_curso()
    if not os.path.isdir(ORIGEN):
        print("no existe la carpeta %s" % ORIGEN)
        return

    archivos = sorted(f for f in os.listdir(ORIGEN)
                      if os.path.isfile(os.path.join(ORIGEN, f))
                      and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
    listas, sueltas = {}, []
    for f in archivos:
        s = slug(os.path.splitext(f)[0])
        if s in palabras or s in ("goodbye", "bye-bye"):
            listas[s] = os.path.join(ORIGEN, f)
        else:
            sueltas.append(f)

    print("imágenes en la carpeta : %d" % len(archivos))
    print("palabras del curso     : %d" % len(palabras))
    print("emparejadas            : %d" % len(listas))
    print("sin palabra en el curso: %d" % len(sueltas))
    if sueltas:
        print("   " + ", ".join(sueltas[:12]) + (" ..." if len(sueltas) > 12 else ""))

    if not aplicar:
        print("\n(simulación · usa --aplicar)")
        return

    os.makedirs(DESTINO, exist_ok=True)
    hechas = []
    for s, ruta in sorted(listas.items()):
        img = preparar(ruta)
        if img is None:
            print("  sin dibujo detectable:", s)
            continue
        img.save(os.path.join(DESTINO, s + ".webp"), "WEBP", quality=CALIDAD, method=6)
        hechas.append(s)

    contenido = ("// Generado por app/tools/import_v2.py — no editar a mano.\n"
                 "window.LANGKIDS_IMG_V2 = %s;\n" % json.dumps(sorted(hechas)))
    open(MANIFIESTO, "w", encoding="utf-8").write(contenido)

    print("\nescritas %d imágenes en %s" % (len(hechas), DESTINO))
    print("manifiesto: %d palabras con versión nueva" % len(hechas))


def _revisar_colores():
    """Tras importar, deja los colores en su sitio (por si venían cruzados)."""
    try:
        import subprocess
        aqui = os.path.dirname(os.path.abspath(__file__))
        subprocess.run([sys.executable, os.path.join(aqui, "auditar_colores.py"), "--aplicar"],
                       check=False)
    except Exception:
        pass


if __name__ == "__main__":
    main()
    _revisar_colores()
