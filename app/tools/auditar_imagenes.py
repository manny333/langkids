# -*- coding: utf-8 -*-
"""
auditar_imagenes.py — Revisa cada ilustración de la app y detecta defectos.

Comprueba cuatro cosas en cada imagen de app/www/assets/img:

  * MOCHA      el dibujo toca el borde del lienzo (viene cortado)
  * TEXTO      hay manchas pequeñas fuera del dibujo (etiquetas de la hoja)
  * DESCENTRADA el dibujo no está en el centro del lienzo
  * PEQUEÑA    el dibujo ocupa poco espacio (< 62 % del lado)

Uso:
    python app/tools/auditar_imagenes.py           # informe por pantalla
    python app/tools/auditar_imagenes.py --json    # además, docs/auditoria.json
"""
import json
import os
import sys

import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
sys.path.insert(0, AQUI)
import import_ia_images as ia

IMG = os.path.join(APP, "www", "assets", "img")
SALIDA = os.path.join(RAIZ, "docs", "auditoria.json")

UMBRAL_DESPLAZAMIENTO = 0.10   # 10 % del lado
UMBRAL_PEQUENA = 0.62
UMBRAL_TEXTO = 45              # área mínima de una mancha "sospechosa"


def analizar(ruta):
    im = Image.open(ruta).convert("RGB")
    W, H = im.size
    mask = ia.mascara_tinta(im)
    piezas = ia.etiquetar(mask)
    if not piezas:
        return {"estado": ["VACIA"], "detalle": "sin dibujo"}

    px0, py0, px1, py1 = ia.agrupar_dibujo(im)
    principal = (px0, py0, px1, py1, 0)

    # --- cortada: el dibujo toca el borde del lienzo
    margen = 3
    mocha = px0 <= margen or py0 <= margen or px1 >= W - margen or py1 >= H - margen

    # --- centrada
    cx, cy = (px0 + px1) / 2.0, (py0 + py1) / 2.0
    desx = abs(cx - W / 2.0) / (W / 2.0)
    desy = abs(cy - H / 2.0) / (H / 2.0)

    # --- tamaño
    relleno = max(px1 - px0, py1 - py0) / float(W)

    # --- manchas sueltas fuera del dibujo (texto de la hoja)
    sueltas = 0
    for c in piezas:
        if c is principal or c[4] < UMBRAL_TEXTO:
            continue
        x0, y0, x1, y1, _ = c
        dentro = not (x1 < px0 or x0 > px1 or y1 < py0 or y0 > py1)
        if not dentro:
            sueltas += 1

    estado = []
    if mocha:
        estado.append("MOCHA")
    if sueltas:
        estado.append("TEXTO")
    if desx > UMBRAL_DESPLAZAMIENTO or desy > UMBRAL_DESPLAZAMIENTO:
        estado.append("DESCENTRADA")
    if relleno < UMBRAL_PEQUENA:
        estado.append("PEQUENA")

    return {
        "estado": estado or ["OK"],
        "relleno": round(float(relleno), 3),
        "desx": round(float(desx), 3),
        "desy": round(float(desy), 3),
        "sueltas": sueltas,
        "caja": [int(px0), int(py0), int(px1), int(py1)],
    }


def main():
    archivos = sorted(f for f in os.listdir(IMG) if f.endswith(".webp"))
    resultados = {}
    for f in archivos:
        resultados[f[:-5]] = analizar(os.path.join(IMG, f))

    cuenta = {}
    for v in resultados.values():
        for e in v["estado"]:
            cuenta[e] = cuenta.get(e, 0) + 1

    print("imágenes revisadas: %d" % len(archivos))
    print()
    for k in ("OK", "MOCHA", "TEXTO", "DESCENTRADA", "PEQUENA", "VACIA"):
        if k in cuenta:
            print("  %-12s %3d" % (k, cuenta[k]))

    for clave in ("MOCHA", "TEXTO", "DESCENTRADA", "PEQUENA", "VACIA"):
        nombres = sorted(n for n, v in resultados.items() if clave in v["estado"])
        if not nombres:
            continue
        print("\n=== %s (%d) ===" % (clave, len(nombres)))
        for n in nombres:
            v = resultados[n]
            print("   %-24s relleno=%.2f desx=%.2f desy=%.2f sueltas=%d"
                  % (n, v["relleno"], v["desx"], v["desy"], v["sueltas"]))

    if "--json" in sys.argv:
        json.dump(resultados, open(SALIDA, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1, sort_keys=True)
        print("\ninforme: %s" % SALIDA)


if __name__ == "__main__":
    main()
