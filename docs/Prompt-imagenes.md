# Prompts para generar imágenes de prueba

Objetivo: conseguir imágenes con **el mismo estilo** que la app (ilustración plana infantil, tipo
Lingokids / Duolingo ABC), cuadradas y con un solo objeto, para probar cómo se ven antes de hacer
las 88 de la lista completa.

---

## 1. Prompt maestro (el que usarás siempre)

Copia esto y sustituye `[OBJECT]` por el objeto en inglés. Está en inglés porque los generadores
de imagen rinden mejor así.

```text
Flat vector illustration for a children's English learning app: a single [OBJECT],
centered, chunky rounded shapes, thick dark outline (#2B2D42) of even weight,
bright saturated flat colors, one soft drop shadow under the object, subtle
highlight, plain pure white background, generous empty margin around the object,
cute friendly preschool style, crisp vector edges, no text, no letters, no numbers,
no people, no hands, no watermark, square 1:1.
```

**Prompt negativo** (pégalo en el campo «negative prompt» si el generador lo tiene):

```text
photo, photorealistic, 3D render, gradient background, textures, noise, grain,
text, typography, letters, numbers, logo, watermark, frame, border, multiple objects,
clutter, busy background, cartoon eyes on objects, creepy, scary, dark, heavy shadows,
cropped object, human faces, hands
```

**Paleta oficial** (menciónala si el generador permite fijar colores):

```text
#FFC93C amarillo · #FF6B6B coral · #22C7C7 turquesa · #8B5CF6 violeta
#58CC02 verde    · #FF8FB1 rosa  · #2B2D42 tinta (contornos)
```

---

## 2. Lote de prueba: 8 objetos

Elegidos para cubrir los casos fáciles **y** los difíciles. Genera uno por prompt, en la misma
sesión, sin cambiar el estilo.

| # | `[OBJECT]` | Por qué está en la prueba | Archivo |
| --- | --- | --- | --- |
| 1 | `red apple` | caso fácil, objeto único | `apple.png` |
| 2 | `cute cartoon dog` | animal, prueba el estilo «cute» | `dog.png` |
| 3 | `wooden chair` | mueble: el más difícil de reconocer | `chair.png` |
| 4 | `school bus` | vehículo, formas grandes | `bus.png` |
| 5 | `straw sun hat` | prenda: prueba si se reconoce sin persona | `hat.png` |
| 6 | `birthday cake with candles` | comida con detalle | `cake.png` |
| 7 | `school backpack` | objeto escolar | `bag.png` |
| 8 | `red ball` | forma simple, valida el trazo grueso | `ball.png` |

**Cómo pedirlos:**

```text
/imagine Flat vector illustration for a children's English learning app: a single
wooden chair, centered, chunky rounded shapes, thick dark outline (#2B2D42) of even
weight, bright saturated flat colors, one soft drop shadow under the object, subtle
highlight, plain pure white background, generous empty margin around the object,
cute friendly preschool style, crisp vector edges, no text, no letters, no numbers,
no people, no hands, no watermark, square 1:1.
```

---

## 3. Variante: una sola imagen con 9 objetos (para ahorrar)

Solo útil si tu generador es bueno respetando cuadrículas. Después hay que recortar.

```text
A 3x3 grid of nine separate flat vector illustrations for a children's English app,
each cell containing exactly one object centered on a plain white background:
apple, dog, chair, bus, hat, cake, backpack, ball, book. Chunky rounded shapes,
thick dark outline (#2B2D42), bright saturated flat colors, cute preschool style,
crisp vector edges, no text, no letters, no numbers, no people, thin white gaps
between cells, square 1:1.
```

> Si el resultado sale con los objetos mezclados o con texto, vuelve a la opción de una imagen
> por objeto: es más lenta pero mucho más fiable.

---

## 4. Claves para que salgan consistentes

1. **Misma sesión y mismo estilo base**: no cambies el prompt maestro, solo `[OBJECT]`.
2. **Fija la semilla** (seed) si la herramienta lo permite: misma semilla = mismo «universo».
3. **Pide 2-3 variantes por objeto** y elige la más clara; no te quedes con la primera.
4. **Revisa sin texto**: si el modelo escribe la palabra, descártala (la app ya pone el texto).
5. **Nada de personas ni manos**: las manos generadas por IA quedan mal y en esta app no hacen falta.
6. **Fondo blanco liso**, no transparente, si el generador no acierta con la transparencia: el
   recorte cuadrado y el redondeo de la app lo resuelven.

---

## 5. Qué hacer con las imágenes

1. Descárgalas y **renómbralas** exactamente como la columna «Archivo» (`chair.png`, `bag.png`…).
2. Déjalas en `app\www\assets\img\`.
3. Reconstruye:

```powershell
python app\tools\gen_content.py
pwsh -File app\tools\build-apk.ps1
```

La app usa la imagen si existe y su emoji si no: puedes probar con 8 y ver el resultado en la app
sin tocar código.

---

## 6. Checklist de aceptación (2 minutos por imagen)

- [ ] ¿Se reconoce el objeto **sin leer** ninguna palabra?
- [ ] ¿Hay un solo objeto y está completo (no cortado)?
- [ ] ¿Fondo limpio, sin sombras raras ni degradados?
- [ ] ¿Sin texto, sin letras, sin números?
- [ ] ¿Sin personas, manos ni caras?
- [ ] ¿El estilo coincide con las demás (trazo y colores)?

Si falla 2 o más, vuelve a generarla: es más rápido que retocarla.

---

## 7. Versión en español (para modelos que responden mejor en español)

```text
Ilustración vectorial plana para una app infantil de inglés: un solo [OBJETO],
centrado, formas redondeadas y gruesas, contorno oscuro grueso (#2B2D42) de grosor
uniforme, colores planos vivos y saturados, una sombra suave debajo del objeto,
brillo sutil, fondo blanco liso, margen amplio alrededor, estilo preescolar tierno,
bordes vectoriales nítidos, sin texto, sin letras, sin números, sin personas,
sin manos, sin marca de agua, cuadrado 1:1.
```
