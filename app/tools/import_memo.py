# -*- coding: utf-8 -*-
"""
import_memo.py — Ilustraciones extra solo para los memoramas.

Hay palabras de los memoramas que no están en el curso (pulpo, ballena, cangrejo,
delfín, tiburón, sandía, asustado). Sus imágenes se generan igual que las demás
pero se guardan aparte, en app/www/assets/img-memo/, para no ensuciar el curso.

Uso:
    python app/tools/import_memo.py            # simulación
    python app/tools/import_memo.py --aplicar
"""
import io
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
DESTINO = os.path.join(APP, "www", "assets", "img-memo")
MANIFIESTO = os.path.join(APP, "www", "content", "imagenes-memo.js")
ESTADO = os.path.join(RAIZ, "img-ia-v2", "_estado.json")

# palabras de los memoramas que no existen en el curso
EXTRAS = ["crab", "dolphin", "octopus", "scared", "shark", "watermelon", "whale"]

LADO = 512
CALIDAD = 88
MARGEN = 0.08


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = t.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def caja_dibujo(im):
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
    recorte = im.crop(caja)
    w, h = recorte.size
    lado = int(max(w, h) * (1 + MARGEN * 2))
    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    lienzo.paste(recorte, ((lado - w) // 2, (lado - h) // 2))
    return lienzo.resize((LADO, LADO), Image.LANCZOS)


def main():
    aplicar = "--aplicar" in sys.argv
    hechas, faltan = [], []
    for palabra in EXTRAS:
        ruta = os.path.join(ORIGEN, slug(palabra) + ".png")
        (hechas if os.path.exists(ruta) else faltan).append(palabra)

    print("palabras extra de memorama : %d" % len(EXTRAS))
    print("  con imagen generada      : %d  (%s)" % (len(hechas), ", ".join(hechas)))
    print("  pendientes de generar    : %d  (%s)" % (len(faltan), ", ".join(faltan) or "—"))

    if not aplicar:
        print("\n(simulación · usa --aplicar)")
        return

    os.makedirs(DESTINO, exist_ok=True)
    escritas = []
    for palabra in hechas:
        img = preparar(os.path.join(ORIGEN, slug(palabra) + ".png"))
        if img is None:
            continue
        img.save(os.path.join(DESTINO, slug(palabra) + ".webp"), "WEBP", quality=CALIDAD, method=6)
        escritas.append(slug(palabra))

    io.open(MANIFIESTO, "w", encoding="utf-8").write(
        "// Generado por app/tools/import_memo.py — no editar a mano.\n"
        "window.LANGKIDS_IMG_MEMO = %s;\n" % json.dumps(sorted(escritas)))

    # que estas palabras no cuenten como parte del curso
    if os.path.exists(ESTADO):
        estado = json.load(open(ESTADO, encoding="utf-8"))
        antes = len(estado.get("hechas", []))
        estado["hechas"] = [w for w in estado.get("hechas", []) if w not in EXTRAS]
        if len(estado["hechas"]) != antes:
            json.dump(estado, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("\nescritas %d imágenes en %s" % (len(escritas), DESTINO))
    print("manifiesto: %s" % ", ".join(sorted(escritas)))


if __name__ == "__main__":
    main()
