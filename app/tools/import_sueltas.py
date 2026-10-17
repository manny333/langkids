# -*- coding: utf-8 -*-
"""
import_sueltas.py — Importa las ilustraciones individuales de img-ia/<carpeta>/*.png

Cada archivo se llama como la palabra que representa (a veces con un matiz:
`bathroom_bathtub.png`, `ate_apple.png`). El programa:

  1. Empareja el nombre del archivo con una palabra del curso.
  2. Recorta los márgenes blancos, la centra en un lienzo cuadrado y la guarda
     como WebP de 512x512 en app/www/assets/img/<slug>.webp
  3. Actualiza los créditos.

Uso:
    python app/tools/import_sueltas.py            # simulación: solo informa
    python app/tools/import_sueltas.py --aplicar  # escribe las imágenes
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
ORIGEN = os.path.join(RAIZ, "img-ia")
WWW = os.path.join(APP, "www")
DESTINO = os.path.join(WWW, "assets", "img")

sys.path.insert(0, AQUI)
import import_ia_images as ia  # etiquetado de tinta ya resuelto
CREDITOS = os.path.join(WWW, "content", "credits.json")

LADO = 512          # tamaño final de cada ilustración
CALIDAD = 90        # calidad WebP
MARGEN = 0.04       # aire alrededor del dibujo dentro del lienzo

# Colores y números: nunca se usan para emparejar por prefijo/sufijo, porque
# "backpack_blue" es una mochila, no el color azul.
GENERICOS = {
    "red", "blue", "green", "yellow", "orange", "purple", "pink", "brown",
    "black", "white", "grey", "gray", "one", "two", "three", "four", "five",
    "six", "seven", "eight", "nine", "ten", "big", "small", "left", "right",
    "up", "down", "clean", "blue2",
}

# Correcciones a mano: nombre del archivo (sin extensión) -> palabra del curso.
FORZAR = {
    "armchair": "armchair",
    "airplane": "plane",
    "bicycle": "bike",
    "bike_red": "bike",
    "bike_yellow": "bike",
    "television": "tv",
    "refrigerator": "fridge",
    "backpack_blue": "school-bag",
    "backpack_orange": "school-bag",
    "have_lunchbox": "have-lunch",
    "wash_face": "wash-my-face",
    "pancakes": "have-breakfast",
    "sleeping": "go-to-bed",
    "pajamas": "get-dressed",
    "friends_hugging": "friend",
    "grandfather_cane": "grandpa",
    "grandmother": "grandma",
    "children_population": "population",
    "flags_countries": "nationality",
    "globe_map": "world",
    "world_globe": "world",
    "weekly_calendar": "monday-sunday",
    "beach_umbrella": "umbrella",
    "carnival_mask": "carnival",
    "flight_boarding": "plane",
    "fuji_blossoms": "japan",
    "pizza_slice": "pizza",
    "suitcase": "suitcase",
    "arrow_straight_up": "go-straight",
    "ate_apple": "ate",
    "cleaned_broom": "cleaned",
    "cooked_pot": "cooked",
    "had_gift": "had",
    "played_football": "played",
    "saw_eye": "saw",
    "buy_shopping": "buy",
    "capital_city": "capital",
    "drank_water": "drank",
    "gave_present": "gave",
    "help_person": "help",
    # mochilas, colores, números y conceptos con nombre distinto en el archivo
    "backpack_blue": "bag",
    "backpack_orange": "bag",
    "crayons_box": "crayon",
    "crayons_pack": "crayon",
    "red_circle": "red",
    "blue_star": "blue",
    "yellow_triangle": "yellow",
    "green_square": "green",
    "purple_diamond": "purple",
    "pink_flower": "pink",
    "brown_pentagon": "brown",
    "black_hexagon": "black",
    "white_cloud": "white",
    "grey_oval": "grey",
    "one_1": "one",
    "two_2": "two",
    "three_3": "three",
    "four_4": "four",
    "five_5": "five",
    "six_6": "six",
    "seven_7": "seven",
    "eight_8": "eight",
    "nine_9": "nine",
    "ten_10": "ten",
    "weekly_calendar": "Monday-Sunday",
    "weekly_schedule": "Monday-Sunday",
    "have_lunchbox": "have lunch",
    "wash_face": "wash my face",
    "arrow_straight_up": "go straight",
    "counting": "count",
    "fuji_blossoms": "Japan",
    "globe_map": "continent",
    "globe_world": "continent",
    "globe": "continent",
    "world_globe": "continent",
    "scroll_quill": "story",
    "thermometer": "weather",
    "light": "lighter",
    "bright_sun": "sunny",
    "made_craft": "made",
    "bicycle_ride": "ride",
    "lime_juice": "juice",
    "orange_juice": "juice",
    "arm_muscle_left": "arms",
    "arm_muscle_right": "arms",
    "cafe": "cafe",
}


def slug(texto):
    """'Living room' -> 'living-room' (igual que gen_content.py)."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = t.lower().replace("'", "").replace("’", "")
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def cargar_palabras():
    ruta = os.path.join(APP, "content", "lessons.json")
    d = json.load(open(ruta, encoding="utf-8"))
    palabras = {}
    for nivel in d["levels"]:
        for unidad in nivel["units"]:
            for w in unidad["words"]:
                palabras[w["en"].strip()] = {
                    "slug": slug(w["en"]),
                    "unidad": unidad["id"],
                    "nivel": nivel["id"],
                }
    return palabras


def limpiar_marco(im, banda=0.06):
    """
    La IA dibuja una tarjeta de gris muy claro alrededor de algunas imágenes.
    Se borra (a blanco) el anillo exterior para que no entre en el recorte.
    """
    a = np.array(im.convert("RGB")).astype(np.int16)
    alto, ancho = a.shape[:2]
    bx, by = int(ancho * banda), int(alto * banda)
    mx, mn = a.max(axis=2), a.min(axis=2)
    luz = a.mean(axis=2)
    gris = ((mx - mn) < 18) & (luz > 185) & (luz < 252)
    anillo = np.zeros((alto, ancho), dtype=bool)
    anillo[:by, :] = True
    anillo[alto - by:, :] = True
    anillo[:, :bx] = True
    anillo[:, ancho - bx:] = True
    a[gris & anillo] = [255, 255, 255]
    return Image.fromarray(a.astype(np.uint8))


def cajas_blancas(im):
    """Caja del dibujo dentro del marco blanco."""
    a = np.array(limpiar_marco(im).convert("RGB")).astype(np.int16)
    mx, mn = a.max(axis=2), a.min(axis=2)
    luz = a.mean(axis=2)
    tinta = ((mx - mn) > 30) | (luz < 185)
    ys, xs = np.where(tinta)
    if len(xs) < 40:
        return (0, 0, im.width, im.height)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def objeto_principal(im):
    """
    Caja del dibujo: la mancha de tinta más grande, descartando marcos de
    tarjeta (cajas casi tan grandes como la imagen y huecas) y etiquetas.
    """
    mask = ia.mascara_tinta(im)
    piezas = ia.etiquetar(mask)
    if not piezas:
        return (0, 0, im.width, im.height)
    W, H = im.width, im.height
    utiles = []
    for x0, y0, x1, y1, area in piezas:
        ancho, alto = x1 - x0, y1 - y0
        cubre = (ancho * alto) / float(W * H)
        relleno = area / float(max(1, ancho * alto))
        if not (cubre > 0.75 and relleno < 0.30):
            utiles.append((x0, y0, x1, y1, area))
    x0, y0, x1, y1, _ = max(utiles or piezas, key=lambda c: c[4])
    return (x0, y0, x1, y1)


def procesar(ruta):
    """Recorta el objeto principal, lo centra en cuadrado (RGB, LADO x LADO)."""
    im = limpiar_marco(Image.open(ruta).convert("RGB"))
    x0, y0, x1, y1 = objeto_principal(im)
    ancho, alto = x1 - x0, y1 - y0
    lado = int(max(ancho, alto) * (1 + MARGEN * 2))
    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    recorte = im.crop((x0, y0, x1, y1))
    lienzo.paste(recorte, ((lado - ancho) // 2, (lado - alto) // 2))
    return lienzo.resize((LADO, LADO), Image.LANCZOS)


def emparejar(nombre, palabras):
    """Devuelve la palabra del curso para un archivo, o None."""
    base = os.path.splitext(nombre)[0]
    if base in FORZAR and FORZAR[base] in palabras:
        return FORZAR[base]

    s = slug(base)
    por_slug = {v["slug"]: k for k, v in palabras.items()}
    if s in por_slug:
        return por_slug[s]

    partes = s.split("-")
    # prefijo más largo que sea una palabra real (nunca un color o número)
    for corte in range(len(partes) - 1, 0, -1):
        cand = "-".join(partes[:corte])
        if cand in por_slug and cand not in GENERICOS:
            return por_slug[cand]
    # sufijo más largo que sea una palabra real
    for corte in range(1, len(partes)):
        cand = "-".join(partes[corte:])
        if cand in por_slug and cand not in GENERICOS:
            return por_slug[cand]
    return None


def main():
    aplicar = "--aplicar" in sys.argv
    palabras = cargar_palabras()
    carpetas = sorted(d for d in os.listdir(ORIGEN) if os.path.isdir(os.path.join(ORIGEN, d)))

    asignadas, sin_pareja, repetidas = {}, [], {}
    for carpeta in carpetas:
        ruta_carpeta = os.path.join(ORIGEN, carpeta)
        for archivo in sorted(os.listdir(ruta_carpeta)):
            if not archivo.lower().endswith(".png"):
                continue
            palabra = emparejar(archivo, palabras)
            if palabra is None:
                sin_pareja.append(os.path.join(carpeta, archivo))
                continue
            repetidas.setdefault(palabra, []).append(archivo)
            asignadas.setdefault(palabra, os.path.join(ruta_carpeta, archivo))

    print("PNG encontrados      : %d" % (len(asignadas) + len(sin_pareja) + sum(
        len(v) - 1 for v in repetidas.values())))
    print("palabras con imagen  : %d" % len(asignadas))
    print("archivos sin pareja  : %d" % len(sin_pareja))
    if sin_pareja:
        print("\n  sin pareja (se ignoran):")
        for s in sin_pareja:
            print("    " + s)

    dobles = {k: v for k, v in repetidas.items() if len(v) > 1}
    if dobles:
        print("\n  palabras con varios archivos (se usa el primero):")
        for k, v in sorted(dobles.items()):
            print("    %-22s %s" % (k, ", ".join(v)))

    con_imagen_hoy = set()
    if os.path.exists(CREDITOS):
        try:
            cr = json.load(open(CREDITOS, encoding="utf-8"))
            con_imagen_hoy = set(cr.get("imagenes", {}).keys())
        except Exception:
            pass
    print("\npalabras del curso   : %d" % len(palabras))
    print("  ya tenían imagen   : %d" % len(con_imagen_hoy))
    print("  nuevas por esta vía: %d" % len([p for p in asignadas if p not in con_imagen_hoy]))

    if not aplicar:
        print("\n(simulación: no se escribió nada · usa --aplicar)")
        return

    creditos = json.load(open(CREDITOS, encoding="utf-8")) if os.path.exists(CREDITOS) else {"imagenes": {}}
    escritas = 0
    for palabra, ruta in sorted(asignadas.items()):
        img = procesar(ruta)
        salida = os.path.join(DESTINO, palabras[palabra]["slug"] + ".webp")
        img.save(salida, "WEBP", quality=CALIDAD, method=6)
        creditos.setdefault("imagenes", {})[palabra] = {
            "archivo": "assets/img/%s.webp" % palabras[palabra]["slug"],
            "autor": "LangKids (IA)",
            "licencia": "Uso propio",
            "origen": os.path.basename(ruta),
            "nota": "ilustración individual",
        }
        escritas += 1
    json.dump(creditos, open(CREDITOS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nescritas %d imágenes en %s" % (escritas, DESTINO))


if __name__ == "__main__":
    main()
