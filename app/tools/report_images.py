# -*- coding: utf-8 -*-
"""
report_images.py — Genera docs/Imagenes-pendientes.md

Documenta, a partir del contenido real de la app:
  · qué palabras ya tienen foto (con su autor),
  · qué palabras siguen pendientes (y por tanto usan emoji),
  · qué fotos hay que revisar o sustituir, y por qué.

Uso:  python app/tools/report_images.py
"""

import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
LESSONS = os.path.join(APP, "content", "lessons.json")
CREDITS = os.path.join(APP, "content", "credits.json")
SALIDA = os.path.join(RAIZ, "docs", "Imagenes-pendientes.md")

# Palabras con foto que, aun siendo correctas, no son ideales para niños.
REVISAR = {
    "head": "es una cara de niño; para «head» se espera la cabeza",
    "feet": "salen unos pies con zapatillas puestas",
    "white": "el color blanco se representa con una nube",
    "tennis": "es una raqueta con pelota, no el deporte en acción",
    "spring": "se representa con una flor suelta",
    "autumn": "se representa con una hoja suelta",
    "winter": "se representa con un muñeco de nieve",
    "crayon": "es una caja de ceras, no una cera suelta",
    "keys": "plural y singular pueden confundirse",
    "climb": "la etiqueta «Climb» de la hoja va dentro del dibujo; no se puede recortar sin cortar al niño",
}

# Las fotos de Pixabay se descartaron al adoptar las ilustraciones propias.
RECHAZADAS = [
    ("todas las de Pixabay", "fotos reales",
     "el estilo fotográfico no encajaba con las ilustraciones; se sustituyeron por las hojas de IA"),
]

NO_FOTOGRAFIABLES = {
    "was", "were", "went", "came", "going to", "will", "won't", "can", "can't",
    "how many", "count", "please", "thank you", "fine", "maybe", "perhaps",
    "sure", "of course", "the biggest", "the fastest", "the most dangerous",
    "more interesting", "more dangerous", "good-better-best", "bigger",
    "taller", "faster", "heavier", "lighter", "first", "then", "next",
    "finally", "suddenly", "once upon a time", "happy ending", "in", "on",
    "under", "where", "next to", "between", "opposite", "behind", "in front of",
    "near", "turn left", "turn right", "go straight", "o'clock", "half past",
    "today", "tomorrow", "tonight", "yesterday", "last night", "last week",
    "last weekend", "next week", "next month", "next year", "ago", "soon",
    "plan", "idea", "beginning", "middle", "end", "narrator", "presentation",
    "project", "hello", "hi", "goodbye", "bye-bye", "good morning",
    "good afternoon", "happy", "sad", "angry", "sleepy", "hungry", "thirsty",
    "name", "nice", "cute", "like", "don't like", "love", "old", "young",
}


def main():
    with open(LESSONS, encoding="utf-8") as f:
        contenido = json.load(f)
    creditos = {}
    if os.path.exists(CREDITS):
        with open(CREDITS, encoding="utf-8") as f:
            creditos = json.load(f).get("imagenes", {})

    con_foto, pendientes, intencionales = [], [], []
    for nivel in contenido["levels"]:
        for unidad in nivel["units"]:
            for w in unidad["words"]:
                fila = (unidad["id"], unidad["title"], w["en"], w.get("img"))
                if w.get("img"):
                    con_foto.append(fila)
                elif w["en"].strip().lower() in NO_FOTOGRAFIABLES:
                    intencionales.append(fila)
                else:
                    pendientes.append(fila)

    lineas = []
    a = lineas.append
    a("# Imágenes: pendientes y dudosas")
    a("")
    a("Informe generado automáticamente por `tools/report_images.py` a partir del contenido real "
      "de la app. Se vuelve a generar después de cada tanda de descargas.")
    a("")
    a("| Estado | Palabras |")
    a("| --- | --- |")
    a("| Con foto | **%d** |" % len(con_foto))
    a("| Pendientes (usan emoji) | %d |" % len(pendientes))
    a("| Con emoji a propósito (no son fotografiables) | %d |" % len(intencionales))
    a("| **Total** | **%d** |" % (len(con_foto) + len(pendientes) + len(intencionales)))
    a("")

    a("## 1. Fotos que conviene revisar o sustituir")
    a("")
    a("Estas palabras **ya tienen foto**, pero la imagen no es del todo clara para un niño.")
    a("")
    a("| Palabra | Unidad | Problema |")
    a("| --- | --- | --- |")
    for uid, titulo, palabra, _ in con_foto:
        if palabra.strip().lower() in REVISAR:
            a("| `%s` | %s | %s |" % (palabra, uid, REVISAR[palabra.strip().lower()]))
    a("")
    a("Para resolverlas, una por una:")
    a("")
    a("```powershell")
    a("# 1) ver 4 candidatas y elegir a ojo")
    a("python app\\tools\\fetch_images.py --candidatos \"milk,skirt,trousers,jacket\"")
    a("# 2) copiar la elegida")
    a("Copy-Item docs\\candidatos\\milk-2.webp app\\www\\assets\\img\\milk.webp -Force")
    a("```")
    a("")

    a("## 2. Fotos descartadas (y por qué)")
    a("")
    a("| Palabra | Qué mostraba | Motivo del descarte |")
    a("| --- | --- | --- |")
    for palabra, que, motivo in RECHAZADAS:
        a("| `%s` | %s | %s |" % (palabra, que, motivo))
    a("")
    a("> La foto de `jacket` (un hombre fumando) se eliminó en cuanto se detectó: una app para "
      "niños no puede mostrar tabaco. **Cada tanda necesita revisión visual antes de publicar.**")
    a("")

    a("## 3. Palabras pendientes (por unidad)")
    a("")
    a("Sin foto todavía: la app las muestra con su emoji, así que **no hay ningún hueco roto**.")
    a("")
    por_unidad = {}
    for uid, titulo, palabra, _ in pendientes:
        por_unidad.setdefault((uid, titulo), []).append(palabra)
    for (uid, titulo), palabras in sorted(por_unidad.items()):
        a("**%s · %s** (%d): %s" % (uid, titulo, len(palabras),
                                    ", ".join("`%s`" % p for p in palabras)))
        a("")

    a("## 4. Palabras con emoji a propósito")
    a("")
    a("Saludos, emociones, gramática y adjetivos abstractos: el buscador devuelve imágenes "
      "absurdas para ellas (un pájaro para *hello*, una lente para *hi*), así que se quedan "
      "con emoji de forma permanente.")
    a("")
    a(", ".join("`%s`" % p for _, _, p, _ in intencionales))
    a("")

    a("## 5. Cómo continuar")
    a("")
    a("```powershell")
    a("$env:PIXABAY_KEY = \"<clave>\"")
    a("python app\\tools\\fetch_images.py --unit 3.2      # siguiente tanda sugerida: ciudad y transporte")
    a("python app\\tools\\report_images.py                # regenerar este informe")
    a("pwsh -File app\\tools\\build-apk.ps1               # reconstruir el APK")
    a("```")
    a("")
    a("*Ritmo: ~25 s por imagen → una tanda de 25 palabras son ~10 minutos. "
      "Lotes de 20-30 para respetar los términos de la API.*")
    a("")

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

    print("Informe: %s" % SALIDA)
    print("  con foto: %d | pendientes: %d | emoji a proposito: %d | a revisar: %d"
          % (len(con_foto), len(pendientes), len(intencionales),
             sum(1 for p in con_foto if p[2].strip().lower() in REVISAR)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
