# -*- coding: utf-8 -*-
"""
recoger_v2.py — Recoge las imágenes generadas y las asigna a su palabra.

El plugin deja cada imagen como dsh-image-gen/image-<hash>.png. Este programa
toma las N más recientes (en orden de creación, que es el orden en que se
pidieron los prompts) y las renombra a img-ia-v2/<palabra>.png.

Estado en img-ia-v2/_estado.json: palabras hechas y pendientes.

Uso:
    python app/tools/recoger_v2.py --estado          # cuántas van
    python app/tools/recoger_v2.py --tomar 10        # asigna las 10 últimas
    python app/tools/recoger_v2.py --reset           # reinicia la lista
"""
import json
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)
RAIZ = os.path.dirname(APP)
DESTINO = os.path.join(RAIZ, "img-ia-v2")
BUZON = os.path.join(RAIZ, "dsh-image-gen")
ESTADO = os.path.join(DESTINO, "_estado.json")


def palabras_con_imagen():
    d = json.load(open(os.path.join(APP, "content", "lessons.json"), encoding="utf-8"))
    vistas = []
    for nivel in d["levels"]:
        for unidad in nivel["units"]:
            for w in unidad["words"]:
                if w.get("img") and w["en"] not in vistas:
                    vistas.append(w["en"])
    return vistas


def slug(texto):
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = t.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def cargar():
    if os.path.exists(ESTADO):
        return json.load(open(ESTADO, encoding="utf-8"))
    lista = palabras_con_imagen()
    estado = {"hechas": [], "pendientes": [w for w in lista]}
    json.dump(estado, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return estado


def guardar(estado):
    json.dump(estado, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    estado = cargar()

    if "--reset" in sys.argv:
        lista = palabras_con_imagen()
        estado = {"hechas": [], "pendientes": lista}
        guardar(estado)
        print("reiniciado: %d palabras" % len(lista))
        return

    if "--estado" in sys.argv or ("--tomar" not in sys.argv and "--palabra" not in sys.argv):
        print("hechas    : %d" % len(estado["hechas"]))
        print("pendientes: %d" % len(estado["pendientes"]))
        print("siguientes: %s" % ", ".join(estado["pendientes"][:10]))
        return

    # modo recomendado: --palabra <nombre>  (no depende del orden)
    if "--palabra" in sys.argv:
        palabra = sys.argv[sys.argv.index("--palabra") + 1]
        archivos = [os.path.join(BUZON, f) for f in os.listdir(BUZON)
                    if f.lower().endswith(".png")]
        # --desde <epoch_segundos>: solo acepta imágenes posteriores a esa marca.
        # Sirve cuando otro proceso (u otra persona) usa el mismo buzón a la vez.
        if "--desde" in sys.argv:
            desde = float(sys.argv[sys.argv.index("--desde") + 1])
            archivos = [p for p in archivos if os.path.getmtime(p) >= desde]
        if not archivos:
            print("no hay imágenes en el buzón (revisa --desde)")
            return
        reciente = max(archivos, key=os.path.getmtime)
        shutil.move(reciente, os.path.join(DESTINO, slug(palabra) + ".png"))
        if palabra in estado["pendientes"]:
            estado["pendientes"].remove(palabra)
        if palabra not in estado["hechas"]:
            estado["hechas"].append(palabra)
        guardar(estado)
        print("registrada %s  · quedan %d pendientes" % (palabra, len(estado["pendientes"])))
        return

    n = int(sys.argv[sys.argv.index("--tomar") + 1])
    if not os.path.isdir(BUZON):
        print("no existe el buzón %s" % BUZON)
        return
    archivos = [os.path.join(BUZON, f) for f in os.listdir(BUZON)
                if f.lower().endswith(".png")]
    archivos.sort(key=lambda p: os.path.getmtime(p))
    nuevos = archivos[-n:]
    if len(nuevos) < n:
        print("AVISO: solo hay %d imágenes en el buzón (se pedían %d)" % (len(nuevos), n))

    destino_palabras = estado["pendientes"][:len(nuevos)]
    for ruta, palabra in zip(nuevos, destino_palabras):
        salida = os.path.join(DESTINO, slug(palabra) + ".png")
        shutil.move(ruta, salida)
        estado["hechas"].append(palabra)
    estado["pendientes"] = estado["pendientes"][len(destino_palabras):]
    guardar(estado)

    print("asignadas %d: %s" % (len(destino_palabras), ", ".join(destino_palabras)))
    print("quedan %d pendientes" % len(estado["pendientes"]))


if __name__ == "__main__":
    main()
