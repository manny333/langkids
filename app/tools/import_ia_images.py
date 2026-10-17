# -*- coding: utf-8 -*-
"""
import_ia_images.py — Recorta las hojas de ilustraciones generadas con IA
(carpeta img-ia) y las convierte en las imágenes de la app.

Cada hoja es una cuadrícula de tarjetas. Dos modos:
  grid : la cuadrícula es regular -> se divide en filas x columnas
  auto : las tarjetas están escalonadas -> se detectan por contenido (tinta)

Salida:
    app/www/assets/img/<palabra>.webp   512x512, fondo blanco
    app/content/credits.json            ficha de cada imagen (autoría IA)
    docs/img/ia-<hoja>.png              hoja de verificación de los recortes

Uso:  python app/tools/import_ia_images.py
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
ORIGEN = os.path.join(RAIZ, "img-ia")
DESTINO = os.path.join(APP, "www", "assets", "img")
CREDITS = os.path.join(APP, "content", "credits.json")
DOCS = os.path.join(RAIZ, "docs", "img")
TAM = 512

# ---------------------------------------------------------------------------
# Qué hay en cada hoja (orden de lectura: izquierda→derecha, arriba→abajo).
# None = celda vacía o repetida que se descarta.
# ---------------------------------------------------------------------------
HOJAS = {
    "01_animales.jpg": dict(modo="grid", cols=5, rows=5, mapa=[
        "cat", "dog", "bird", "fish", "rabbit",
        "cow", "pig", "duck", None, None,
        "horse", "sheep", "lion", "tiger", "elephant",
        "giraffe", "snake", "crocodile", None, "monkey",
        None, "penguin", "bear", "zebra", "spiders",
    ]),
    "02_comida_y_bebida.jpg": dict(modo="grid", cols=5, rows=5, inset=0.12, mapa=[
        "apple", "banana", "orange", "grapes", None,
        "strawberry", "milk", "water", "juice", None,
        "bread", "cheese", "egg", "rice", None,
        "chicken", "salad", "cake", "ice cream", None,
        "sandwich", None, None, None, None,
    ]),
    "03_ropa.jpg": dict(modo="auto", padding=0.02, mapa=[
        "t-shirt", "trousers", "dress",
        "skirt", "shoes", "socks", "hat",
        "jacket", "shorts", "scarf",
    ]),
    "04_casa.jpg": dict(modo="grid", cols=4, rows=4, inset=0.06, corte_inferior=0.22, mapa=[
        "house", "bed", "kitchen", "bathroom",
        "sofa", "garden", None, "table",
        None, "tv", "fridge", "door",
        "window", None, None, None,
    ]),
    "05_aula_y_utiles.jpg": dict(modo="grid", cols=4, rows=4, mapa=[
        "pencil", "pen", "crayon", None,
        "book", "notebook", "ruler", None,
        "rubber", "scissors", "bag", None,
        "desk", "chair", "board", None,
    ]),
    "06_juguetes.jpg": dict(modo="auto", padding=0.03, mapa=[
        "ball", "doll", "teddy bear",
        "kite", "train", "blocks",
    ]),
    "07_cuerpo.jpg": dict(modo="grid", cols=4, rows=4, inset=0.14, mapa=[
        "head", None, "eyes", None,
        "ears", "nose", "teeth", "mouth",
        "hands", "arms", None, "legs",
        "feet", "tummy", None, None,
    ]),
    "08_transporte.jpg": dict(modo="proyeccion", inset=0.06, mapa=[
        "bus", "car",
        "plane", "boat",
        "taxi", "underground",
    ]),
    "09_lugares.jpg": dict(modo="grid", cols=3, rows=4, inset=0.10, corte_inferior=0.24, mapa=[
        "school", "park", "hospital",
        "supermarket", "library", "cinema",
        "museum", "bank", "café",
        "shop", "street", "square",
    ]),
    "10_naturaleza_y_clima.jpg": dict(modo="proyeccion", inset=0.04, mapa=[
        "mountain", "ocean", "desert",
        "jungle", "sunny", "rainy",
        "cloudy", "windy", "snowy",
        "stormy", "foggy", "spring",
        "umbrella", "autumn", "winter",
    ]),
    "11_deportes.jpg": dict(modo="grid", cols=3, rows=2, mapa=[
        "football", "basketball", "tennis",
        None, None, None,
    ]),
    "12_colores_y_formas.jpg": dict(modo="grid", cols=3, rows=3, mapa=[
        "red", "blue", "yellow",
        "green", "purple", "pink",
        "brown", "black", "white",
    ]),
    "13_numeros.jpg": dict(modo="auto", padding=0.02, mapa=[
        "one", "two", "three",
        "four", "five", "six", "seven",
        "eight", "nine", "ten",
    ]),
    "14_calendario_y_meses.jpg": dict(modo="proyeccion", inset=0.06, mapa=[
        "morning", "afternoon", "evening", "night",
        None, "january", "february", "march",
        "april", "may", "june", "july",
        "august", "september", "october", "november",
        "december", None, None, None,
    ]),
    "15_paises_y_viajes.jpg": dict(modo="grid", cols=4, rows=4, inset=0.10, mapa=[
        "spain", "england", "france", "italy",
        None, None, "japan", "brazil",
        None, None, "continent", "trip",
        None, None, "travel", "holiday",
    ]),
    "16_rutinas_diarias.jpg": dict(modo="proyeccion", inset=0.04, mapa=[
        "wake up", "get up", "get dressed", None,
        "brush my teeth", "wash my face", "have breakfast", None,
        "have lunch", "have dinner", "go to school", None,
        "do homework", "watch TV", "go to bed", None,
    ]),
    "17_acciones_y_movimiento.jpg": dict(modo="grid", cols=3, rows=3, inset=0.06,
                                         corte_superior=0.15, mapa=[
        "run", "jump", "climb",
        "swim", "fly", "cycling",
        "dance", "sing", "play",
    ]),
    "18_aprendizaje_adjetivos_y_fiesta.jpg": dict(modo="grid", cols=4, rows=4, inset=0.10,
                                                  corte_inferior=0.28, mapa=[
        "draw", "paint", "read", "write",
        "study", "cook", "teacher", "hero",
        "villain", "hot", "cold", "warm",
        "smile", "birthday party", "glasses", "beard",
    ]),
    "19_familia_y_personas.jpg": dict(modo="grid", cols=4, rows=4, inset=0.12, mapa=[
        "mummy", "daddy", "baby", "boy",
        "girl", "grandma", "grandpa", "family",
        None, None, None, None,
        None, None, "friend", None,
    ]),
    "20_emociones_y_sentimientos.jpg": dict(modo="grid", cols=4, rows=4, inset=0.12, corte_inferior=0.17, mapa=[
        "happy", "sad", "angry", "sleepy",
        "hungry", "thirsty", "brave", "shy",
        "funny", "kind", "like", "don't like",
        "yummy", None, None, None,
    ]),
    "21_saludos_y_cortesia.jpg": dict(modo="proyeccion", inset=0.06, mapa=[
        "hello", "good morning", "good afternoon",
        "goodbye", "please", "thank you",
        "sorry", "fine", "favorite",
    ]),
    "22_preposiciones_y_direcciones.jpg": dict(modo="grid", cols=4, rows=4, inset=0.08,
                                              corte_superior_filas=[0.30, 0.30, 0.0, 0.30],
                                              mapa=[
        "in", "on", "under", "behind",
        "in front of", "between", "next to", None,
        None, "turn left", "turn right", None,
        "go straight", None, None, "opposite",
    ]),
    "23_opuestos_y_comparativos.jpg": dict(modo="grid", cols=4, rows=4, inset=0.08,
                                           corte_superior=0.26, mapa=[
        "big", "small", "tall", "short",
        "fast", "slow", "heavier", "lighter",
        "long", None, "curly", "straight",
        "dark", None, None, "strong",
    ]),
    "24_conceptos_tiempo_y_gramatica.jpg": dict(modo="grid", cols=4, rows=4, inset=0.10,
                                                corte_inferior=0.26, mapa=[
        "o'clock", "half past", "yesterday", "once upon a time",
        "happy ending", "alphabet", "idea", "plan",
        "count", "weather", "continent", "story",
        None, None, None, None,
    ]),
    "25_familia_y_aspecto.jpg": dict(modo="grid", cols=3, rows=3, inset=0.12, mapa=[
        "sister", "brother", "hair",
        "thin", "fair", "moustache",
        "friendly", "clever", None,
    ]),
    "26_fiesta_tiempo_escuela.jpg": dict(modo="grid", cols=3, rows=3, inset=0.12, mapa=[
        "birthday", "balloon", "month",
        "letter", "spell", "Monday-Sunday",
        "party", "invitation", "free time",
    ]),
    "27_casa_y_ocio.jpg": dict(modo="grid", cols=3, rows=3, inset=0.12, mapa=[
        "bedroom", "living room", "favorite",
        "summer", "cool", "reading",
        "painting", "swimming", "dancing",
    ]),
    "28_acciones_y_mundo.jpg": dict(modo="grid", cols=3, rows=3, inset=0.12, mapa=[
        "singing", "cooking", "writing",
        "drawing", "acting", "ride",
        "character", "beautiful", "country",
    ]),
    "29_pasado_1.jpg": dict(modo="grid", cols=3, rows=3, inset=0.12, mapa=[
        "played", "watched", "visited",
        "cooked", "cleaned", "studied",
        "saw", "had", "ate",
    ]),
    "30_pasado_2_y_planes.jpg": dict(modo="grid", cols=3, rows=3, inset=0.12, mapa=[
        "drank", "made", "took",
        "gave", "visit", "buy",
        "meet", "help", "capital",
    ]),
    "31_extras.jpg": dict(modo="grid", cols=3, rows=3, inset=0.12, mapa=[
        "bike", None, None,
        None, "population", None,
        "nationality", None, None,
    ]),
}


# --------------------------------------------------------------------------- utilidades
# Palabras que comparten dibujo con otra (se copia el archivo ya recortado)
COPIAS = {
    "hi": "hello",
    "bye-bye": "goodbye",
    "of course": "fine",
    "hobby": "favorite",
    "today": "yesterday",
    "tomorrow": "yesterday",
    "degrees": "weather",
    "project": "plan",
    "how many": "count",
    "narrator": "story",
    "love": "like",
    "near": "next to",
}


# Reencuadres manuales: palabras cuyo recorte automático quedó descuadrado.
# (hoja, fila, columna, filas de la hoja, columnas de la hoja) — índices desde 0
# Cajas medidas a mano sobre la hoja original (x0, y0, x1, y1).
REENCUADRE_CAJA = {
    # la hoja del calendario tiene 4 filas (4+4+4+5) y las etiquetas van debajo:
    # estas cajas están medidas sobre la hoja y se usan tal cual
    "afternoon": ("14_calendario_y_meses.jpg", (301, 58, 485, 242)),
    "april":     ("14_calendario_y_meses.jpg", (62, 543, 228, 717)),
}

# Cajas medidas que además necesitan alineación vertical (la etiqueta está
# encima o debajo y el cuadro, al centrarse, la alcanzaría).
REENCUADRE_CAJA_ALINEADA = {
    # el oso de "behind" se sale de su celda por la izquierda
    "behind": ("22_preposiciones_y_direcciones.jpg", (770, 92, 962, 241), "arriba"),
}

# Palabras cuyo encuadre se pega al borde inferior del dibujo: la etiqueta de la
# hoja está justo debajo y, al centrar el cuadro, se colaba.
REENCUADRE_ABAJO = set()

# Palabras con un corchete decorativo pegado al dibujo: se limpia el trazo
# oscuro que flota sobre blanco en toda la imagen (no solo arriba).
LIMPIAR_FLOTANTE = {"tummy"}

# Celdas de una rejilla regular (hoja, fila, columna, filas, columnas).
REENCUADRE = {
    # (hoja, fila, columna, filas, columnas): encuadre por objeto más grande
    "arms":     ("07_cuerpo.jpg", 2, 1, 4, 4),
    "autumn":   ("10_naturaleza_y_clima.jpg", 4, 1, 5, 3),
    "angry":    ("20_emociones_y_sentimientos.jpg", 0, 2, 4, 4),
    "alphabet": ("24_conceptos_tiempo_y_gramatica.jpg", 1, 1, 4, 4),
    # objetos anchos que el margen de la rejilla recortaba
    "bear":     ("01_animales.jpg", 4, 2, 5, 5),
    "bus":      ("08_transporte.jpg", 0, 0, 3, 3),
    "car":      ("08_transporte.jpg", 0, 2, 3, 3),
    "chicken":  ("02_comida_y_bebida.jpg", 3, 0, 5, 5),
    "bathroom": ("04_casa.jpg", 0, 3, 4, 4, 0.10),
    # hoja 31: la bici y el grupo de gente ocupan toda la celda
    "bike":        ("31_extras.jpg", 0, 0, 3, 3, 0.06),
    "nationality": ("31_extras.jpg", 2, 0, 3, 3, 0.06),
    "population":  ("31_extras.jpg", 1, 1, 3, 3, 0.06),
}


def slug(palabra):
    import re
    return re.sub(r"[^a-z0-9]+", "-", palabra.strip().lower()).strip("-")


def mascara_tinta(im):
    """Pixeles con color o con línea oscura (los objetos, no el fondo ni las tarjetas)."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    mx, mn = a.max(axis=2), a.min(axis=2)
    saturacion = mx - mn
    luz = a.mean(axis=2)
    return (saturacion > 30) | (luz < 170)


def dilatar(mask, r):
    """Dilatación cuadrada simple (une partes del mismo objeto)."""
    out = mask.copy()
    for _ in range(r):
        m = out.copy()
        out[1:, :] |= m[:-1, :]
        out[:-1, :] |= m[1:, :]
        m = out.copy()
        out[:, 1:] |= m[:, :-1]
        out[:, :-1] |= m[:, 1:]
    return out


def etiquetar(mask):
    """Componentes conexas (4-vecindad) con búsqueda en anchura."""
    alto, ancho = mask.shape
    visto = np.zeros_like(mask, dtype=bool)
    cajas = []
    for y0 in range(alto):
        fila = mask[y0]
        for x0 in range(ancho):
            if not fila[x0] or visto[y0, x0]:
                continue
            pila = [(y0, x0)]
            visto[y0, x0] = True
            xmin = xmax = x0
            ymin = ymax = y0
            area = 0
            while pila:
                y, x = pila.pop()
                area += 1
                if x < xmin: xmin = x
                if x > xmax: xmax = x
                if y < ymin: ymin = y
                if y > ymax: ymax = y
                if y > 0 and mask[y - 1, x] and not visto[y - 1, x]:
                    visto[y - 1, x] = True; pila.append((y - 1, x))
                if y + 1 < alto and mask[y + 1, x] and not visto[y + 1, x]:
                    visto[y + 1, x] = True; pila.append((y + 1, x))
                if x > 0 and mask[y, x - 1] and not visto[y, x - 1]:
                    visto[y, x - 1] = True; pila.append((y, x - 1))
                if x + 1 < ancho and mask[y, x + 1] and not visto[y, x + 1]:
                    visto[y, x + 1] = True; pila.append((y, x + 1))
            cajas.append((xmin, ymin, xmax + 1, ymax + 1, area))
    return cajas


def _bandas(perfil, largo_min, hueco_min=6):
    """Devuelve los tramos [inicio, fin) donde el perfil supera el umbral."""
    bandas, inicio, hueco = [], None, 0
    for i, v in enumerate(perfil):
        if v:
            if inicio is None:
                inicio = i
            hueco = 0
        elif inicio is not None:
            hueco += 1
            if hueco >= hueco_min:
                if i - hueco - inicio >= largo_min:
                    bandas.append((inicio, i - hueco + 1))
                inicio = None
    if inicio is not None and len(perfil) - inicio >= largo_min:
        bandas.append((inicio, len(perfil)))
    return bandas


def cajas_proyeccion(im):
    """
    Segmenta por proyecciones: primero filas de objetos, luego columnas dentro
    de cada fila. Ignora los textos porque son bandas muy finas.
    """
    mask = mascara_tinta(im)
    filas = mask.sum(axis=1)
    bandas_y = _bandas(filas > max(2, int(im.width * 0.008)), int(im.height * 0.06))
    cajas = []
    for y0, y1 in bandas_y:
        sub = mask[y0:y1]
        cols = sub.sum(axis=0)
        for x0, x1 in _bandas(cols > max(1, int(sub.shape[0] * 0.02)), int(im.width * 0.04)):
            cajas.append([x0, y0, x1, y1])
    return cajas


def cajas_auto(im, minimo=1200):
    """Detecta las tarjetas por contenido y las devuelve ordenadas."""
    peq = im.convert("RGB").resize((im.width // 2, im.height // 2), Image.LANCZOS)
    mask = dilatar(mascara_tinta(peq), 10)
    cajas = [c for c in etiquetar(mask) if c[4] >= minimo]
    # descartar cajas muy alargadas (líneas de texto o sombras)
    limpias = []
    for x0, y0, x1, y1, _ in cajas:
        w, h = x1 - x0, y1 - y0
        if w < 55 or h < 55:
            continue
        if w / float(h) > 2.4 or h / float(w) > 2.4:
            continue
        limpias.append([x0 * 2, y0 * 2, x1 * 2, y1 * 2])
    # ordenar por filas (tolerancia 60 px) y luego por x
    limpias.sort(key=lambda b: (round((b[1] + b[3]) / 2 / 60), b[0]))
    return limpias


def cajas_grid(im, cols, rows):
    w, h = im.width / float(cols), im.height / float(rows)
    cajas = []
    for r in range(rows):
        for c in range(cols):
            cajas.append([int(c * w), int(r * h), int((c + 1) * w), int((r + 1) * h)])
    return cajas


def cajas_tarjetas(im, minimo=0.012):
    """Detecta las tarjetas blancas de la hoja (deja fuera el fondo y los textos)."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    blanco = (a.min(axis=2) >= 250)
    mask = dilatar(blanco, 2)
    area_min = im.width * im.height * minimo
    cajas = []
    for x0, y0, x1, y1, area in etiquetar(mask):
        if area < area_min:
            continue
        if (x1 - x0) < im.width * 0.08 or (y1 - y0) < im.height * 0.04:
            continue
        cajas.append([x0, y0, x1, y1])
    cajas.sort(key=lambda b: (round((b[1] + b[3]) / 2 / 80), b[0]))
    return cajas


def recortar(im, caja, inset=0.10, corte_inferior=0.0, corte_superior=0.0, padding=0.0):
    x0, y0, x1, y1 = caja
    if padding:
        # las cajas detectadas por contenido abrazan el dibujo: se amplían
        px, py = (x1 - x0) * padding, (y1 - y0) * padding
        x0, y0, x1, y1 = x0 - px, y0 - py, x1 + px, y1 + py
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(im.width, x1), min(im.height, y1)
    dx, dy = (x1 - x0) * inset, (y1 - y0) * inset
    x0, y0, x1, y1 = x0 + dx, y0 + dy, x1 - dx, y1 - dy
    if corte_superior:
        y0 = y0 + (y1 - y0) * corte_superior
    if corte_inferior:
        y1 = y1 - (y1 - y0) * corte_inferior
    return im.crop((int(x0), int(y0), int(x1), int(y1)))


def ajustar_a_contenido(im, margen=0.12):
    """
    Encaja el objeto dentro del recorte: elimina bordes de tarjeta y centra.
    Usa la máscara de tinta para encontrar el objeto y deja un margen parejo.
    """
    mask = mascara_tinta(im)
    ys, xs = np.where(mask)
    if len(xs) < 50:
        return im
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    w, h = x1 - x0, y1 - y0
    lado = int(max(w, h) * (1 + margen * 2))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    lienzo.paste(im.crop((max(0, cx - lado // 2), max(0, cy - lado // 2),
                          max(0, cx - lado // 2) + lado, max(0, cy - lado // 2) + lado)),
                 (0, 0))
    return lienzo


def limpiar_bordes(im, banda=0.14):
    """
    Pone en blanco los grises muy claros del borde del recorte: son restos de la
    tarjeta vecina. No toca los pixeles con color ni el dibujo (que va centrado).
    """
    a = np.array(im.convert("RGB")).astype(np.int16)
    alto, ancho = a.shape[:2]
    bx, by = int(ancho * banda), int(alto * banda)
    mx, mn = a.max(axis=2), a.min(axis=2)
    luz = a.mean(axis=2)
    gris_claro = ((mx - mn) < 20) & (luz > 195) & (luz < 252)
    mascara = np.zeros((alto, ancho), dtype=bool)
    mascara[:by, :] = True
    mascara[alto - by:, :] = True
    mascara[:, :bx] = True
    mascara[:, ancho - bx:] = True
    a[gris_claro & mascara] = [255, 255, 255]
    return Image.fromarray(a.astype(np.uint8))


def a_cuadrado(im, fondo=(255, 255, 255)):
    """Centra el recorte en un lienzo cuadrado blanco (sin deformar)."""
    lado = max(im.width, im.height)
    lienzo = Image.new("RGB", (lado, lado), fondo)
    lienzo.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2))
    return lienzo.resize((TAM, TAM), Image.LANCZOS)


def reencuadrar(im, caja, margen=0.12, abajo=False):
    """
    Recorta la celda y encaja el objeto principal: se queda con la mancha de
    tinta más grande de la celda (el dibujo) e ignora los marcos y etiquetas,
    que son trazos finos de poca área.
    """
    celda = im.crop(caja)
    mask = mascara_tinta(celda)
    piezas = etiquetar(mask)
    if not piezas:
        return None
    x0, y0, x1, y1, _ = max(piezas, key=lambda c: c[4])
    lado = int(max(x1 - x0, y1 - y0) * (1 + margen))
    lado = min(lado, celda.width, celda.height)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    x0b = min(max(0, cx - lado // 2), celda.width - lado)
    if abajo:
        y0b = min(max(0, y1 - lado), celda.height - lado)
    else:
        y0b = min(max(0, cy - lado // 2), celda.height - lado)
    trozo = celda.crop((x0b, y0b, x0b + lado, y0b + lado))
    return preparar(trozo)


def recorte_directo(im, caja, margen=0.04, alinear="centro"):
    """
    Recorta exactamente la caja indicada y la centra en un lienzo cuadrado con
    relleno blanco. Así no se traen píxeles de las celdas vecinas.
    """
    x0, y0, x1, y1 = caja
    dx, dy = int((x1 - x0) * margen), int((y1 - y0) * margen)
    caja2 = (max(0, x0 - dx), max(0, y0 - dy), min(im.width, x1 + dx), min(im.height, y1 + dy))
    trozo = im.crop(caja2)
    return preparar(trozo)


def preparar(trozo):
    """Cadena completa de limpieza + normalización de un recorte."""
    return normalizar(quitar_texto_flotante(recortar_etiquetas(quitar_bordes_celda(trozo))))


def toca_borde(im, margen=3):
    mask = mascara_tinta(im)
    piezas = etiquetar(mask)
    if not piezas:
        return False
    x0, y0, x1, y1, _ = max(piezas, key=lambda c: c[4])
    return x0 <= margen or y0 <= margen or x1 >= im.width - margen or y1 >= im.height - margen


def recortar_etiquetas(im, tope=0.42):
    """
    Quita las franjas de texto de la hoja (van encima o debajo del dibujo).
    Trabaja por BANDAS: una banda es un grupo de filas con tinta seguido de
    filas vacías. Se descarta la primera/última banda si no tiene nada de color
    (el texto nunca aporta color) y es baja.
    """
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    alto, ancho = a.shape[:2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = mx - mn
    oscuro = ((sat < 60) & (a.mean(axis=2) < 170)).sum(axis=1)
    color = (sat > 60).sum(axis=1)
    con_tinta = (oscuro + color) > 0

    bandas = []
    y = 0
    while y < alto:
        if con_tinta[y]:
            ini_b = y
            while y < alto and con_tinta[y]:
                y += 1
            bandas.append((ini_b, y - 1))
        else:
            y += 1
    if not bandas:
        return im

    def es_texto(banda):
        b0, b1 = banda
        return color[b0:b1 + 1].sum() == 0 and (b1 - b0 + 1) < alto * 0.16

    y0, y1 = 0, alto - 1
    if bandas and es_texto(bandas[0]) and bandas[0][0] < alto * tope:
        y0 = bandas[1][0] if len(bandas) > 1 else bandas[0][1] + 1
    if bandas and es_texto(bandas[-1]) and bandas[-1][0] > alto * (1 - tope):
        y1 = bandas[-2][1] if len(bandas) > 1 else bandas[-1][0] - 1
    if y1 - y0 < alto * 0.35:
        return im
    return im.crop((0, y0, ancho, y1 + 1))


def quitar_texto_flotante(im, banda=0.30):
    """
    Borra los trazos oscuros sin color que flotan sobre blanco (etiquetas que
    se solapan con el dibujo). Se respeta el contorno del dibujo porque se pide
    que el entorno sea mayoritariamente blanco.
    """
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    alto, ancho = a.shape[:2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    luz = a.mean(axis=2)
    sat = mx - mn
    candidato = (sat < 60) & (luz < 170)
    candidato[int(alto * banda):, :] = False
    if not candidato.any():
        return im

    # entorno: se dilata el blanco y se exige que rodee al trazo
    blanco = (luz > 243) & (sat < 25)
    entorno = np.zeros_like(blanco)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            if dy == 0 and dx == 0:
                continue
            entorno |= np.roll(np.roll(blanco, dy, axis=0), dx, axis=1)
    quitar = candidato & entorno
    base = np.array(im.convert("RGB"))
    base[quitar] = [255, 255, 255]
    return Image.fromarray(base)


def quitar_bordes_celda(im, margen=2):
    """
    Borra los trazos finos que tocan el borde del recorte (corchetes y líneas
    decorativas que la hoja dibuja en las esquinas de cada tarjeta).
    """
    W, H = im.size
    mask = mascara_tinta(im)
    piezas = etiquetar(mask)
    if not piezas:
        return im
    area_principal = max(c[4] for c in piezas)
    base = np.array(im.convert("RGB"))
    tocado = False
    for x0, y0, x1, y1, area in piezas:
        ancho, alto = max(1, x1 - x0), max(1, y1 - y0)
        relleno = area / float(ancho * alto)
        toca = x0 <= margen or y0 <= margen or x1 >= W - margen or y1 >= H - margen
        fino = relleno < 0.35 or max(ancho, alto) / float(min(ancho, alto)) > 6
        if toca and fino and area < area_principal * 0.6:
            base[max(0, y0 - 1):y1 + 1, max(0, x0 - 1):x1 + 1] = [255, 255, 255]
            tocado = True
    if not tocado:
        return im
    limpia = Image.fromarray(base)
    # si se ha borrado demasiado, no se aplica
    if mascara_tinta(limpia).sum() < mascara_tinta(im).sum() * 0.55:
        return im
    return limpia


def agrupar_dibujo(im):
    """
    Caja del dibujo completo: el objeto principal más las piezas que lo tocan
    (gotas, lápices, adornos). Se descartan marcos, líneas sueltas y etiquetas.
    """
    W, H = im.size
    mask = mascara_tinta(im)
    piezas = etiquetar(mask)
    if not piezas:
        return (0, 0, W, H)
    gris = np.asarray(im.convert("L")).astype(np.int16)

    def es_tenue(c):
        x0, y0, x1, y1, area = c
        trozo_m = mask[y0:y1, x0:x1]
        if not trozo_m.any():
            return True
        return float(gris[y0:y1, x0:x1][trozo_m].mean()) > 200

    def es_marco(c):
        x0, y0, x1, y1, area = c
        ancho, alto = x1 - x0, y1 - y0
        cubre = (ancho * alto) / float(W * H)
        relleno = area / float(max(1, ancho * alto))
        return cubre > 0.80 and relleno < 0.28

    def es_linea(c):
        x0, y0, x1, y1, area = c
        ancho, alto = max(1, x1 - x0), max(1, y1 - y0)
        largo, corto = max(ancho, alto), min(ancho, alto)
        alargado = largo / float(corto) > 8 and area < (W * H) * 0.03
        hueco = (area / float(ancho * alto)) < 0.16 and area < (W * H) * 0.05
        return alargado or hueco

    utiles = [c for c in piezas if not es_marco(c) and not es_linea(c) and not es_tenue(c)] or piezas
    principal = max(utiles, key=lambda c: c[4])
    px0, py0, px1, py1, parea = principal

    x0, y0, x1, y1 = px0, py0, px1, py1
    usadas = {id(principal)}
    cambio = True
    while cambio:
        cambio = False
        for c in utiles:
            if id(c) in usadas or es_linea(c):
                continue
            cx0, cy0, cx1, cy1, area = c
            ix = (x1 - x0) * 0.06 + 4
            iy = (y1 - y0) * 0.06 + 4
            pegado = not (cx1 < x0 - ix or cx0 > x1 + ix or cy1 < y0 - iy or cy0 > y1 + iy)
            if pegado or area >= parea * 0.30:
                usadas.add(id(c))
                x0, y0 = min(x0, cx0), min(y0, cy0)
                x1, y1 = max(x1, cx1), max(y1, cy1)
                cambio = True
    return (int(x0), int(y0), int(x1), int(y1))


def normalizar(im, margen=0.10):
    """
    Deja el dibujo centrado y con margen garantizado:
      1. caja del dibujo (agrupar_dibujo)
      2. se recorta y se pega centrada en un lienzo cuadrado con relleno blanco
         (nunca se amplía hacia los vecinos de la hoja)
      3. se borran las manchas que no forman parte del dibujo (etiquetas)
    """
    W, H = im.size
    x0, y0, x1, y1 = agrupar_dibujo(im)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return a_cuadrado(im).resize((512, 512), Image.LANCZOS)

    # borrar lo que no es dibujo (texto de la hoja, motas)
    piezas = etiquetar(mascara_tinta(im))
    base = np.array(im.convert("RGB"))
    limpia = im
    if piezas:
        area_principal = max(c[4] for c in piezas)
        for cx0, cy0, cx1, cy1, area in piezas:
            if area >= area_principal * 0.25:
                continue                      # pieza importante: no se toca
            dentro = (cx0 >= x0 - 2 and cx1 <= x1 + 2 and cy0 >= y0 - 2 and cy1 <= y1 + 2)
            if not dentro:
                base[max(0, cy0 - 1):cy1 + 1, max(0, cx0 - 1):cx1 + 1] = [255, 255, 255]
        candidata = Image.fromarray(base)
        # si tras limpiar queda casi vacia, se descarta la limpieza
        if mascara_tinta(candidata).sum() >= mascara_tinta(im).sum() * 0.55:
            limpia = candidata

    # se recorta EXACTAMENTE el dibujo: el margen lo aporta el lienzo blanco,
    # así no entran los trazos tenues que rodean al objeto en la hoja
    recorte = limpia.crop((x0, y0, x1, y1))
    bw, bh = recorte.size
    lado = int(max(bw, bh) * (1 + margen * 2))
    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    lienzo.paste(recorte, ((lado - bw) // 2, (lado - bh) // 2))
    # limpiar trazos tenues (marcos punteados) en el anillo exterior
    arr = np.asarray(lienzo.convert("RGB")).astype(np.int16)
    alto_l, ancho_l = arr.shape[:2]
    mx_l = arr.max(axis=2)
    mn_l = arr.min(axis=2)
    luz_l = arr.mean(axis=2)
    tenue = ((mx_l - mn_l) < 22) & (luz_l > 195) & (luz_l < 250)
    bx, by = int(ancho_l * 0.10), int(alto_l * 0.10)
    anillo = np.zeros((alto_l, ancho_l), dtype=bool)
    anillo[:by, :] = True
    anillo[alto_l - by:, :] = True
    anillo[:, :bx] = True
    anillo[:, ancho_l - bx:] = True
    arr[tenue & anillo] = [255, 255, 255]
    lienzo = Image.fromarray(arr.astype(np.uint8))

    if toca_borde(lienzo):
        # el dibujo llenaba el recorte: se reduce para dejar aire
        dentro = lienzo.resize((int(lado * 0.86), int(lado * 0.86)), Image.LANCZOS)
        lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
        lienzo.paste(dentro, ((lado - dentro.width) // 2, (lado - dentro.height) // 2))
    return lienzo.resize((512, 512), Image.LANCZOS)


def hoja_verificacion(recortes, ruta, titulo, cols=6):
    celda, pie = 128, 26
    filas = (len(recortes) + cols - 1) // cols
    lienzo = Image.new("RGB", (cols * celda, filas * (celda + pie) + 40), "#FFFFFF")
    d = ImageDraw.Draw(lienzo)
    try:
        f_tit = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 18)
        f_pie = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 11)
    except Exception:
        f_tit = f_pie = ImageFont.load_default()
    d.text((10, 8), titulo, font=f_tit, fill="#2B2D42")
    for i, (palabra, im) in enumerate(recortes):
        x = (i % cols) * celda
        y = 40 + (i // cols) * (celda + pie)
        lienzo.paste(im.resize((celda - 8, celda - 8), Image.LANCZOS), (x + 4, y + 4))
        d.text((x + 6, y + celda - 2), palabra[:18], font=f_pie, fill="#2B2D42")
    lienzo.save(ruta)
    return ruta


# --------------------------------------------------------------------------- principal
def main():
    if not os.path.isdir(ORIGEN):
        print("No existe la carpeta img-ia", file=sys.stderr)
        return 2

    os.makedirs(DESTINO, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)

    creditos = {"fuente": "Ilustraciones propias generadas con IA",
                "licencia": "Uso propio (LangKids)",
                "aviso": "Sin atribución externa: son ilustraciones originales del proyecto.",
                "imagenes": {}}

    total, saltadas = 0, 0
    for archivo, spec in HOJAS.items():
        ruta = os.path.join(ORIGEN, archivo)
        if not os.path.exists(ruta):
            print("  falta la hoja %s" % archivo)
            continue
        im = Image.open(ruta).convert("RGB")
        if spec["modo"] == "auto":
            cajas = cajas_auto(im)
        elif spec["modo"] == "cartas":
            cajas = cajas_tarjetas(im)
        elif spec["modo"] == "proyeccion":
            cajas = cajas_proyeccion(im)
        else:
            cajas = cajas_grid(im, spec["cols"], spec["rows"])

        mapa = spec["mapa"]
        recortes = []
        print("\n%s  (%d tarjetas detectadas, %d palabras en el mapa)"
              % (archivo, len(cajas), len(mapa)))
        for i, caja in enumerate(cajas):
            palabra = mapa[i] if i < len(mapa) else None
            if not palabra:
                saltadas += 1
                continue
            es_contenido = spec.get("modo") in ("auto", "proyeccion", "cartas")
            cs = spec.get("corte_superior", 0.0)
            filas_cs = spec.get("corte_superior_filas")
            if filas_cs and spec.get("modo") == "grid":
                fila = i // spec["cols"]
                if fila < len(filas_cs):
                    cs = filas_cs[fila]
            trozo = recortar(im, caja,
                             inset=0.0 if es_contenido else spec.get("inset", 0.15),
                             corte_inferior=spec.get("corte_inferior", 0.0),
                             corte_superior=cs,
                             padding=spec.get('padding', 0.08) if es_contenido else 0.0)
            if palabra in LIMPIAR_FLOTANTE:
                cuadrada = normalizar(quitar_texto_flotante(
                    recortar_etiquetas(quitar_bordes_celda(trozo)), banda=1.0))
            else:
                cuadrada = preparar(trozo)
            salida = os.path.join(DESTINO, slug(palabra) + ".webp")
            cuadrada.save(salida, "WEBP", quality=88, method=6)
            creditos["imagenes"][palabra] = {
                "archivo": "assets/img/%s.webp" % slug(palabra),
                "autor": "LangKids (IA)",
                "licencia": "Uso propio",
                "origen": archivo,
            }
            recortes.append((palabra, cuadrada))
            total += 1

        if recortes:
            nombre = "ia-" + os.path.splitext(archivo)[0] + ".png"
            hoja_verificacion(recortes, os.path.join(DOCS, nombre),
                              "%s · %d recortes" % (archivo, len(recortes)))
            print("  verificación: docs/img/%s" % nombre)



    # reencuadres manuales (solo estas palabras)
    rehechas = 0
    trabajos = []
    for palabra, (hoja, caja) in REENCUADRE_CAJA.items():
        trabajos.append((palabra, hoja, caja))
    for palabra, (hoja, caja, alinear) in REENCUADRE_CAJA_ALINEADA.items():
        trabajos.append((palabra, hoja, ("alineada", caja, alinear)))
    for palabra, datos in REENCUADRE.items():
        hoja, fila, col, filas, cols = datos[:5]
        margen = datos[5] if len(datos) > 5 else 0.12
        trabajos.append((palabra, hoja, ("celda", fila, col, filas, cols, margen)))

    for palabra, hoja, ref in trabajos:
        ruta_hoja = os.path.join(ORIGEN, hoja)
        if not os.path.exists(ruta_hoja):
            continue
        im = Image.open(ruta_hoja).convert("RGB")
        if isinstance(ref, tuple) and ref and ref[0] == "alineada":
            nueva = recorte_directo(im, ref[1], alinear=ref[2])
        elif isinstance(ref, tuple) and ref and ref[0] == "celda":
            _, fila, col, filas, cols, margen = ref
            w, h = im.width / float(cols), im.height / float(filas)
            caja = (int(col * w), int(fila * h), int((col + 1) * w), int((fila + 1) * h))
            nueva = reencuadrar(im, caja, margen, abajo=(palabra in REENCUADRE_ABAJO))
        else:
            nueva = recorte_directo(im, ref)
        if nueva is None:
            print("  reencuadre sin objeto:", palabra)
            continue
        nueva.save(os.path.join(DESTINO, slug(palabra) + ".webp"), "WEBP", quality=88, method=6)
        creditos["imagenes"].setdefault(palabra, {})
        creditos["imagenes"][palabra].update({
            "archivo": "assets/img/%s.webp" % slug(palabra),
            "autor": "LangKids (IA)", "licencia": "Uso propio",
            "origen": hoja, "nota": "reencuadrada a mano",
        })
        rehechas += 1
    print("reencuadradas a mano: %d" % rehechas)

    # copias de ilustraciones compartidas
    import shutil
    for destino_palabra, origen_palabra in COPIAS.items():
        origen = os.path.join(DESTINO, slug(origen_palabra) + ".webp")
        destino = os.path.join(DESTINO, slug(destino_palabra) + ".webp")
        if os.path.exists(origen):
            shutil.copyfile(origen, destino)
            creditos["imagenes"][destino_palabra] = dict(creditos["imagenes"].get(origen_palabra, {}))
            creditos["imagenes"][destino_palabra]["archivo"] = "assets/img/%s.webp" % slug(destino_palabra)
            creditos["imagenes"][destino_palabra]["nota"] = "misma ilustración que «%s»" % origen_palabra

    with open(CREDITS, "w", encoding="utf-8") as f:
        json.dump(creditos, f, ensure_ascii=False, indent=1)
    with open(os.path.join(APP, "www", "content", "credits.js"), "w", encoding="utf-8") as f:
        f.write("/* Generado por tools/import_ia_images.py */\n")
        f.write("window.LANGKIDS_CREDITS = ")
        json.dump(creditos, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print("\nTotal importadas: %d · celdas descartadas: %d" % (total, saltadas))
    print("Créditos: %d imágenes" % len(creditos["imagenes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
