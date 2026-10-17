# Imágenes: pendientes y dudosas

Informe generado automáticamente por `tools/report_images.py` a partir del contenido real de la app. Se vuelve a generar después de cada tanda de descargas.

| Estado | Palabras |
| --- | --- |
| Con foto | **356** |
| Pendientes (usan emoji) | 2 |
| Con emoji a propósito (no son fotografiables) | 54 |
| **Total** | **412** |

## 1. Fotos que conviene revisar o sustituir

Estas palabras **ya tienen foto**, pero la imagen no es del todo clara para un niño.

| Palabra | Unidad | Problema |
| --- | --- | --- |
| `white` | 1.2 | el color blanco se representa con una nube |
| `crayon` | 1.2 | es una caja de ceras, no una cera suelta |
| `head` | 1.3 | es una cara de niño; para «head» se espera la cabeza |
| `feet` | 1.3 | salen unos pies con zapatillas puestas |
| `crayon` | 2.2 | es una caja de ceras, no una cera suelta |
| `climb` | 2.4 | la etiqueta «Climb» de la hoja va dentro del dibujo; no se puede recortar sin cortar al niño |
| `spring` | 3.4 | se representa con una flor suelta |
| `autumn` | 3.4 | se representa con una hoja suelta |
| `winter` | 3.4 | se representa con un muñeco de nieve |
| `tennis` | 3.4 | es una raqueta con pelota, no el deporte en acción |

Para resolverlas, una por una:

```powershell
# 1) ver 4 candidatas y elegir a ojo
python app\tools\fetch_images.py --candidatos "milk,skirt,trousers,jacket"
# 2) copiar la elegida
Copy-Item docs\candidatos\milk-2.webp app\www\assets\img\milk.webp -Force
```

## 2. Fotos descartadas (y por qué)

| Palabra | Qué mostraba | Motivo del descarte |
| --- | --- | --- |
| `todas las de Pixabay` | fotos reales | el estilo fotográfico no encajaba con las ilustraciones; se sustituyeron por las hojas de IA |

> La foto de `jacket` (un hombre fumando) se eliminó en cuanto se detectó: una app para niños no puede mostrar tabaco. **Cada tanda necesita revisión visual antes de publicar.**

## 3. Palabras pendientes (por unidad)

Sin foto todavía: la app las muestra con su emoji, así que **no hay ningún hueco roto**.

**2.1 · All About Me** (1): `age`

**3.4 · Weather, Seasons & Free Time** (1): `favorite`

## 4. Palabras con emoji a propósito

Saludos, emociones, gramática y adjetivos abstractos: el buscador devuelve imágenes absurdas para ellas (un pájaro para *hello*, una lente para *hi*), así que se quedan con emoji de forma permanente.

`hi`, `goodbye`, `bye-bye`, `name`, `count`, `cute`, `old`, `where`, `can`, `can't`, `near`, `young`, `old`, `last night`, `last week`, `last weekend`, `ago`, `was`, `were`, `went`, `came`, `first`, `then`, `finally`, `tonight`, `next week`, `next month`, `next year`, `soon`, `going to`, `will`, `won't`, `maybe`, `perhaps`, `sure`, `bigger`, `taller`, `faster`, `more interesting`, `more dangerous`, `good-better-best`, `the biggest`, `the fastest`, `the most dangerous`, `beginning`, `middle`, `end`, `first`, `then`, `next`, `finally`, `suddenly`, `narrator`, `presentation`

## 5. Cómo continuar

```powershell
$env:PIXABAY_KEY = "<clave>"
python app\tools\fetch_images.py --unit 3.2      # siguiente tanda sugerida: ciudad y transporte
python app\tools\report_images.py                # regenerar este informe
pwsh -File app\tools\build-apk.ps1               # reconstruir el APK
```

*Ritmo: ~25 s por imagen → una tanda de 25 palabras son ~10 minutos. Lotes de 20-30 para respetar los términos de la API.*
