# -*- coding: utf-8 -*-
"""
fetch_images.py — Descarga imágenes de Pixabay para el vocabulario de LangKids.

Uso:
    python fetch_images.py --unit 1.1            # una unidad
    python fetch_images.py --all                 # todo el curso (lento)
    python fetch_images.py --unit 1.1 --tipo illustration

La clave se lee de la variable de entorno PIXABAY_KEY. Nunca se escribe en
ningún archivo que viaje dentro del APK.

Salida:
    app/www/assets/img/<palabra>.webp        imagen 512x512 (WebP)
    app/content/credits.json                 autor, id y licencia de cada imagen
    docs/img/contact-<unidad>.png            hoja de contactos para revisar
"""

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
IMG_DIR = os.path.join(APP, "www", "assets", "img")
LESSONS = os.path.join(APP, "content", "lessons.json")
CREDITS = os.path.join(APP, "content", "credits.json")
DOCS_IMG = os.path.join(RAIZ, "docs", "img")

API = "https://pixabay.com/api/"
UA = "LangKids-English/1.0 (app educativa; contacto: docente)"
TAM = 512

# Solo se buscan FOTOS para sustantivos concretos: en saludos, emociones o
# gramatica el buscador devuelve imagenes absurdas (un pajaros para "hello"),
# asi que esas palabras conservan su emoji.
FOTOGRAFIABLES = {
    # animales
    "cat", "dog", "bird", "fish", "rabbit", "cow", "pig", "horse", "duck", "sheep",
    "lion", "tiger", "elephant", "monkey", "giraffe", "snake", "crocodile",
    "penguin", "bear", "zebra", "spiders",
    # comida
    "apple", "banana", "orange", "grapes", "strawberry", "milk", "water", "juice",
    "bread", "cheese", "egg", "rice", "chicken", "salad", "cake", "ice cream",
    "sandwich",
    # juguetes
    "ball", "doll", "teddy bear", "train", "kite", "bike",
    # aula y casa
    "pencil", "pen", "crayon", "book", "notebook", "ruler", "rubber", "scissors",
    "bag", "desk", "chair", "board", "door", "window", "house", "bedroom",
    "kitchen", "bathroom", "garden", "bed", "table", "sofa", "tv", "fridge",
    # ropa
    "t-shirt", "trousers", "dress", "skirt", "shoes", "socks", "hat", "jacket",
    "shorts",
    # cuerpo
    "head", "hair", "eyes", "ears", "nose", "mouth", "teeth", "hands", "arms",
    "legs", "feet",
    # ciudad y transporte
    "school", "park", "hospital", "supermarket", "library", "cinema", "museum",
    "café", "shop", "street", "bus", "plane", "boat", "taxi",
    # naturaleza
    "mountain", "desert", "jungle", "ocean", "garden",
}

# Categorias de la API por grupo (mejoran mucho la pertinencia)
CATEGORIA = {}
for _w in {"apple", "banana", "orange", "grapes", "strawberry", "milk", "water",
           "juice", "bread", "cheese", "egg", "rice", "chicken", "salad", "cake",
           "ice cream", "sandwich"}:
    CATEGORIA[_w] = "food"
for _w in {"t-shirt", "trousers", "dress", "skirt", "shoes", "socks", "hat",
           "jacket", "shorts"}:
    CATEGORIA[_w] = "fashion"
for _w in {"cat", "dog", "bird", "fish", "rabbit", "cow", "pig", "horse", "duck",
           "sheep", "lion", "tiger", "elephant", "monkey", "giraffe", "snake",
           "crocodile", "penguin", "bear", "zebra", "spiders"}:
    CATEGORIA[_w] = "animals"
for _w in {"bus", "plane", "boat", "taxi", "train", "bike"}:
    CATEGORIA[_w] = "transportation"

# Consultas afinadas: evitan resultados absurdos del buscador
CONSULTA = {
    "orange": "orange fruit", "apple": "red apple", "chair": "wooden chair",
    "board": "blackboard classroom", "bank": "bank building", "square": "city square",
    "shop": "shop storefront", "café": "cafe coffee shop", "train": "steam train",
    "bear": "brown bear", "spiders": "spider", "eyes": "human eye",
    "head": "human head", "mouth": "human mouth", "teeth": "teeth smile",
    "hair": "hair close up", "hands": "human hands", "feet": "bare feet",
    "tv": "television", "ice cream": "ice cream cone", "teddy bear": "teddy bear toy",
    "t-shirt": "t-shirt clothing", "dress": "dress clothing", "skirt": "skirt clothing",
    "shorts": "shorts clothing", "bag": "school backpack", "park": "city park",
    "street": "city street", "jungle": "jungle forest", "desert": "desert dunes",
    "water": "glass of water", "milk": "glass of milk", "juice": "orange juice glass",
    "bread": "bread loaf", "cheese": "cheese slices", "egg": "chicken eggs",
    "rice": "cooked rice bowl", "chicken": "roast chicken", "salad": "green salad",
    "cake": "birthday cake", "t-shirt": "white t-shirt", "trousers": "jeans trousers",
    "dress": "summer dress", "skirt": "skirt clothing", "shoes": "sneakers shoes",
    "socks": "pair of socks", "hat": "sun hat", "jacket": "jacket clothing",
    "shorts": "shorts clothing", "grapes": "grapes bunch", "cheese": "cheese slices",
    "apple": "red apple fruit", "milk": "glass of milk", "cheese": "cheese block",
    "chicken": "roasted chicken", "ice cream": "ice cream cone",
    "t-shirt": "t-shirt on hanger", "trousers": "jeans pants",
    "dress": "dress on hanger", "skirt": "skirt on hanger",
    "jacket": "leather jacket", "shorts": "denim shorts",
    "hat": "straw hat", "shoes": "pair of sneakers", "socks": "socks pair",
    "pencil": "yellow pencil", "pen": "ballpoint pen", "crayon": "wax crayons",
    "book": "book cover", "notebook": "notebook paper", "ruler": "ruler measure",
    "rubber": "eraser", "scissors": "scissors office", "bag": "school backpack",
    "desk": "office desk", "chair": "wooden chair", "board": "blackboard",
    "door": "wooden door", "window": "house window", "house": "house exterior",
    "bedroom": "bedroom interior", "kitchen": "kitchen interior",
    "bathroom": "bathroom interior", "garden": "garden flowers", "bed": "bed bedroom",
    "table": "dining table", "sofa": "sofa living room", "tv": "television",
    "fridge": "refrigerator kitchen", "street": "city street",
}

def clave():
    k = os.environ.get("PIXABAY_KEY", "").strip()
    if not k:
        print("FALTA la variable de entorno PIXABAY_KEY", file=sys.stderr)
        sys.exit(2)
    return k


def buscar(palabra, key, tipo="photo", n=6, categoria=None):
    # OJO: "order" solo admite "popular" o "latest" (no existe "relevance")
    params = {
        "key": key,
        "q": palabra,
        "image_type": tipo,
        "safesearch": "true",
        "per_page": str(n),
        "lang": "en",
    }
    if categoria:
        params["category"] = categoria
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        limite = r.headers.get("X-RateLimit-Remaining")
        if limite is not None and int(limite) < 5:
            print("     (quedan %s peticiones en esta ventana)" % limite)
        return json.loads(r.read().decode("utf-8"))


def elegir(hits, palabra):
    """Prefiere una imagen cuyas etiquetas incluyan la palabra buscada."""
    p = palabra.lower()
    for h in hits:
        etiquetas = h.get("tags", "").lower()
        if p in etiquetas:
            return h
    return hits[0] if hits else None


def descargar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def cuadrado(datos):
    im = Image.open(io.BytesIO(datos)).convert("RGB")
    w, h = im.size
    lado = min(w, h)
    im = im.crop(((w - lado) // 2, (h - lado) // 2, (w + lado) // 2, (h + lado) // 2))
    return im.resize((TAM, TAM), Image.LANCZOS)


def nombre_archivo(palabra):
    s = re.sub(r"[^a-z0-9]+", "-", palabra.lower()).strip("-")
    return s + ".webp"


def cargar_creditos():
    if os.path.exists(CREDITS):
        try:
            with open(CREDITS, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"fuente": "Pixabay", "licencia": "Pixabay Content License",
            "aviso": "Atribución no obligatoria; se conserva por transparencia.",
            "imagenes": {}}


def hoja_contactos(palabras, ruta, titulo):
    """Miniatura con las imagenes descargadas, para revisar a ojo."""
    cols = 5
    celda, pie = 150, 34
    filas = (len(palabras) + cols - 1) // cols
    lienzo = Image.new("RGB", (cols * celda, filas * (celda + pie) + 44), "#FFF7E6")
    d = ImageDraw.Draw(lienzo)
    try:
        f_tit = ImageFont.truetype(r"C:\Windows\Fonts\georgiab.ttf", 22)
        f_pie = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 14)
    except Exception:
        f_tit = f_pie = ImageFont.load_default()
    d.text((12, 10), titulo, font=f_tit, fill="#2B2D42")

    for i, (palabra, archivo) in enumerate(palabras):
        cx = (i % cols) * celda
        cy = 44 + (i // cols) * (celda + pie)
        if archivo and os.path.exists(archivo):
            im = Image.open(archivo).resize((celda - 10, celda - 10), Image.LANCZOS)
            lienzo.paste(im, (cx + 5, cy + 5))
        else:
            d.rectangle([cx + 5, cy + 5, cx + celda - 5, cy + celda - 5], outline="#D9CFB8")
            d.text((cx + 20, cy + celda // 2), "sin imagen", font=f_pie, fill="#9A917F")
        d.text((cx + 8, cy + celda - 2), palabra[:20], font=f_pie, fill="#2B2D42")

    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    lienzo.save(ruta)
    return ruta


def candidatos(palabras, key, tipo):
    """
    Para cada palabra descarga 4 opciones y arma una hoja para elegir a ojo.
    Las elegidas se copian luego a www/assets/img/<palabra>.webp.
    """
    dir_out = os.path.join(RAIZ, "docs", "candidatos")
    os.makedirs(dir_out, exist_ok=True)
    filas = []
    for palabra in palabras:
        p = palabra.strip().lower()
        try:
            datos = buscar(CONSULTA.get(p, palabra), key, tipo, n=6,
                           categoria=CATEGORIA.get(p))
        except Exception as e:
            print("  %-14s ERROR %s" % (palabra, str(e)[:50]))
            continue
        hits = datos.get("hits", [])[:4]
        print("  %-14s %d opciones" % (palabra, len(hits)))
        for i, h in enumerate(hits, 1):
            destino = os.path.join(dir_out, "%s-%d.webp" % (nombre_archivo(palabra)[:-5], i))
            try:
                cuadrado(descargar(h["webformatURL"])).save(destino, "WEBP", quality=82)
                filas.append((palabra, i, destino, h.get("user")))
            except Exception as e:
                print("     opcion %d falló: %s" % (i, str(e)[:40]))
            time.sleep(0.35)

    if not filas:
        return
    # hoja: una fila por palabra
    celda, pie = 170, 26
    palabras_unicas = []
    for pal, _, _, _ in filas:
        if pal not in palabras_unicas:
            palabras_unicas.append(pal)
    cols = max(len([f for f in filas if f[0] == p]) for p in palabras_unicas)
    lienzo = Image.new("RGB", (cols * celda, len(palabras_unicas) * (celda + pie) + 40), "#FFF7E6")
    d = ImageDraw.Draw(lienzo)
    try:
        f_tit = ImageFont.truetype(r"C:\Windows\Fonts\georgiab.ttf", 20)
        f_pie = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 13)
    except Exception:
        f_tit = f_pie = ImageFont.load_default()
    d.text((10, 8), "Elige una opción por palabra (nombre de archivo: palabra-numero)", font=f_tit, fill="#2B2D42")
    for idx, pal in enumerate(palabras_unicas):
        y = 40 + idx * (celda + pie)
        opciones = [f for f in filas if f[0] == pal]
        for j, (_, n, ruta, autor) in enumerate(opciones):
            x = j * celda
            im = Image.open(ruta).resize((celda - 12, celda - 12), Image.LANCZOS)
            lienzo.paste(im, (x + 6, y + 6))
            d.text((x + 8, y + celda - 4), "%s · %d · %s" % (pal, n, (autor or "")[:14]),
                   font=f_pie, fill="#2B2D42")
    salida = os.path.join(RAIZ, "docs", "img", "candidatos.png")
    lienzo.save(salida)
    print("\nHoja de candidatas: docs/img/candidatos.png")
    print("Copia la elegida:  Copy-Item docs/candidatos/<palabra>-<n>.webp app/www/assets/img/<palabra>.webp")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", help="id de unidad, p. ej. 1.1")
    ap.add_argument("--all", action="store_true", help="todas las unidades")
    ap.add_argument("--tipo", default="photo", choices=["photo", "illustration", "all"])
    ap.add_argument("--force", action="store_true", help="vuelve a descargar")
    ap.add_argument("--max", type=int, default=0, help="limite de palabras (pruebas)")
    ap.add_argument("--palabras", help="lista separada por comas, para pruebas rapidas")
    ap.add_argument("--candidatos", help="palabras para las que generar 4 opciones y elegir a mano")
    args = ap.parse_args()

    key = clave()
    if args.candidatos:
        candidatos(args.candidatos.split(","), key, args.tipo)
        return 0
    with open(LESSONS, encoding="utf-8") as f:
        contenido = json.load(f)

    unidades = []
    for lv in contenido["levels"]:
        for u in lv["units"]:
            if args.all or (args.unit and u["id"] == args.unit):
                unidades.append(u)
    if not unidades:
        print("No encontre la unidad indicada", file=sys.stderr)
        return 2

    os.makedirs(IMG_DIR, exist_ok=True)
    creditos = cargar_creditos()
    descargadas, saltadas, fallidas = 0, 0, 0

    for u in unidades:
        print("\n=== Unidad %s · %s ===" % (u["id"], u["title"]))
        solo = None
        if args.palabras:
            solo = {p.strip().lower() for p in args.palabras.split(",")}
        for w in u["words"]:
            palabra = w["en"]
            if solo is not None and palabra.strip().lower() not in solo:
                continue
            if palabra.strip().lower() not in FOTOGRAFIABLES:
                saltadas += 1
                continue
            destino = os.path.join(IMG_DIR, nombre_archivo(palabra))
            if os.path.exists(destino) and not args.force:
                saltadas += 1
                continue
            if args.max and descargadas >= args.max:
                break
            try:
                datos = buscar(CONSULTA.get(palabra.strip().lower(), palabra), key, args.tipo,
                                CATEGORIA.get(palabra.strip().lower()))
                hit = elegir(datos.get("hits", []), palabra)
                if not hit:
                    print("  %-22s sin resultados" % palabra)
                    fallidas += 1
                    time.sleep(0.4)
                    continue
                im = cuadrado(descargar(hit["webformatURL"]))
                im.save(destino, "WEBP", quality=82, method=6)
                creditos["imagenes"][palabra] = {
                    "archivo": "assets/img/" + os.path.basename(destino),
                    "pixabay_id": hit.get("id"),
                    "autor": hit.get("user"),
                    "pagina": hit.get("pageURL"),
                    "etiquetas": hit.get("tags", "")[:120],
                    "licencia": "Pixabay Content License",
                    "descargado": time.strftime("%Y-%m-%d"),
                }
                descargadas += 1
                print("  %-22s OK  (%s, %s KB)" % (palabra, hit.get("user"),
                                                   round(os.path.getsize(destino) / 1024)))
            except Exception as e:
                print("  %-22s ERROR %s" % (palabra, str(e)[:60]))
                fallidas += 1
            time.sleep(0.45)          # cortesia: limite de 100 peticiones/minuto

    os.makedirs(os.path.dirname(CREDITS), exist_ok=True)
    with open(CREDITS, "w", encoding="utf-8") as f:
        json.dump(creditos, f, ensure_ascii=False, indent=1)

    # copia como JS para que la app pueda mostrar la atribución sin fetch()
    credits_js = os.path.join(APP, "www", "content", "credits.js")
    with open(credits_js, "w", encoding="utf-8") as f:
        f.write("/* Generado por tools/fetch_images.py */\n")
        f.write("window.LANGKIDS_CREDITS = ")
        json.dump(creditos, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print("\nResumen: %d descargadas · %d saltadas (ya existian o no aplican) · %d fallidas"
          % (descargadas, saltadas, fallidas))
    print("Créditos: %s (%d imágenes)" % (CREDITS, len(creditos["imagenes"])))

    # hoja de contactos de lo que hay ahora en estas unidades
    for u in unidades:
        pares = []
        for w in u["words"]:
            ruta = os.path.join(IMG_DIR, nombre_archivo(w["en"]))
            pares.append((w["en"], ruta))
        nombre = "contact-%s.png" % u["id"].replace(".", "-")
        hoja_contactos(pares, os.path.join(DOCS_IMG, nombre),
                       "Unidad %s · %s" % (u["id"], u["title"]))
        print("Hoja de contactos: docs/img/" + nombre)

    return 0


if __name__ == "__main__":
    sys.exit(main())
