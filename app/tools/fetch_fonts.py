# -*- coding: utf-8 -*-
"""
fetch_fonts.py — Descarga las tipografías infantiles (Google Fonts, licencia OFL)
y genera el CSS de @font-face local, para que la app funcione sin internet.

Uso:  python fetch_fonts.py
"""

import os
import re
import sys
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(os.path.dirname(AQUI), "www", "assets", "fonts")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# familia, pesos, nombre de archivo base
FUENTES = [
    ("Baloo+2", [400, 600, 700, 800], "baloo2"),
    ("Nunito", [400, 600, 700, 800], "nunito"),
]

AVISO = """Tipografías incluidas en esta app
==================================

Baloo 2  — Copyright (c) 2019 The Baloo 2 Project Authors
Nunito   — Copyright (c) 2019 The Nunito Project Authors
https://github.com/google/fonts/tree/main/ofl/baloo2
https://github.com/google/fonts/tree/main/ofl/nunito

Ambas se distribuyen bajo la SIL Open Font License, Version 1.1 (OFL).
Se permite su uso, estudio, modificación y redistribución (incluida su
inclusión dentro de un APK) siempre que no se vendan por separado y que se
conserve esta nota de licencia. Texto completo de la licencia:
https://openfontlicense.org/open-font-license-official-text/

Descargadas desde Google Fonts (fonts.googleapis.com / fonts.gstatic.com).
"""


def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def css_de(familia, pesos):
    url = ("https://fonts.googleapis.com/css2?family=%s:wght@%s&display=swap"
           % (familia, ";".join(str(p) for p in pesos)))
    return bajar(url).decode("utf-8")


def main():
    os.makedirs(DESTINO, exist_ok=True)
    reglas = []
    total = 0
    ya_bajadas = {}          # url -> nombre de archivo (Google repite la misma fuente variable)
    usos = {}                # (familia, archivo) -> [pesos]

    for familia, pesos, base in FUENTES:
        css = css_de(familia, pesos)
        bloques = re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)
        hechos = set()

        for b in bloques:
            peso_m = re.search(r"font-weight:\s*(\d+)", b)
            url_m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", b)
            rango_m = re.search(r"unicode-range:\s*([^;]+);", b)
            if not (peso_m and url_m):
                continue
            # solo el subconjunto latin basico
            if rango_m and "U+0000-00FF" not in rango_m.group(1):
                continue
            peso = int(peso_m.group(1))
            if peso in hechos:
                continue
            hechos.add(peso)

            url = url_m.group(1)
            if url in ya_bajadas:
                nombre = ya_bajadas[url]
                print("  reutiliza  %-20s (peso %d)" % (nombre, peso))
            else:
                nombre = "%s-%d.woff2" % (base, peso)
                datos = bajar(url)
                with open(os.path.join(DESTINO, nombre), "wb") as f:
                    f.write(datos)
                ya_bajadas[url] = nombre
                total += len(datos)
                print("  descargada %-20s %6.1f KB" % (nombre, len(datos) / 1024.0))

            familia_css = familia.replace("+", " ")
            usos.setdefault((familia_css, nombre), []).append(peso)

        faltan = [p for p in pesos if p not in hechos]
        if faltan:
            print("  AVISO: %s sin pesos %s" % (familia, faltan))

    # una regla por archivo, con el rango de pesos (las fuentes son variables)
    for (familia_css, nombre), pesos_usados in usos.items():
        bajo, alto = min(pesos_usados), max(pesos_usados)
        rango = ("%d %d" % (bajo, alto)) if bajo != alto else str(bajo)
        reglas.append(
            "@font-face {\n"
            "  font-family: '%s';\n"
            "  font-style: normal;\n"
            "  font-weight: %s;\n"
            "  font-display: swap;\n"
            "  src: url('%s') format('woff2');\n"
            "}" % (familia_css, rango, nombre))

    css_local = os.path.join(DESTINO, "fuentes.css")
    with open(css_local, "w", encoding="utf-8") as f:
        f.write("/* Generado por tools/fetch_fonts.py — Google Fonts, licencia OFL */\n\n")
        f.write("\n\n".join(reglas))
        f.write("\n")

    with open(os.path.join(DESTINO, "LICENCIAS.txt"), "w", encoding="utf-8") as f:
        f.write(AVISO)

    print("CSS: %s (%d reglas)" % (css_local, len(reglas)))
    print("Total descargado: %.1f KB" % (total / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
