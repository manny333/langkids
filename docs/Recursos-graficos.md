# Recursos gráficos: cómo usar imágenes gratuitas en LangKids

Investigación de las cinco fuentes que propusiste, con lo que **realmente** exige cada una y cómo
integrarlas en la app sin problemas legales.

---

## 1. Comparativa rápida

| Fuente | Qué aporta | Licencia | ¿Clave de API? | ¿Atribución obligatoria? | Encaja en LangKids |
| --- | --- | --- | --- | --- | --- |
| **Pixabay** | Fotos e ilustraciones | Pixabay Content License (uso comercial sí, redistribución como imagen sola no) | Sí (gratuita) | No | ✅ Fotos de objetos |
| **Pexels** | Fotos profesionales | Pexels License (uso comercial sí) | Sí (gratuita, 200 peticiones/hora y 20.000/mes) | No, pero se agradece | ✅ Fotos de objetos |
| **Unsplash** | Fotos de muy alta calidad | Unsplash License | Sí (*app key*) | **Sí, por contrato de API** | ⚠️ Solo con pantalla de créditos |
| **Openverse** | Agregador (Flickr, Wikimedia, museos…) | Variable: CC0, CC BY, CC BY-SA… | No | Depende de cada licencia | ⚠️ Filtrar a CC0 |
| **Wikimedia Commons** | Fotos, mapas e ilustraciones | CC0, dominio público, CC BY, CC BY-SA | No | CC BY y CC BY-SA, sí | ✅ Si se filtra a CC0/PD |
| **SVG Repo** | Iconos vectoriales | Mixta: CC0, MIT, CC BY | No | Según el icono | ✅ Iconos de interfaz |

> **Dato importante:** en este equipo solo **Wikimedia Commons** y **SVG Repo** respondieron sin clave.
> Pexels y Unsplash responden pero devuelven `HTTP 401` (falta la clave). Pixabay y Openverse no
> respondieron por timeout desde esta red. Ver la tabla de pruebas al final.

---

## 2. Reglas de oro (las que evitan problemas)

1. **Registrar siempre la fuente**, aunque no sea obligatorio: autor, URL, licencia y fecha de descarga.
   Un archivo `credits.json` junto a las imágenes basta y demuestra buena fe.
2. **Ojo con CC BY-SA**: es « contagiosa ». Si mezclas una imagen CC BY-SA con tu app, en teoría obliga a
   licenciar la obra derivada igual. Para una app comercial conviene **CC0 o dominio público**.
3. **Unsplash por API exige atribución con enlace**, con parámetros `?utm_source=...&utm_medium=referral`
   y enlace al perfil del fotógrafo. Si no quieres pantalla de créditos, usa Pexels o Pixabay.
4. **Los hotlinks caducan**: Unsplash pide usar sus URLs, pero para una app **offline** hay que descargar
   las imágenes. En ese caso, la atribución en pantalla sigue siendo obligatoria.
5. **Nada de marcas ni personajes**: el ejemplo de Lingokids con Disney funciona porque tienen licencia
   pagada. Un APK gratuito usando personajes de Disney sería infracción.
6. **Nada de caras reales de niños** sin consentimiento escrito de las familias (RGPD/COPPA).
7. **Tamaño**: para la app, 512×512 px en WebP (< 40 KB) es suficiente; 400 imágenes ≈ 16 MB.

---

## 3. Cómo obtener las claves (cuando las necesites)

| Servicio | Dónde | Notas |
| --- | --- | --- |
| Pexels | <https://www.pexels.com/api/> | Registro inmediato, clave en el panel. Límite 200/h y 20.000/mes |
| Unsplash | <https://unsplash.com/developers> → *New application* | Modo demo: 50 peticiones/hora |
| Pixabay | <https://pixabay.com/api/docs/> | La clave aparece en tu perfil tras iniciar sesión |

Se guardan como variables de entorno y **nunca** dentro del APK:

```powershell
$env:PEXELS_KEY   = "..."
$env:UNSPLASH_KEY = "..."
$env:PIXABAY_KEY  = "..."
```

---

## 4. Cómo lo integraría en la app (diseño propuesto)

**a) El contenido ya admite imágenes.** Cada palabra del `lessons.json` tiene `emoji`; se le añadiría un
campo opcional `img`:

```json
{ "en": "apple", "emoji": "🍎", "img": "assets/img/apple.webp" }
```

La interfaz usa `img` si existe y cae al emoji si no. Así se pueden ir sustituyendo palabras **sin
romper nada** y sin descargar 412 imágenes de golpe.

**b) Script de descarga con registro de licencias** (`tools/fetch_images.py`, pendiente de escribir):

```
1. Lee la lista de palabras del currículo.
2. Busca en la fuente elegida (Wikimedia por defecto: sin clave).
3. Filtra por licencia permitida (CC0 / dominio público).
4. Descarga, recorta a cuadrado y convierte a WebP 512 px.
5. Guarda en www/assets/img/ y añade la entrada a credits.json.
```

**c) Pantalla de créditos** en Ajustes, generada desde `credits.json`, con autor, licencia y enlace.

---

## 5. Mi recomendación para el estilo que quieres

Para el look Lingokids/Duolingo ABC, las **fotos reales no son lo que más ayuda**: lo que da carácter son
las **ilustraciones planas** de personajes y objetos, con contornos gruesos y colores planos.

| Necesidad | Mejor opción | Por qué |
| --- | --- | --- |
| Vocabulario visual (manzana, perro, coche) | **Openverse filtrado a CC0** o **Wikimedia CC0/PD** | Ilustraciones y fotos con licencia limpia |
| Fotos «reales» para niveles 3-4 | **Pexels** (clave gratuita) | Calidad y licencia simple |
| Iconos de la interfaz (estrellas, candados, trofeos) | **SVG Repo** (CC0/MIT) | Vectorial, pesa poco y escala perfecto |
| Personajes y mascota | **Encargo propio** o generador con licencia comercial | Es la identidad de la marca: no debe ser genérico |

**Lo que ya está hecho y no depende de terceros:** la app usa **emojis** como arte base. Son gratuitos, a
color, consistentes en las 412 palabras y pesan 0 KB. Es la decisión más robusta para la v1; las imágenes
reales se pueden añadir después, palabra por palabra, sin refactorizar nada.

---

## 6. Estado de las pruebas de red (este equipo)

| Servicio | Resultado |
| --- | --- |
| `api.pexels.com` | HTTP 401 (alcanzable, falta clave) |
| `api.unsplash.com` | HTTP 401 (alcanzable, falta clave) |
| `pixabay.com/api` | timeout |
| `api.openverse.org` | timeout |
| `commons.wikimedia.org/api` | **HTTP 200** (usable sin clave) |
| `www.svgrepo.com` | HTTP 429 (límite temporal, alcanzable) |
| `fonts.googleapis.com` | HTTP 200 (tipografías OFL descargadas) |

---

## 7. Integración real con Pixabay (implementada)

La conexión está hecha y probada. Resumen de lo que hay y de lo que aprendimos.

### 7.1 El cliente

`app/tools/fetch_images.py` consulta la API y deja las imágenes listas para la app:

```powershell
$env:PIXABAY_KEY = "<tu clave>"        # nunca se escribe en archivos del proyecto
python app\tools\fetch_images.py --unit 2.3        # una unidad
python app\tools\fetch_images.py --unit 1.4 --tipo illustration
```

Qué hace: busca la palabra (con consultas afinadas), elige el resultado cuyas etiquetas
contienen el término, descarga el `webformatURL` de 640 px, recorta a cuadrado, redimensiona
a **512×512 WebP** (≈30 KB), y registra autor, ID y licencia en `credits.json`.

### 7.2 Reglas de la API que se respetan

| Regla | Cómo se cumple |
| --- | --- |
| 100 peticiones / 60 s | Pausa de 0,45 s entre palabras y lectura del header `X-RateLimit-Remaining` |
| Caché de 24 h | Las imágenes se descargan una vez y no se vuelven a pedir (`--force` solo manual) |
| «No systematic mass downloads» | Lotes de 20-30 palabras, nunca las 412 de golpe |
| Mostrar la procedencia | Pantalla de Ajustes: «Fotos: Pixabay · licencia · fotógrafos» |
| Descargar, no hotlinkear | Todas las imágenes se empaquetan dentro del APK |

### 7.3 Resultado del experimento (lo importante)

**Lección aprendida:** la búsqueda automática funciona con **sustantivos concretos** y fracasa con
conceptos abstractos.

| Prueba | Resultado |
| --- | --- |
| Unidad 1.1 «Hello, Friends!» (saludos y emociones) | ❌ 17 fotos inservibles: un pájaro para *hello*, una lente para *hi*, un payaso para *sad* |
| Unidad 1.4 «Animals & Toys» (animales) | ✅ 10/10 correctas y adecuadas para niños |

Por eso el script ahora usa una **lista blanca** de ~150 sustantivos concretos (`FOTOGRAFIABLES`)
y **consultas afinadas** por palabra (`orange` → «orange fruit», `chair` → «wooden chair»). Todo lo
demás (saludos, emociones, gramática, adjetivos) conserva su **emoji**.

### 7.4 Cómo llega la imagen a la pantalla

1. `gen_content.py` detecta `app/www/assets/img/<palabra>.webp` y añade `"img": "assets/img/…"` a la palabra.
2. La interfaz (`activities.js`) usa una función `figura()`: **foto si existe, emoji si no**.
3. Si mañana se borra una foto, la app vuelve al emoji sin romperse.

### 7.5 Estado

| Métrica | Valor |
| --- | --- |
| Imágenes con foto | 10 (animales de la unidad 1.4) |
| Peso de las imágenes | 303 KB |
| Peso del APK | 572 KB |
| Créditos registrados | 10 autores, con licencia y página de origen |

### 7.6 Siguiente tanda

Comida y ropa (unidad 2.3), luego casa/aula (2.2) y transporte/ciudad (3.2). A ~25 s por imagen,
cada tanda de 25-30 palabras son unos 10-12 minutos.

---

## 8. Fuentes consultadas

- [Unsplash API Guidelines · atribución](https://help.unsplash.com/en/articles/2511315-guideline-attribution)
- [Unsplash API Guidelines](https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines)
- [Pexels Help · límites de peticiones](https://help.pexels.com/hc/en-us/articles/900005852323-How-do-I-get-unlimited-requests)
- [Licencia Pixabay](https://pixabay.com/service/license-summary/)
- [Openverse API](https://api.openverse.org/v1/)
- [Wikimedia Commons · reutilización](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia)
- [SVG Repo · licencias](https://www.svgrepo.com/page/licensing/)
- [SIL Open Font License (fuentes usadas)](https://openfontlicense.org/open-font-license-official-text/)

*Documento vivo: se actualiza al integrar el primer lote de imágenes.*
