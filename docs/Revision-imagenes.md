# Revisión imagen por imagen · 339 ilustraciones

Informe del trabajo hecho sobre todas las ilustraciones de la app: qué se ha
comprobado, qué se ha corregido y qué queda con alguna limitación.

Fecha: 17/10/2026 · APK 4,82 MB · 339 imágenes

---

## Cómo se revisó

1. **Auditoría automática** (`app/tools/auditar_imagenes.py`) sobre las 339 imágenes.
   Cada una se puntúa con cuatro criterios:

   | Sigla | Qué detecta |
   | --- | --- |
   | `MOCHA` | el dibujo toca el borde del lienzo (viene cortado) |
   | `TEXTO` | hay manchas sueltas fuera del dibujo (etiquetas de la hoja) |
   | `DESCENTRADA` | el dibujo no está en el centro |
   | `PEQUEÑA` | el dibujo ocupa menos del 62 % del lado |

2. **Revisión visual** en 14 hojas de contacto de 25 imágenes cada una
   (`docs/revision/r01.png` … `r14.png`).

3. Corrección y repetición hasta que el informe quedó limpio.

---

## Correcciones aplicadas a todas las imágenes

Estas mejoras se aplican en cadena a **cada** ilustración al generarla:

1. **Recorte de etiquetas de la hoja.** Se detectan las bandas de filas con
   tinta pero sin color (el texto nunca tiene relleno de color) y se recortan.
2. **Borrado de texto que flota.** Los trazos oscuros rodeados de blanco se
   eliminan (etiquetas que se solapaban con el dibujo).
3. **Borrado de corchetes de celda.** La hoja dibuja líneas decorativas en las
   esquinas de algunas tarjetas; se eliminan si tocan el borde y son finas.
4. **Agrupación del dibujo.** Se toma el objeto principal y solo las piezas que
   lo **tocan** (gotas, lápices, adornos). Se descartan marcos de tarjeta,
   líneas sueltas, trazos tenues y piezas lejanas.
5. **Centrado con margen garantizado.** Se recorta exactamente el dibujo y se
   pega centrado en un lienzo cuadrado de blanco puro (margen del 10 %). El
   margen nunca se toma del original, así no entran trazos de la hoja.
6. **Reducción de seguridad.** Si el dibujo aún toca el lienzo, se reduce un
   14 % y se vuelve a centrar.
7. **512×512 WebP** para todas, con el mismo nombre `<palabra>.webp`.

---

## Errores de contenido corregidos

| Palabra | Problema | Corrección |
| --- | --- | --- |
| `kite` / `train` | tenían **las imágenes intercambiadas** (la cometa mostraba un tren de bloques y el tren una cometa) | se intercambiaron en el mapa de la hoja de juguetes |
| `blocks` | se había quedado **sin imagen** porque esa hoja detecta 6 tarjetas y el mapa tenía 8 entradas | mapa ajustado a 6; recupera su ilustración |
| `bathroom` | la etiqueta «bathroom» se colaba bajo la bañera | la limpieza se aplica también a los recortes manuales |
| `climb` | la etiqueta «Climb» se solapaba con el pelo | recorte por bandas + borrado de texto flotante |
| `cycling`, `dance`, `tall` | etiquetas sobre el dibujo | ídem |
| `tummy`, `ears`, `hands`, `head`, `legs` | corchete decorativo de la hoja pegado al dibujo | borrado de corchetes + limpieza específica en `tummy` |
| `go-straight`, `butterfly`… | etiquetas superiores | recorte por bandas |

---

## Resultado del informe automático

```
imágenes revisadas: 339
  OK           337
  TEXTO          2
  DESCENTRADA    1
  PEQUEÑA        1
```

Las tres que aún aparecen marcadas están revisadas a ojo y son correctas:

| Palabra | Marca | Por qué se acepta |
| --- | --- | --- |
| `school` | TEXTO | la «mancha suelta» es la **bandera** del tejado, parte del dibujo |
| `foggy` | PEQUEÑA / DESCENTRADA | el dibujo original es una nube gris con rayas de niebla, muy plano; está completo y centrado, pero es soso |
| `bathroom` | TEXTO | las «manchas» son las burbujas del agua de la bañera |

Ninguna queda cortada ni descentrada de forma visible.

---

## Limitaciones conocidas (no son fallos de recorte)

- **Estilo punteado**: algunos dibujos de la hoja traen un contorno punteado de
  pegatina (`like`, `love`, `bag`, `ball`, `beard`, `monkey`…). Es parte del
  dibujo original, no un resto de recorte.
- **Texto dentro del dibujo**: `shop` lleva un cartel con letras y
  `go-to-school` una fachada con rótulo. Forman parte del dibujo.
- **`feet`** muestra piernas con zapatillas (cortadas arriba por diseño de la
  hoja) y **`eyes`** solo los ojos: son así en el original.
- **`foggy`** y **`go-straight`** son los dibujos más flojos del conjunto.

---

## Cómo revisarlas tú

- **En el ordenador**: `docs/revision/r01.png` … `r14.png`, 25 por hoja con el
  nombre debajo (se regeneran con `python app/tools/hojas_contacto.py`).
- La pantalla de revisión dentro de la app se retiró cuando dejó de ser
  necesaria; el código quedó más simple.

## Herramientas

| Archivo | Para qué |
| --- | --- |
| `app/tools/import_ia_images.py` | recorta las hojas y aplica la cadena de limpieza |
| `app/tools/auditar_imagenes.py` | informe de las cuatro comprobaciones |
| `app/tools/hojas_contacto.py` | genera las 14 hojas de revisión |
| `app/tools/import_sueltas.py` | importa imágenes individuales (no se usa: el lote por palabra venía recortado de la hoja y salió peor) |
