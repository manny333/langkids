# -*- coding: utf-8 -*-
"""
gen_content.py — Convierte el plan de temas de LangKids (Markdown) en el contenido
de la app (lessons.json): 4 niveles, 16 unidades, 80 clases con sus actividades.

Uso:
    python gen_content.py
"""

import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
PLAN_MD = os.path.join(RAIZ, "Plan-de-Temas-LangKids-Niveles-1-a-4.md")
SALIDA = os.path.join(os.path.dirname(AQUI), "content", "lessons.json")

# --------------------------------------------------------------------------- emojis
# Diccionario palabra -> emoji. Es el "arte" de la app: sin imagenes externas.
EMOJI = {
    # --- saludos, personas, emociones
    "hello": "👋", "hi": "🙋", "goodbye": "👋", "bye-bye": "🙋", "good morning": "🌅",
    "good afternoon": "🌤️", "teacher": "🧑‍🏫", "boy": "👦", "girl": "👧", "friend": "🧑‍🤝‍🧑",
    "name": "🏷️", "happy": "😊", "sad": "😢", "angry": "😠", "sleepy": "😴", "hungry": "🍽️",
    "thirsty": "🥤", "fine": "👌", "thank you": "🙏", "please": "🙏", "sorry": "😔",
    "love": "❤️", "smile": "😄", "kind": "💛", "funny": "🤣", "friendly": "🤝", "shy": "🙈",
    "brave": "🦁", "clever": "🧠", "happy ending": "🎉",
    # --- colores
    "red": "🔴", "blue": "🔵", "yellow": "🟡", "green": "🟢", "orange": "🟠", "purple": "🟣",
    "pink": "🌸", "brown": "🟤", "black": "⚫", "white": "⚪", "color": "🎨",
    # --- numeros y contar
    "one": "1️⃣", "two": "2️⃣", "three": "3️⃣", "four": "4️⃣", "five": "5️⃣", "six": "6️⃣",
    "seven": "7️⃣", "eight": "8️⃣", "nine": "9️⃣", "ten": "🔟", "eleven": "1️⃣1️⃣",
    "twelve": "1️⃣2️⃣", "thirteen": "1️⃣3️⃣", "twenty": "2️⃣0️⃣",
    "how many": "🔢", "count": "🔢", "number": "🔢", "age": "🎂", "old": "👴",
    "crayon": "🖍️", "paint": "🎨", "balloon": "🎈", "blocks": "🧱",
    # --- cuerpo
    "head": "🙂", "hair": "💇", "eyes": "👀", "ears": "👂", "nose": "👃", "mouth": "👄",
    "teeth": "🦷", "hands": "🙌", "arms": "💪", "legs": "🦵", "feet": "🦶", "tummy": "🫃",
    # --- familia
    "mummy": "👩", "daddy": "👨", "sister": "👧", "brother": "👦", "baby": "👶",
    "grandma": "👵", "grandpa": "👴", "family": "👨‍👩‍👧‍👦",
    # --- animales
    "cat": "🐱", "dog": "🐶", "bird": "🐦", "fish": "🐟", "rabbit": "🐰", "cow": "🐮",
    "pig": "🐷", "horse": "🐴", "duck": "🦆", "sheep": "🐑", "lion": "🦁", "tiger": "🐯",
    "elephant": "🐘", "monkey": "🐵", "giraffe": "🦒", "snake": "🐍", "crocodile": "🐊",
    "penguin": "🐧", "bear": "🐻", "zebra": "🦓", "spiders": "🕷️", "animal": "🐾",
    # --- juguetes
    "ball": "⚽", "doll": "🪆", "car": "🚗", "teddy bear": "🧸", "train": "🚂", "kite": "🪁",
    "bike": "🚲", "toy": "🧸",
    # --- tamaños y adjetivos
    "big": "🐘", "small": "🐜", "cute": "🥰", "fast": "⚡", "slow": "🐌", "tall": "🦒",
    "short": "🐧", "thin": "🥢", "strong": "💪", "young": "🧒", "curly": "🌀",
    "straight": "📏", "long": "📏", "fair": "🌟", "dark": "🌑", "glasses": "👓",
    "beard": "🧔", "moustache": "👨", "beautiful": "🌸", "interesting": "🤔",
    "dangerous": "⚠️", "heavier": "🏋️", "lighter": "🪶", "bigger": "🐘", "taller": "🦒",
    "faster": "⚡",
    # --- clima y estaciones
    "weather": "🌦️", "sunny": "☀️", "rainy": "🌧️", "cloudy": "☁️", "windy": "🌬️",
    "snowy": "❄️", "stormy": "⛈️", "foggy": "🌫️", "hot": "🔥", "warm": "🌤️", "cool": "😎",
    "cold": "🧊", "degrees": "🌡️", "spring": "🌷", "summer": "🏖️", "autumn": "🍂",
    "winter": "⛄", "today": "📅", "favorite": "⭐", "month": "📆", "birthday": "🎂",
    "birthday party": "🎉", "alphabet": "🔤", "letter": "🔤", "spell": "✍️",
    "monday-sunday": "📅", "the biggest": "🐳", "the fastest": "🏎️",
    "the most dangerous": "⚠️", "good-better-best": "🥇", "more interesting": "🤔",
    "more dangerous": "⚠️", "population": "👥", "reading": "📖", "painting": "🎨",
    "january": "1️⃣", "february": "2️⃣", "march": "3️⃣", "april": "4️⃣", "may": "5️⃣",
    "june": "6️⃣", "july": "7️⃣", "august": "8️⃣", "september": "9️⃣", "october": "🔟",
    "november": "1️⃣1️⃣", "december": "1️⃣2️⃣",
    # --- aula y casa
    "pencil": "✏️", "pen": "🖊️", "book": "📕", "notebook": "📓", "ruler": "📏",
    "rubber": "🧽", "scissors": "✂️", "bag": "🎒", "desk": "🪑", "chair": "🪑",
    "board": "📋", "door": "🚪", "window": "🪟", "house": "🏠", "bedroom": "🛏️",
    "kitchen": "🍳", "bathroom": "🛁", "living room": "🏡", "garden": "🌳", "bed": "🛏️",
    "table": "🪑", "sofa": "🛋️", "tv": "📺", "fridge": "🧊", "box": "📦",
    "open": "🔓", "close": "🔒", "put": "📍", "in": "📥", "on": "⬆️", "under": "⬇️",
    "where": "❓",
    # --- comida
    "apple": "🍎", "banana": "🍌", "grapes": "🍇", "strawberry": "🍓", "milk": "🥛",
    "water": "💧", "juice": "🧃", "bread": "🍞", "cheese": "🧀", "egg": "🥚", "rice": "🍚",
    "chicken": "🍗", "salad": "🥗", "cake": "🍰", "ice cream": "🍦", "sandwich": "🥪",
    "yummy": "😋", "food": "🍽️", "breakfast": "🥣", "lunch": "🍱", "dinner": "🍲",
    # --- ropa
    "t-shirt": "👕", "trousers": "👖", "dress": "👗", "skirt": "👗", "shoes": "👟",
    "socks": "🧦", "hat": "🎩", "jacket": "🧥", "shorts": "🩳", "scarf": "🧣",
    # --- acciones
    "run": "🏃", "jump": "🤸", "swim": "🏊", "fly": "🕊️", "climb": "🧗", "dance": "💃",
    "sing": "🎤", "read": "📖", "write": "✍️", "draw": "🖌️", "cook": "👨‍🍳", "ride": "🚴",
    "play": "⚽", "watch tv": "📺", "study": "📚", "help": "🤝", "buy": "🛒", "meet": "🤝",
    "travel": "✈️", "visit": "🚪", "act": "🎭", "acting": "🎭", "swimming": "🏊",
    "cycling": "🚴", "dancing": "💃", "reading": "📖", "painting": "🎨", "singing": "🎤",
    "cooking": "🍳", "writing": "✍️", "drawing": "🖌️",
    "wake up": "⏰", "get up": "🛌", "brush my teeth": "🪥", "wash my face": "🧼",
    "get dressed": "👕", "have breakfast": "🥣", "have lunch": "🍱", "have dinner": "🍲",
    "go to school": "🎒", "do homework": "📝", "go to bed": "😴",
    "o'clock": "🕐", "half past": "🕜", "morning": "🌅", "afternoon": "🌇",
    "evening": "🌆", "night": "🌙", "monday": "📅", "tuesday": "📅", "wednesday": "📅",
    "thursday": "📅", "friday": "📅", "saturday": "📅", "sunday": "📅",
    # --- ciudad y transporte
    "school": "🏫", "park": "🏞️", "hospital": "🏥", "supermarket": "🛒", "library": "📚",
    "cinema": "🎬", "museum": "🏛️", "bank": "🏦", "café": "☕", "shop": "🏪",
    "street": "🛣️", "square": "⛲", "bus": "🚌", "plane": "✈️", "boat": "⛵",
    "taxi": "🚕", "underground": "🚇", "next to": "↔️", "between": "↔️", "opposite": "🔄",
    "behind": "🔙", "in front of": "🔜", "near": "📍", "turn left": "⬅️",
    "turn right": "➡️", "go straight": "⬆️", "country": "🗺️", "nationality": "🛂",
    "spain": "🇪🇸", "england": "🇬🇧", "france": "🇫🇷", "italy": "🇮🇹", "japan": "🇯🇵",
    "brazil": "🇧🇷", "continent": "🌍", "ocean": "🌊", "mountain": "🏔️", "desert": "🏜️",
    "jungle": "🌴", "capital": "🏛️", "population": "👥",
    # --- deportes
    "football": "⚽", "basketball": "🏀", "tennis": "🎾", "hobby": "🎯",
    "free time": "🕐", "sport": "🏅",
    # --- pasado y futuro (verbos)
    "played": "⚽", "watched": "📺", "visited": "🚪", "cooked": "🍳", "cleaned": "🧹",
    "studied": "📚", "went": "🚶", "saw": "👀", "had": "✅", "ate": "🍽️", "drank": "🥤",
    "made": "🛠️", "took": "✋", "came": "🚶", "gave": "🎁", "was": "⏪", "were": "⏪",
    "yesterday": "⏪", "last night": "🌙", "last week": "📆", "last weekend": "📅",
    "ago": "⏳", "trip": "🧳", "holiday": "🏖️", "tomorrow": "⏩", "tonight": "🌙",
    "next week": "📆", "next month": "📆", "next year": "📅", "soon": "⏱️",
    "going to": "⏩", "will": "🔮", "won't": "🚫", "plan": "🗒️", "idea": "💡",
    "party": "🎉", "invitation": "💌", "maybe": "🤔", "perhaps": "🤔", "sure": "👍",
    "of course": "👍",
    # --- cuentos
    "story": "📖", "character": "🎭", "hero": "🦸", "villain": "🦹", "beginning": "▶️",
    "middle": "⏸️", "end": "⏹️", "first": "1️⃣", "then": "➡️", "next": "⏭️",
    "finally": "🏁", "suddenly": "💥", "once upon a time": "🏰", "narrator": "🎙️",
    "project": "📁", "presentation": "🎤",
    # --- verbos de habilidad y movimiento
    "can": "💪", "can't": "🚫", "like": "❤️", "don't like": "👎", "love it": "😍",
}

# Emoji de respaldo por unidad, cuando la palabra no esta en el diccionario.
FALLBACK_UNIDAD = {
    "1.1": "💬", "1.2": "🎨", "1.3": "🧍", "1.4": "🧸",
    "2.1": "🪪", "2.2": "🏠", "2.3": "🍎", "2.4": "🐾",
    "3.1": "⏰", "3.2": "🏙️", "3.3": "🧑", "3.4": "🌦️",
    "4.1": "⏪", "4.2": "⏩", "4.3": "🌍", "4.4": "📖",
}

# Alternativas para cuando dos palabras de la misma unidad comparten dibujo.
# En el juego de parejas dos imagenes iguales hacen la ronda ambigua, asi que
# cada palabra de una unidad debe tener un emoji distinto.
EMOJI_ALT = {
    "goodbye": ["🤚", "🖐️", "👋"],
    "bye-bye": ["🖐️", "🤚", "👋"],
    "hi": ["🙋", "😃"],
    "hello": ["👋", "😊"],
    "count": ["🧮", "🔢"],
    "how many": ["🔢", "🧮"],
    "age": ["🎈", "🔢"],
    "letter": ["🅰️", "🔠"],
    "alphabet": ["🔤", "🔠"],
    "chair": ["💺", "🪑"],
    "desk": ["🖥️", "🪑"],
    "table": ["🍽️", "🪵"],
    "bed": ["🛏️", "🛌"],
    "bedroom": ["🛌", "🛏️"],
    "sofa": ["🛋️", "💺"],
    "living room": ["🏡", "🪟"],
    "skirt": ["🩱", "👘"],
    "dress": ["👗", "👘"],
    "thank you": ["💐", "🥰"],
    "please": ["🙏", "🥺"],
    "big": ["🐳", "🐘"],
    "small": ["🐜", "🤏"],
    "elephant": ["🐘", "🦣"],
    "tall": ["🏢", "🦒"],
    "giraffe": ["🦒", "🦓"],
    "short": ["🤏", "🐧"],
    "penguin": ["🐧", "🐦"],
    "next to": ["↔️", "🤝"],
    "between": ["🔀", "↔️"],
    "straight": ["📏", "🧭"],
    "long": ["🧵", "📏"],
    "was": ["🕰️", "⏪"],
    "were": ["📜", "🕰️"],
    "yesterday": ["⏪", "🕰️"],
    "went": ["🚶", "🏃"],
    "came": ["🔙", "🚶"],
    "tomorrow": ["⏩", "🌅"],
    "going to": ["🔜", "⏩"],
    "next week": ["📆", "🗓️"],
    "next month": ["🗓️", "📆"],
    "next year": ["📅", "🗓️"],
    "meet": ["🤝", "👋"],
    "help": ["🆘", "🤝"],
    "maybe": ["🤔", "❓"],
    "perhaps": ["❓", "🤔"],
    "sure": ["👍", "✔️"],
    "of course": ["✔️", "👍"],
    "more dangerous": ["⚠️", "☠️"],
    "the most dangerous": ["☠️", "⚠️"],
    "the biggest": ["🐘", "🌍"],
    "the fastest": ["🏎️", "⚡"],
    "country": ["🗺️", "🌍"],
    "continent": ["🌍", "🗺️"],
    "story": ["📖", "📚"],
    "reading": ["📚", "📖"],
    "character": ["🎭", "👤"],
    "acting": ["🎬", "🎭"],
    "desk chair": ["🪑", "💺"],
    "in": ["📥", "⬇️"],
    "on": ["⬆️", "📌"],
    "under": ["⬇️", "🔽"],
}


# Emojis neutros para palabras sin dibujo propio que aun asi colisionan
GENERICOS = ["⭐", "📌", "🎯", "🧩", "🔹", "🎈", "🧷", "🌟", "📎", "🪄", "🔸", "🎁"]


def unicos_con_emoji(palabras, usados=None):
    """
    Deja cada palabra con un emoji distinto dentro de la lista (y de `usados`).
    Las palabras sin alternativa reservan su emoji primero; las que tienen
    alternativas (EMOJI_ALT) se resuelven despues, y como ultimo recurso se usa
    un emoji neutro del pool.
    """
    usados = set(usados or ())
    asignado = {}
    con_alt = lambda w: w["en"].strip().lower() in EMOJI_ALT
    orden = sorted(range(len(palabras)), key=lambda i: 1 if con_alt(palabras[i]) else 0)

    for i in orden:
        w = palabras[i]
        emoji = w["emoji"]
        if emoji in usados:
            for alt in EMOJI_ALT.get(w["en"].strip().lower(), []):
                if alt not in usados:
                    emoji = alt
                    break
            else:
                for g in GENERICOS:
                    if g not in usados:
                        emoji = g
                        break
        usados.add(emoji)
        asignado[i] = emoji

    return [{"en": w["en"], "emoji": asignado[i]} for i, w in enumerate(palabras)]

NIVEL_META = {    1: {"emoji": "🐣", "badge": "First Words Star", "badge_emoji": "⭐"},
    2: {"emoji": "🧭", "badge": "Little Explorer Badge", "badge_emoji": "🏅"},
    3: {"emoji": "🎤", "badge": "Young Speaker Award", "badge_emoji": "🏆"},
    4: {"emoji": "📚", "badge": "Story Maker Medal", "badge_emoji": "🥇"},
}

UNIDAD_EMOJI = {
    "1.1": "👋", "1.2": "🌈", "1.3": "👨‍👩‍👧", "1.4": "🐶",
    "2.1": "🪪", "2.2": "🏡", "2.3": "🍽️", "2.4": "🦁",
    "3.1": "🕐", "3.2": "🚌", "3.3": "🧑‍🎨", "3.4": "🌸",
    "4.1": "📅", "4.2": "🚀", "4.3": "🌍", "4.4": "🏰",
}

# Numeros que usa la actividad "¿Cuantos son?" (1-10)
NUMEROS_1_10 = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}


def emoji_de(palabra, unidad_id):
    """Busca el emoji de una palabra con normalizaciones razonables."""
    p = palabra.strip().lower().rstrip(".").strip()
    if not p:
        return FALLBACK_UNIDAD.get(unidad_id, "🔤")
    # 1) tal cual: "the biggest" debe encontrarse entero, sin quitar el articulo
    if p in EMOJI:
        return EMOJI[p]
    # 2) sin articulo o posesivo inicial
    q = re.sub(r"^(a|an|the|my|your|his|her|to)\s+", "", p)
    if q and q != p:
        if q in EMOJI:
            return EMOJI[q]
        p = q
    # 3) plural / singular
    if p.endswith("s") and p[:-1] in EMOJI:
        return EMOJI[p[:-1]]
    if p + "s" in EMOJI:
        return EMOJI[p + "s"]
    # 4) alguna de las palabras sueltas
    for parte in p.split():
        if parte in EMOJI:
            return EMOJI[parte]
    return FALLBACK_UNIDAD.get(unidad_id, "🔤")


# --------------------------------------------------------------------------- utilidades
def limpiar(t):
    return re.sub(r"\s+", " ", t.replace("**", "").strip())


def campo(linea, etiqueta):
    """Extrae el valor de una linea '**Etiqueta:** valor'."""
    m = re.match(r"\*\*%s:?\*\*\s*(.*)" % re.escape(etiqueta), linea.strip())
    return limpiar(m.group(1)) if m else None


def palabras_de(texto, unidad_id, limite=40):
    """Trocea una lista de vocabulario en palabras con su emoji."""
    palabras, vistas = [], set()
    for bruto in re.split(r",|·", texto):
        w = limpiar(bruto)
        if not w or len(w) > 34:
            continue
        clave = w.lower()
        if clave in vistas:
            continue
        vistas.add(clave)
        palabras.append({"en": w, "emoji": emoji_de(w, unidad_id)})
        if len(palabras) >= limite:
            break
    return palabras


def oracion_de(texto):
    """Convierte una estructura modelo en una frase ordenable (o None)."""
    if not texto:
        return None
    t = limpiar(texto)
    t = t.replace("«", "").replace("»", "")
    if "..." in t or "…" in t:            # "I went to... First... Then..." -> primera parte
        t = re.split(r"\.\.\.|…", t)[0]
    partes = [p.strip() for p in t.split(" / ") if p.strip()]
    if not partes:
        return None
    elegida = partes[0]
    if " — " in elegida:
        izq, der = elegida.split(" — ", 1)
        elegida = izq if len(izq.split()) >= 3 else der
    elegida = elegida.replace("___", "Ana").replace("…", " ").replace("...", " ")
    elegida = re.sub(r"\s+", " ", elegida).strip(" .")
    tokens = [w for w in elegida.split() if w]
    # quita palabras colgantes al final ("went to" -> "went")
    while len(tokens) > 3 and tokens[-1].lower().strip(",.;:!?") in (
            "to", "at", "in", "on", "and", "the", "a", "an", "my", "is", "are", "of"):
        tokens.pop()
    if not (3 <= len(tokens) <= 9):
        return None
    return " ".join(tokens)


# --------------------------------------------------------------------------- parser
def parsear_plan():
    with open(PLAN_MD, encoding="utf-8") as f:
        lineas = f.read().split("\n")

    niveles, nivel, unidad = [], None, None
    en_estructuras = False

    for linea in lineas:
        l = linea.strip()

        m = re.match(r"^###\s+NIVEL\s+(\d+)\s*·\s*(.+)$", l)
        if m:
            num = int(m.group(1))
            nivel = {
                "id": num, "name": m.group(2).strip().title(), "emoji": NIVEL_META[num]["emoji"],
                "badge": NIVEL_META[num]["badge"], "badgeEmoji": NIVEL_META[num]["badge_emoji"],
                "units": [],
            }
            niveles.append(nivel)
            unidad = None
            continue

        if nivel is None:
            continue

        m = re.match(r"^####\s+Unidad\s+([\d.]+)\s*—\s*(.+)$", l)
        if m:
            uid = m.group(1)
            unidad = {
                "id": uid, "title": m.group(2).strip(), "emoji": UNIDAD_EMOJI.get(uid, "📘"),
                "objective": "", "words": [], "structures": [], "classes": [],
                "song": "", "games": "", "materials": "", "phonics": "",
                "errores": [], "evaluation": "", "project": "",
            }
            nivel["units"].append(unidad)
            en_estructuras = False
            continue

        if unidad is None:
            for etq, clave in (("Edad recomendada", "age"), ("Nivel MCER", "cefr"),
                               ("Duración del nivel", "duration"), ("Meta del nivel", "goal"),
                               ("Proyecto de nivel", "levelProject")):
                v = campo(l, etq)
                if v:
                    nivel[clave] = v
            continue

        # ---- dentro de una unidad
        v = campo(l, "Objetivo comunicativo")
        if v:
            unidad["objective"] = v
            continue
        v = campo(l, "Vocabulario núcleo")
        if v:
            unidad["words"] = palabras_de(v, unidad["id"])
            continue
        v = campo(l, "Fonética")
        if v:
            unidad["phonics"] = v
            continue
        v = campo(l, "Canción y rutina")
        if v:
            unidad["song"] = v
            continue
        v = campo(l, "Juegos y dinámicas")
        if v:
            unidad["games"] = v
            continue
        v = campo(l, "Materiales")
        if v:
            unidad["materials"] = v
            continue
        v = campo(l, "Evaluación y evidencia")
        if v:
            unidad["evaluation"] = v
            continue
        v = campo(l, "Proyecto de unidad")
        if v:
            unidad["project"] = v
            continue

        if l.startswith("**Estructuras clave"):
            en_estructuras = True
            continue
        if en_estructuras and l.startswith("- "):
            # se guardan como objetos {en}: es el formato que consume la app
            unidad["structures"].append({"en": limpiar(l[2:])})
            continue
        if en_estructuras and l and not l.startswith("- "):
            en_estructuras = False

        m = re.match(r"^\|\s*\*\*Clase\s+(\d+)\*\*\s*\|(.+)\|\s*$", l)
        if m:
            celdas = [limpiar(c) for c in m.group(2).split("|")]
            if len(celdas) >= 5:
                unidad["classes"].append({
                    "n": int(m.group(1)), "focus": celdas[0], "vocab": celdas[1],
                    "structure": celdas[2], "activity": celdas[3], "evidence": celdas[4],
                })
            continue

    return niveles


# --------------------------------------------------------------------------- enriquecido
def palabras_de_clase(clase, unidad):
    """Palabras de una clase concreta (o todas las de la unidad en el repaso)."""
    texto = clase["vocab"].lower()
    if "repaso" in texto or not texto.strip():
        return list(unidad["words"])
    palabras = palabras_de(clase["vocab"], unidad["id"], limite=10)
    # completa con las palabras de la unidad que coincidan exactamente
    return palabras


def tareas_de_clase(clase, unidad, es_ultima):
    """Decide que actividades tendra la clase."""
    tareas = ["flashcards", "listen"]
    palabras = palabras_de_clase(clase, unidad)
    if len(palabras) >= 4:
        tareas.append("pairs")
    if oracion_de(clase["structure"]):
        tareas.append("sentence")
    # "¿Cuantos son?" solo si la clase trabaja numeros del 1 al 10
    if len([w for w in palabras if w["en"].strip().lower() in NUMEROS_1_10]) >= 3:
        tareas.append("count")
    if es_ultima:
        tareas.append("quiz")
    return tareas


WWW = os.path.join(os.path.dirname(AQUI), "www")


def slug_imagen(palabra):
    return re.sub(r"[^a-z0-9]+", "-", palabra.strip().lower()).strip("-")


# Dibujos diferentes pero que se ven casi iguales: se usa solo el primero.
PARECIDOS = [
    # hello, goodbye y bye-bye ya tienen ilustraciones propias y distintas,
    # asi que no se descarta ninguna.
    ("hello", "hi"),          # hi no tiene dibujo propio: se queda hello
]


def _huella(ruta):
    """Huella perceptual 8x8 de la imagen (para detectar dibujos casi iguales)."""
    try:
        from PIL import Image
        im = Image.open(ruta).convert("L").resize((8, 8), Image.LANCZOS)
        vals = list(im.getdata())
        prom = sum(vals) / float(len(vals))
        bits = 0
        for v in vals:
            bits = (bits << 1) | (1 if v > prom else 0)
        return bits
    except Exception:
        return None


def _distancia(a, b):
    return bin(a ^ b).count("1")


def adjuntar_imagenes(niveles):
    """
    Si existe una foto descargada para la palabra se añade el campo `img`.
    La interfaz usa la foto cuando está y cae al emoji cuando no: nunca queda
    un hueco. Devuelve cuántas palabras distintas tienen foto.
    """
    for nivel in niveles:
        for unidad in nivel["units"]:
            grupos = [unidad["words"]] + [c["words"] for c in unidad["classes"]]
            for grupo in grupos:
                for w in grupo:
                    if "img" in w:
                        continue
                    base = "assets/img/%s" % slug_imagen(w["en"])
                    for ext in (".webp", ".png", ".jpg", ".jpeg", ".svg"):
                        if os.path.exists(os.path.join(WWW, base + ext)):
                            w["img"] = base + ext
                            break
    # dentro de una unidad, dos palabras no pueden compartir dibujo:
    # en la actividad de parejas el juego se vuelve ambiguo
    import hashlib

    def _firma(ruta_abs):
        try:
            return hashlib.sha1(open(ruta_abs, "rb").read()).hexdigest()
        except Exception:
            return None

    for nivel in niveles:
        for unidad in nivel["units"]:
            firmas = set()
            for w in unidad["words"]:
                if "img" not in w:
                    continue
                firma = _firma(os.path.join(WWW, w["img"]))
                if firma and firma in firmas:
                    del w["img"]              # copia exacta: se queda con su emoji
                else:
                    firmas.add(firma)

            # pares de dibujos distintos pero visualmente casi iguales:
            # se conserva el primero y el segundo pasa a emoji
            presentes = {w["en"].strip().lower() for w in unidad["words"]}
            for conservar, descartar in PARECIDOS:
                if conservar in presentes and descartar in presentes:
                    for w in unidad["words"]:
                        if w["en"].strip().lower() == descartar:
                            w.pop("img", None)

            # sincronizar las listas de clase con lo decidido en la unidad
            por_palabra = {x["en"].strip().lower(): x.get("img") for x in unidad["words"]}
            for c in unidad["classes"]:
                for w in c["words"]:
                    k = w["en"].strip().lower()
                    if k in por_palabra:
                        if por_palabra[k]:
                            w["img"] = por_palabra[k]
                        else:
                            w.pop("img", None)

    con_foto = {w["img"] for n in niveles for u in n["units"] for w in u["words"] if "img" in w}
    return len(con_foto)


def enriquecer(niveles):
    for nivel in niveles:
        nivel.setdefault("age", "")
        nivel.setdefault("cefr", "")
        nivel.setdefault("goal", "")
        nivel.setdefault("levelProject", "")
        for unidad in nivel["units"]:
            # 1) vocabulario de la unidad: un emoji distinto por palabra
            unidad["words"] = unicos_con_emoji(unidad["words"])
            mapa = {w["en"].strip().lower(): w["emoji"] for w in unidad["words"]}
            emojis_unidad = [w["emoji"] for w in unidad["words"]]

            for i, clase in enumerate(unidad["classes"]):
                ultima = (i == len(unidad["classes"]) - 1)
                palabras = palabras_de_clase(clase, unidad)
                if palabras is unidad["words"] or palabras == unidad["words"]:
                    clase["words"] = list(unidad["words"])
                else:
                    # reutiliza el emoji ya asignado en la unidad y evita repetir
                    for w in palabras:
                        k = w["en"].strip().lower()
                        if k in mapa:
                            w["emoji"] = mapa[k]
                    clase["words"] = unicos_con_emoji(palabras, emojis_unidad)
                clase["sentence"] = oracion_de(clase["structure"])
                clase["tasks"] = tareas_de_clase(clase, unidad, ultima)
                clase["key"] = "%s.%d" % (unidad["id"], clase["n"])
            # preguntas del cuestionario de unidad
            unidad["quiz"] = [
                {"q": w["en"], "emoji": w["emoji"]} for w in unidad["words"][:12]
            ]
    return niveles


# --------------------------------------------------------------------------- validacion
def validar(niveles):
    errores = []
    if len(niveles) != 4:
        errores.append("Se esperaban 4 niveles y hay %d" % len(niveles))
    total_u = total_c = 0
    total_p = 0
    for n in niveles:
        if len(n["units"]) != 4:
            errores.append("Nivel %s: %d unidades" % (n["id"], len(n["units"])))
        for u in n["units"]:
            total_u += 1
            if not u["words"]:
                errores.append("Unidad %s sin vocabulario" % u["id"])
            if len(u["classes"]) != 5:
                errores.append("Unidad %s: %d clases" % (u["id"], len(u["classes"])))
            total_p += len(u["words"])
            # dos dibujos iguales hacen ambigua la actividad de parejas
            ims = [w.get("img") for w in u["words"] if w.get("img")]
            if len(set(ims)) != len(ims):
                errores.append("Unidad %s: imagenes repetidas" % u["id"])
            ems = [w["emoji"] for w in u["words"]]
            if len(set(ems)) != len(ems):
                repes = sorted({e for e in ems if ems.count(e) > 1})
                errores.append("Unidad %s: emojis repetidos %s" % (u["id"], repes))
            for c in u["classes"]:
                total_c += 1
                if not c["words"]:
                    errores.append("Clase %s sin palabras" % c["key"])
                if not c["tasks"]:
                    errores.append("Clase %s sin actividades" % c["key"])
                ims_c = [w.get("img") for w in c["words"] if w.get("img")]
                if len(set(ims_c)) != len(ims_c):
                    errores.append("Clase %s: imagenes repetidas" % c["key"])
                ems_c = [w["emoji"] for w in c["words"]]
                if len(set(ems_c)) != len(ems_c):
                    repes = sorted({e for e in ems_c if ems_c.count(e) > 1})
                    errores.append("Clase %s: emojis repetidos %s" % (c["key"], repes))
    return errores, total_u, total_c, total_p


# --------------------------------------------------------------------------- traduccion
def traducir_contenido(niveles):
    """Pasa al ingles los textos pedagogicos con app/content/traducciones.json.

    El plan original esta en espanol; este diccionario permite que la app se
    muestre entera en ingles sin perder la fuente.
    """
    import json as _json
    ruta = os.path.join(os.path.dirname(WWW), "content", "traducciones.json")
    if not os.path.exists(ruta):
        return 0
    with open(ruta, encoding="utf-8") as f:
        mapa = _json.load(f)

    campos_nivel = ("goal", "levelProject")
    campos_unidad = ("objective", "song", "games", "materials", "evaluation",
                     "project", "phonics", "errores")
    campos_clase = ("focus", "activity", "evidence")
    cambios = [0]

    def tr(valor):
        if not isinstance(valor, str):
            return valor
        clave = valor.strip()
        if clave in mapa:
            cambios[0] += 1
            return mapa[clave]
        return valor

    for lv in niveles:
        if isinstance(lv.get("age"), str):
            lv["age"] = lv["age"].replace("años", "years").strip()
        for k in campos_nivel:
            if k in lv:
                lv[k] = tr(lv[k])
        for u in lv["units"]:
            for k in campos_unidad:
                if k in u:
                    u[k] = tr(u[k])
            for c in u["classes"]:
                for k in campos_clase:
                    if k in c:
                        c[k] = tr(c[k])
    return cambios[0]


def main():
    niveles = enriquecer(parsear_plan())
    con_foto = adjuntar_imagenes(niveles)
    traducidas = traducir_contenido(niveles)
    errores, tu, tc, tp = validar(niveles)

    contenido = {
        "app": "LangKids English",
        "version": "1.0",
        "source": os.path.basename(PLAN_MD),
        "levels": niveles,
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(contenido, f, ensure_ascii=False, indent=1)

    # Copia como JS: en file:// (dentro del APK) no se puede usar fetch()
    salida_js = os.path.join(os.path.dirname(AQUI), "www", "content", "lessons.js")
    os.makedirs(os.path.dirname(salida_js), exist_ok=True)
    with open(salida_js, "w", encoding="utf-8") as f:
        f.write("/* Generado por tools/gen_content.py — no editar a mano */\n")
        f.write("window.LANGKIDS_CONTENT = ")
        json.dump(contenido, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print("JS:      %s (%.1f KB)" % (salida_js, os.path.getsize(salida_js) / 1024))

    print("Niveles: %d | Unidades: %d | Clases: %d | Palabras: %d" % (len(niveles), tu, tc, tp))
    print("Palabras con foto: %d (el resto usa emoji)" % con_foto)
    print("Textos traducidos al ingles: %d" % traducidas)
    print("Salida: %s (%.1f KB)" % (SALIDA, os.path.getsize(SALIDA) / 1024))
    if errores:
        print("PROBLEMAS:")
        for e in errores:
            print("  -", e)
        return 1
    print("Validacion: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
