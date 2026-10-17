# -*- coding: utf-8 -*-
"""
import_inicio.py — Portadas de las cinco tarjetas del inicio.

Toma `inicio-<id>.png` de img-ia-v2 y las deja en app/www/assets/img-memo/
con su manifiesto (imagenes-inicio.js).

Uso:
    python app/tools/import_inicio.py            # simulación
    python app/tools/import_inicio.py --aplicar
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
MANIFIESTO = os.path.join(APP, "www", "content", "imagenes-inicio.js")
ESTADO = os.path.join(RAIZ, "img-ia-v2", "_estado.json")

IDS = ["clases", "pintar", "juegos", "memo", "bingo", "falta", "traza", "repaso", "domino", "busca", "progreso"]
LADO = 512
CALIDAD = 90
MARGEN = 0.06


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


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
    hechas, faltan = {}, []
    for ident in IDS:
        ruta = os.path.join(ORIGEN, "inicio-" + ident + ".png")
        if os.path.exists(ruta):
            hechas[ident] = ruta
        else:
            faltan.append(ident)

    print("portadas de inicio : %d" % len(IDS))
    print("  generadas        : %d  (%s)" % (len(hechas), ", ".join(hechas)))
    print("  pendientes       : %d  (%s)" % (len(faltan), ", ".join(faltan) or "—"))

    if not aplicar:
        print("\n(simulación · usa --aplicar)")
        return

    os.makedirs(DESTINO, exist_ok=True)
    mapa = {}
    for ident, ruta in sorted(hechas.items()):
        img = preparar(ruta)
        if img is None:
            continue
        nombre = "inicio-" + ident + ".webp"
        img.save(os.path.join(DESTINO, nombre), "WEBP", quality=CALIDAD, method=6)
        mapa[ident] = "assets/img-memo/" + nombre

    io.open(MANIFIESTO, "w", encoding="utf-8").write(
        "// Generado por app/tools/import_inicio.py — no editar a mano.\n"
        "window.LANGKIDS_INICIO = %s;\n"
        % json.dumps(mapa, ensure_ascii=False, indent=1, sort_keys=True))

    if os.path.exists(ESTADO):
        estado = json.load(open(ESTADO, encoding="utf-8"))
        antes = len(estado.get("hechas", []))
        estado["hechas"] = [w for w in estado.get("hechas", []) if not w.startswith("inicio ")]
        if len(estado["hechas"]) != antes:
            json.dump(estado, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("\nescritas %d portadas en %s" % (len(mapa), DESTINO))
    for k in sorted(mapa):
        print("   %-9s %s" % (k, mapa[k]))


if __name__ == "__main__":
    main()
