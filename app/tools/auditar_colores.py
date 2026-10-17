# -*- coding: utf-8 -*-
"""
auditar_colores.py — Comprueba que cada palabra de color tenga su color.

Lee las imágenes de app/www/assets/img-v2 y mira el color dominante (sin
contar el blanco del fondo ni el azul marino del contorno). Si no coincide
con el esperado, lo avisa.

Uso:
    python app/tools/auditar_colores.py
    python app/tools/auditar_colores.py --aplicar   # intercambia las parejas cruzadas
"""
import os
import sys

import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
V2 = os.path.join(APP, "www", "assets", "img-v2")
if not os.path.isdir(V2):
    V2 = os.path.join(APP, "www", "assets", "img")

# rangos de tono (grados) esperados para cada color
ESPERADO = {
    "red": [(0, 15), (340, 360)],
    "orange": [(15, 45)],
    "yellow": [(45, 70)],
    "green": [(70, 165)],
    "blue": [(190, 255)],
    "purple": [(255, 330)],
    "pink": [(320, 345)],
}

NOMBRES = [
    ("rojo", [(0, 15), (340, 360)]),
    ("naranja", [(15, 45)]),
    ("amarillo", [(45, 70)]),
    ("verde", [(70, 165)]),
    ("cian", [(165, 190)]),
    ("azul", [(190, 255)]),
    ("morado", [(255, 300)]),
    ("magenta", [(300, 340)]),
    ("rojo", [(340, 360)]),
]


def color_dominante(ruta):
    im = Image.open(ruta).convert("RGB").resize((128, 128), Image.BILINEAR)
    a = np.asarray(im).astype(np.float32) / 255.0
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    val = mx
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    # fuera blanco (muy claro y poco saturado) y fuera el azul marino del contorno
    util = (sat > 0.35) & (val > 0.18)
    # el contorno azul marino es oscuro: se descarta lo muy oscuro
    util &= val > 0.28
    if util.sum() < 50:
        return None, 0.0
    r, g, b = a[:, :, 0][util], a[:, :, 1][util], a[:, :, 2][util]
    mxu = np.maximum(np.maximum(r, g), b)
    mnu = np.minimum(np.minimum(r, g), b)
    d = mxu - mnu

    h = np.zeros_like(mxu)
    m = d > 1e-6
    idx = (mxu == r) & m
    h[idx] = ((g[idx] - b[idx]) / d[idx]) % 6
    idx = (mxu == g) & m
    h[idx] = ((b[idx] - r[idx]) / d[idx]) + 2
    idx = (mxu == b) & m
    h[idx] = ((r[idx] - g[idx]) / d[idx]) + 4
    h = (h * 60) % 360

    hist, bordes = np.histogram(h, bins=36, range=(0, 360))
    i = int(np.argmax(hist))
    centro = (bordes[i] + bordes[i + 1]) / 2
    return centro, hist[i] / max(1, hist.sum())


def nombre(h):
    if h is None:
        return "sin color"
    for nom, rangos in NOMBRES:
        for a, b in rangos:
            if a <= h < b:
                return nom
    return "?"


def encaja(palabra, h):
    if h is None:
        return False
    for a, b in ESPERADO.get(palabra, []):
        if a <= h < b:
            return True
    return False


def main():
    aplicar = "--aplicar" in sys.argv
    filas = []
    for palabra in sorted(ESPERADO):
        ruta = os.path.join(V2, palabra + ".webp")
        if not os.path.exists(ruta):
            filas.append((palabra, "falta", None, False))
            continue
        h, peso = color_dominante(ruta)
        filas.append((palabra, nombre(h), h, encaja(palabra, h)))

    print("%-10s %-10s %-8s %s" % ("palabra", "sale", "tono", "estado"))
    malas = []
    for palabra, nom, h, bien in filas:
        print("%-10s %-10s %-8s %s" % (
            palabra, nom, ("%.0f" % h) if h is not None else "-",
            "OK" if bien else "REVISAR"))
        if not bien:
            malas.append(palabra)

    if not malas:
        print("\ntodos los colores coinciden")
        return

    print("\ncon problema: %s" % ", ".join(malas))
    # propuesta de intercambio: si el color dominante de A es el que espera B
    if len(malas) >= 2:
        print("\nposibles intercambios:")
        for i in range(len(malas)):
            for j in range(i + 1, len(malas)):
                a, b = malas[i], malas[j]
                rutaA = os.path.join(V2, a + ".webp")
                rutaB = os.path.join(V2, b + ".webp")
                ha, _ = color_dominante(rutaA)
                hb, _ = color_dominante(rutaB)
                if encaja(b, ha) and encaja(a, hb):
                    print("   %s <-> %s" % (a, b))
                    if aplicar:
                        tmp = rutaA + ".tmp"
                        os.replace(rutaA, tmp)
                        os.replace(rutaB, rutaA)
                        os.replace(tmp, rutaB)
                        print("      intercambiadas")


if __name__ == "__main__":
    main()
