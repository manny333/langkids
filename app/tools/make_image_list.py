# -*- coding: utf-8 -*-
"""
make_image_list.py — Genera la lista de imágenes que necesita la app, para
poder crearlas en otro sitio (generador de imágenes, ilustrador, banco propio).

Salida:
    docs/Imagenes-para-crear.txt    lista legible (copiar/pegar + nombres)
    docs/imagenes-para-crear.csv    la misma lista en tabla, para seguimiento

Uso:  python app/tools/make_image_list.py
"""

import csv
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
LESSONS = os.path.join(APP, "content", "lessons.json")
SALIDA_TXT = os.path.join(RAIZ, "docs", "Imagenes-para-crear.txt")
SALIDA_CSV = os.path.join(RAIZ, "docs", "imagenes-para-crear.csv")

# ---------------------------------------------------------------------------
# Taxonomía del vocabulario: qué merece una imagen y en qué grupo va.
# (Los nombres deben coincidir con el vocabulario del currículo.)
# ---------------------------------------------------------------------------
GRUPOS = [
    ("ANIMALES", [
        "cat", "dog", "bird", "fish", "rabbit", "cow", "pig", "horse", "duck",
        "sheep", "lion", "tiger", "elephant", "monkey", "giraffe", "snake",
        "crocodile", "penguin", "bear", "zebra", "spiders",
    ]),
    ("COMIDA Y BEBIDA", [
        "apple", "banana", "orange", "grapes", "strawberry", "milk", "water",
        "juice", "bread", "cheese", "egg", "rice", "chicken", "salad", "cake",
        "ice cream", "sandwich",
    ]),
    ("ROPA", [
        "t-shirt", "trousers", "dress", "skirt", "shoes", "socks", "hat",
        "jacket", "shorts", "scarf",
    ]),
    ("CASA", [
        "house", "bedroom", "kitchen", "bathroom", "living room", "garden",
        "bed", "table", "sofa", "tv", "fridge", "door", "window",
    ]),
    ("AULA Y ÚTILES", [
        "pencil", "pen", "crayon", "book", "notebook", "ruler", "rubber",
        "scissors", "bag", "desk", "chair", "board",
    ]),
    ("JUGUETES", ["ball", "doll", "teddy bear", "train", "kite", "bike", "blocks"]),
    ("CUERPO", [
        "head", "hair", "eyes", "ears", "nose", "mouth", "teeth", "hands",
        "arms", "legs", "feet", "tummy",
    ]),
    ("TRANSPORTE", ["bus", "car", "plane", "boat", "taxi", "underground"]),
    ("LUGARES", [
        "school", "park", "hospital", "supermarket", "library", "cinema",
        "museum", "bank", "café", "shop", "street", "square",
    ]),
    ("NATURALEZA Y CLIMA", [
        "mountain", "ocean", "desert", "jungle", "sunny", "rainy", "cloudy",
        "windy", "snowy", "stormy", "foggy", "spring", "summer", "autumn",
        "winter",
    ]),
    ("DEPORTES", ["football", "basketball", "tennis"]),
    ("COLORES Y FORMAS", [
        "red", "blue", "yellow", "green", "orange", "purple", "pink", "brown",
        "black", "white",
    ]),
]

# Lo que NO necesita imagen: se queda con emoji para siempre.
NO_APLICA = {
    "hello", "hi", "goodbye", "bye-bye", "good morning", "good afternoon",
    "happy", "sad", "angry", "sleepy", "hungry", "thirsty", "fine",
    "please", "thank you", "sorry", "name", "boy", "girl", "friend",
    "mummy", "daddy", "sister", "brother", "baby", "grandma", "grandpa",
    "family", "love", "like", "don't like", "can", "can't", "was", "were",
    "went", "came", "going to", "will", "won't", "how many", "count",
    "maybe", "perhaps", "sure", "of course", "the biggest", "the fastest",
    "the most dangerous", "more interesting", "more dangerous",
    "good-better-best", "bigger", "taller", "faster", "heavier", "lighter",
    "first", "then", "next", "finally", "suddenly", "once upon a time",
    "happy ending", "in", "on", "under", "where", "next to", "between",
    "opposite", "behind", "in front of", "near", "turn left", "turn right",
    "go straight", "o'clock", "half past", "today", "tomorrow", "tonight",
    "yesterday", "last night", "last week", "last weekend", "next week",
    "next month", "next year", "ago", "soon", "plan", "idea", "beginning",
    "middle", "end", "narrator", "presentation", "project", "big", "small",
    "cute", "old", "young", "fast", "slow", "tall", "short", "thin",
    "strong", "curly", "straight", "long", "fair", "dark", "kind", "funny",
    "friendly", "shy", "brave", "clever", "beautiful", "yummy", "weather",
    "age", "spell", "alphabet", "letter", "favorite", "degrees", "hobby",
    "free time", "nationality", "population", "continent", "capital",
}


# Aclaración en español para las palabras que pueden confundirse al crear la imagen.
GLOSA = {
    "lion": "león", "tiger": "tigre", "elephant": "elefante", "monkey": "mono",
    "giraffe": "jirafa", "snake": "serpiente", "crocodile": "cocodrilo",
    "penguin": "pingüino", "bear": "oso", "zebra": "cebra",
    "spiders": "araña (el plan dice «spiders» en plural)",
    "ice cream": "helado", "sandwich": "sándwich", "cheese": "queso",
    "rice": "arroz", "chicken": "pollo", "salad": "ensalada",
    "grapes": "uvas", "strawberry": "fresa", "juice": "zumo",
    "t-shirt": "camiseta", "trousers": "pantalón", "dress": "vestido",
    "skirt": "falda", "shoes": "zapatos", "socks": "calcetines",
    "hat": "sombrero", "jacket": "chaqueta", "shorts": "pantalón corto",
    "scarf": "bufanda",
    "house": "casa", "bedroom": "dormitorio", "kitchen": "cocina",
    "bathroom": "baño", "living room": "sala de estar", "garden": "jardín",
    "bed": "cama", "table": "mesa", "sofa": "sofá", "fridge": "nevera",
    "door": "puerta", "window": "ventana",
    "pencil": "lápiz", "pen": "bolígrafo", "crayon": "cera de color",
    "notebook": "cuaderno", "ruler": "regla", "rubber": "goma de borrar",
    "scissors": "tijeras", "bag": "mochila", "desk": "escritorio", "book": "libro", "tv": "televisor",
    "chair": "silla", "board": "pizarra",
    "ball": "pelota", "doll": "muñeca", "teddy bear": "oso de peluche",
    "train": "tren", "kite": "cometa", "bike": "bicicleta",
    "blocks": "bloques de construcción",
    "head": "cabeza", "hair": "pelo", "eyes": "ojos", "ears": "orejas",
    "nose": "nariz", "mouth": "boca", "teeth": "dientes", "hands": "manos",
    "arms": "brazos", "legs": "piernas", "feet": "pies", "tummy": "barriga",
    "bus": "autobús", "plane": "avión", "boat": "barco", "taxi": "taxi",
    "underground": "metro subterráneo (subway)",
    "school": "escuela", "park": "parque", "hospital": "hospital",
    "supermarket": "supermercado", "library": "biblioteca", "cinema": "cine",
    "museum": "museo", "bank": "banco", "café": "cafetería",
    "shop": "tienda", "street": "calle", "square": "plaza",
    "mountain": "montaña", "ocean": "océano", "desert": "desierto",
    "jungle": "selva", "sunny": "soleado", "rainy": "lluvioso",
    "cloudy": "nublado", "windy": "con viento", "snowy": "nevado",
    "stormy": "tormentoso", "foggy": "con niebla", "spring": "primavera",
    "summer": "verano", "autumn": "otoño", "winter": "invierno",
    "football": "fútbol", "basketball": "baloncesto", "tennis": "tenis",
    "red": "rojo", "blue": "azul", "yellow": "amarillo", "green": "verde",
    "purple": "morado", "pink": "rosa", "brown": "marrón", "black": "negro",
    "white": "blanco",
}


def slug(palabra):
    return re.sub(r"[^a-z0-9]+", "-", palabra.strip().lower()).strip("-")


def main():
    with open(LESSONS, encoding="utf-8") as f:
        contenido = json.load(f)

    # palabras únicas del currículo, con la unidad donde aparecen
    catalogo = {}
    for nivel in contenido["levels"]:
        for unidad in nivel["units"]:
            for w in unidad["words"]:
                clave = w["en"].strip().lower()
                if clave not in catalogo:
                    catalogo[clave] = {
                        "palabra": w["en"],
                        "unidad": unidad["id"],
                        "img": w.get("img"),
                    }

    # clasificación
    filas = []
    en_grupo = set()
    for grupo, palabras in GRUPOS:
        for p in palabras:
            clave = p.strip().lower()
            if clave in en_grupo:      # ya clasificada en un grupo anterior
                continue
            en_grupo.add(clave)
            datos = catalogo.get(clave)
            filas.append({
                "grupo": grupo,
                "palabra": datos["palabra"] if datos else p,
                "clave": clave,
                "unidad": datos["unidad"] if datos else "—",
                "archivo": slug(p) + ".png",
                "estado": "LISTA" if (datos and datos["img"]) else "FALTA",
                "en_curriculo": bool(datos),
            })

    faltan = [f for f in filas if f["estado"] == "FALTA"]
    listas = [f for f in filas if f["estado"] == "LISTA"]
    opcionales = sorted(k for k in catalogo
                        if k not in en_grupo and k not in NO_APLICA)
    sin_clasificar = [f for f in filas if not f["en_curriculo"]]

    # ---------------------------------------------------------------- TXT
    out = []
    a = out.append
    a("LISTA DE IMÁGENES · LANGKIDS ENGLISH")
    a("=" * 60)
    a("")
    a("CÓMO USAR ESTA LISTA")
    a("-" * 60)
    a("1. Crea o consigue cada imagen que aparece abajo.")
    a("2. Formato ideal: cuadrado, 512x512 px, PNG con fondo transparente o blanco,")
    a("   un solo objeto centrado, sin texto y sin personas reales identificables.")
    a("3. Guarda el archivo con el NOMBRE EXACTO de la columna derecha")
    a("   (por ejemplo  apple.png ).  Se aceptan .png, .jpg, .webp y .svg.")
    a("4. Déjalas todas en la carpeta:   app\\www\\assets\\img\\")
    a("5. Reconstruye la app:")
    a("       python app\\tools\\gen_content.py")
    a("       pwsh -File app\\tools\\build-apk.ps1")
    a("   La app detecta la imagen sola. Si una palabra no tiene imagen, muestra su emoji:")
    a("   no se rompe nada y se pueden añadir de a poco.")
    a("")
    a("RESUMEN")
    a("-" * 60)
    a("  Imágenes por crear (sin foto todavía):  %d" % len(faltan))
    a("  Imágenes que ya existen:               %d" % len(listas))
    a("  Palabras opcionales (no críticas):     %d" % len(opcionales))
    a("  Palabras que NO necesitan imagen:      %d  (usan emoji a propósito)" % len(NO_APLICA))
    a("")
    a("")
    a("1) LISTA RÁPIDA — para pegar en un generador de imágenes")
    a("-" * 60)
    a(", ".join(f["palabra"] for f in faltan))
    a("")
    a("")
    a("2) LISTA POR CATEGORÍA, CON NOMBRE DE ARCHIVO")
    a("-" * 60)
    for grupo, _ in GRUPOS:
        del_grupo = [f for f in filas if f["grupo"] == grupo]
        if not del_grupo:
            continue
        a("")
        a("%s  (%d)" % (grupo, len(del_grupo)))
        for f in del_grupo:
            estado = "" if f["estado"] == "FALTA" else "   [ya está]"
            glosa = GLOSA.get(f["clave"], "")
            extra = ("   (" + glosa + ")") if glosa else ""
            a("   %-16s ->  %s%s%s" % (f["palabra"], f["archivo"], extra, estado))
    a("")
    a("")
    a("3) YA LAS TENGO — no hace falta repetirlas")
    a("-" * 60)
    a(", ".join(f["palabra"] for f in listas))
    a("")
    a("")
    a("4) OPCIONALES — si quieres ir más allá")
    a("-" * 60)
    a("Números, meses, días, países, acciones y adjetivos: se entienden mejor con")
    a("símbolos o ilustraciones simples que con fotos, por eso no están en la lista principal.")
    a("")
    a(", ".join(opcionales))
    a("")
    a("")
    a("5) NO NECESITAN IMAGEN (usan emoji)")
    a("-" * 60)
    a("Saludos, emociones, gramática y palabras abstractas. Buscar fotos para ellas")
    a("da resultados absurdos (un pájaro para «hello»), así que se quedan con emoji.")
    a("")
    a(", ".join(sorted(NO_APLICA)))
    a("")
    if sin_clasificar:
        a("")
        a("NOTA: %s de la lista no aparecen en el currículo actual (puedes ignorarlas)."
          % len(sin_clasificar))
    a("")
    a("=" * 60)
    a("Generado por app\\tools\\make_image_list.py")

    os.makedirs(os.path.dirname(SALIDA_TXT), exist_ok=True)
    with open(SALIDA_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    # ---------------------------------------------------------------- CSV
    with open(SALIDA_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["grupo", "palabra", "archivo", "unidad", "estado"])
        for fila in filas:
            w.writerow([fila["grupo"], fila["palabra"], fila["archivo"],
                        fila["unidad"], fila["estado"]])

    print("TXT: %s" % SALIDA_TXT)
    print("CSV: %s" % SALIDA_CSV)
    print("por crear: %d | ya estan: %d | opcionales: %d | no aplica: %d"
          % (len(faltan), len(listas), len(opcionales), len(NO_APLICA)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
