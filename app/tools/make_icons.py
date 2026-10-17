# -*- coding: utf-8 -*-
"""
make_icons.py — Dibuja el icono de LangKids (bocadillo + ABC) en todas las
densidades de Android, el icono adaptativo, el de Play Store y el de la web.
"""

import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
ANDROID = os.path.join(os.path.dirname(AQUI), "android")
WWW = os.path.join(os.path.dirname(AQUI), "www")

TEAL = (31, 111, 139)
TEAL2 = (46, 147, 181)
ORANGE = (210, 105, 30)
WHITE = (255, 255, 255)
AMARILLO = (245, 179, 1)

FUENTE = r"C:\Windows\Fonts\comicbd.ttf"

DENSIDADES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}


def degradado(size, c1, c2):
    img = Image.new("RGB", (size, size), c1)
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / float(size - 1)
        col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        d.line([(0, y), (size, y)], fill=col)
    return img


def estrella(d, cx, cy, r, color):
    import math
    puntos = []
    for i in range(10):
        ang = math.pi / 5 * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.45
        puntos.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(puntos, fill=color)


def dibujar_bocadillo(img, caja, radio, relleno, borde=None, grosor=0):
    """Bocadillo redondeado con colita, dentro de la caja (x0,y0,x1,y1)."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = caja
    d.rounded_rectangle([x0, y0, x1, y1], radius=radio, fill=relleno,
                        outline=borde, width=grosor)
    # colita
    w = x1 - x0
    cola = [(x0 + w * 0.28, y1 - 2), (x0 + w * 0.46, y1 - 2), (x0 + w * 0.30, y1 + (y1 - y0) * 0.18)]
    d.polygon(cola, fill=relleno)
    return d


def arte(size):
    """Dibuja el motivo (bocadillo + ABC + estrella) sobre fondo transparente."""
    S = size
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    caja = (S * 0.12, S * 0.18, S * 0.88, S * 0.60)
    dibujar_bocadillo(img, caja, int(S * 0.10), WHITE)

    d = ImageDraw.Draw(img)
    alto = int(S * 0.22)
    f = ImageFont.truetype(FUENTE, alto)
    texto = "ABC"
    bb = d.textbbox((0, 0), texto, font=f)
    d.text(((caja[0] + caja[2]) / 2 - (bb[2] - bb[0]) / 2 - bb[0],
            (caja[1] + caja[3]) / 2 - (bb[3] - bb[1]) / 2 - bb[1]), texto, font=f, fill=TEAL)

    estrella(d, S * 0.76, S * 0.70, S * 0.10, AMARILLO)
    d.ellipse([S * 0.17, S * 0.72, S * 0.24, S * 0.79], fill=ORANGE)
    d.ellipse([S * 0.30, S * 0.79, S * 0.36, S * 0.85], fill=TEAL2)
    return img


def icono(size, con_fondo=True, escala_arte=1.0):
    """
    con_fondo=True  -> icono clasico: fondo degradado + motivo.
    con_fondo=False -> primer plano de icono adaptativo (motivo al 66 %).
    """
    S = size * 4                      # se dibuja grande y se reduce: bordes suaves
    motivo = arte(S)

    if escala_arte != 1.0:
        nuevo = int(S * escala_arte)
        reducido = motivo.resize((nuevo, nuevo), Image.LANCZOS)
        lienzo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        off = (S - nuevo) // 2
        lienzo.paste(reducido, (off, off), reducido)
        motivo = lienzo

    if not con_fondo:
        return motivo.resize((size, size), Image.LANCZOS)

    base = degradado(S, TEAL, TEAL2).convert("RGBA")
    mascara = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, S - 1, S - 1],
                                              radius=int(S * 0.23), fill=255)
    fondo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fondo.paste(base, (0, 0), mascara)
    fondo.alpha_composite(motivo)
    return fondo.resize((size, size), Image.LANCZOS)


def guardar(img, ruta):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    img.save(ruta)
    return ruta


def main():
    salidas = []
    for dens, tam in DENSIDADES.items():
        salidas.append(guardar(icono(tam, True), os.path.join(ANDROID, "res", "mipmap-" + dens, "ic_launcher.png")))
        salidas.append(guardar(icono(tam, True), os.path.join(ANDROID, "res", "mipmap-" + dens, "ic_launcher_round.png")))
        # primer plano adaptativo: 108dp, el motivo ocupa el 66% central
        fg = int(tam * 108 / 48)
        salidas.append(guardar(icono(fg, False, escala_arte=0.66),
                               os.path.join(ANDROID, "res", "mipmap-" + dens, "ic_launcher_foreground.png")))

    # icono de tienda y de la web
    salidas.append(guardar(icono(512, True), os.path.join(os.path.dirname(AQUI), "dist", "icono-512.png")))
    salidas.append(guardar(icono(192, True), os.path.join(WWW, "assets", "icon.png")))

    for s in salidas:
        print("icono:", os.path.relpath(s, os.path.dirname(AQUI)))


if __name__ == "__main__":
    main()
