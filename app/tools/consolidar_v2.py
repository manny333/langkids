# -*- coding: utf-8 -*-
"""
consolidar_v2.py — Deja SOLO la tanda nueva dentro de la app.

Qué hace:
  1. Para cada palabra con ilustración usa la versión nueva (img-ia-v2).
  2. Si alguna palabra todavía no tiene versión nueva, conserva la clásica
     para que nunca quede un hueco.
  3. Escribe el resultado en app/www/assets/img (el juego único de la app).
  4. Vacía el manifiesto de la tanda nueva y borra assets/img-v2.

Uso:
    python app/tools/consolidar_v2.py            # simulación
    python app/tools/consolidar_v2.py --aplicar  # consolida de verdad
"""
import json
import os
import shutil
import sys

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
WWW = os.path.join(APP, "www")
IMG = os.path.join(WWW, "assets", "img")
IMG_V2 = os.path.join(WWW, "assets", "img-v2")
FUENTE_V2 = os.path.join(RAIZ, "img-ia-v2")
MANIFIESTO = os.path.join(WWW, "content", "imagenes-v2.js")
LADO = 512
CALIDAD = 88


def palabras_con_imagen():
    d = json.load(open(os.path.join(APP, "content", "lessons.json"), encoding="utf-8"))
    salida = {}
    for nivel in d["levels"]:
        for unidad in nivel["units"]:
            for w in unidad["words"]:
                if w.get("img"):
                    salida[os.path.basename(w["img"])[:-5]] = w["en"]
    return salida


def main():
    aplicar = "--aplicar" in sys.argv
    palabras = palabras_con_imagen()
    nuevas, clasicas, faltan = [], [], []

    for slug in sorted(palabras):
        origen_v2 = os.path.join(IMG_V2, slug + ".webp")
        origen_clasica = os.path.join(IMG, slug + ".webp")
        if os.path.exists(origen_v2):
            nuevas.append(slug)
        elif os.path.exists(origen_clasica):
            clasicas.append(slug)
        else:
            faltan.append(slug)

    print("palabras con ilustración : %d" % len(palabras))
    print("  versión nueva          : %d" % len(nuevas))
    print("  se queda la clásica    : %d" % len(clasicas))
    if clasicas:
        print("     " + ", ".join(clasicas[:15]) + (" ..." if len(clasicas) > 15 else ""))
    print("  sin ninguna            : %d" % len(faltan))
    if faltan:
        print("     " + ", ".join(faltan[:15]))

    if not aplicar:
        print("\n(simulación · usa --aplicar)")
        return

    # 1) las nuevas pasan a ser las definitivas
    for slug in nuevas:
        shutil.copyfile(os.path.join(IMG_V2, slug + ".webp"), os.path.join(IMG, slug + ".webp"))

    # 2) se elimina la carpeta de la tanda nueva y el manifiesto
    if os.path.isdir(IMG_V2):
        shutil.rmtree(IMG_V2)
    open(MANIFIESTO, "w", encoding="utf-8").write(
        "// Ya solo hay una tanda de ilustraciones (ver docs/Revision-imagenes.md).\n"
        "window.LANGKIDS_IMG_V2 = [];\n")

    total = len([f for f in os.listdir(IMG) if f.endswith(".webp")])
    peso = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG)
               if f.endswith(".webp")) / (1024.0 * 1024.0)
    print("\nconsolidado: %d imágenes en assets/img (%.2f MB)" % (total, peso))
    print("img-v2 eliminado · manifiesto vacío (el selector de Ajustes desaparece solo)")


if __name__ == "__main__":
    main()
