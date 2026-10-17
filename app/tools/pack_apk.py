# -*- coding: utf-8 -*-
"""
pack_apk.py — Reempaqueta el APK con nombres de asset POSIX.

Windows: aapt2 escribe los assets como `assets/www\\index.html` (barra
invertida) y el AssetManager de Android los ve como un archivo suelto, así que
la WebView no encuentra `assets/www/index.html`. Este script reescribe el APK
con nombres correctos, añade classes.dex y deja resources.arsc sin comprimir.

Uso:
    python pack_apk.py <base.apk> <dir_assets> <classes.dex> <salida.apk>
"""

import os
import sys
import zipfile

FECHA = (2026, 1, 1, 0, 0, 0)


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        return 2

    base, dir_assets, dex, salida = sys.argv[1:5]

    with zipfile.ZipFile(base) as origen:
        entradas = {i.filename: i for i in origen.infolist()}

        with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as destino:
            # 1) recursos enlazados por aapt2, sin los assets (vienen mal nombrados)
            for nombre, info in entradas.items():
                if nombre.startswith("assets/"):
                    continue
                compresion = (zipfile.ZIP_STORED
                              if nombre == "resources.arsc"
                              else zipfile.ZIP_DEFLATED)
                zi = zipfile.ZipInfo(nombre, FECHA)
                zi.compress_type = compresion
                zi.external_attr = 0o644 << 16
                destino.writestr(zi, origen.read(nombre))

            # 2) classes.dex
            zi = zipfile.ZipInfo("classes.dex", FECHA)
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(dex, "rb") as f:
                destino.writestr(zi, f.read())

            # 3) assets con separador POSIX
            n = 0
            for raiz, _, archivos in os.walk(dir_assets):
                for a in archivos:
                    completo = os.path.join(raiz, a)
                    rel = os.path.relpath(completo, dir_assets).replace("\\", "/")
                    zi = zipfile.ZipInfo("assets/" + rel, FECHA)
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zi.external_attr = 0o644 << 16
                    with open(completo, "rb") as f:
                        destino.writestr(zi, f.read())
                    n += 1

    # comprobación: ninguna entrada con barra invertida
    with zipfile.ZipFile(salida) as z:
        malas = [i.filename for i in z.infolist() if "\\" in i.filename]
        assets = [i.filename for i in z.infolist() if i.filename.startswith("assets/")]
    print("   APK empaquetado: %d assets, %d entradas" % (n, len(assets)))
    if malas:
        print("   ERROR: entradas con barra invertida:", malas)
        return 1
    if "assets/www/index.html" not in assets:
        print("   ERROR: falta assets/www/index.html")
        return 1
    print("   rutas POSIX verificadas OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
