# Plan de Desarrollo · App «LangKids English»

**Aplicación Android interactiva para aprender inglés, basada en el plan de temas LangKids (4 niveles · 16 unidades · 80 clases).**

`Versión 1.0` · `Plataforma: Android 7.0+ (API 24+)` · `Sin conexión` · `Sin recolección de datos`

---

## 0. Estado de la entrega

Este plan ya está ejecutado en sus fases 1 a 4: la app existe, está compilada y fue probada en un Android real.

| Entregable | Ruta | Estado |
| --- | --- | --- |
| App interactiva (web) | `app/www/` | ✅ Funcionando |
| Contenido de las 80 clases | `app/content/lessons.json` | ✅ 4 niveles · 16 unidades · 80 clases · 412 palabras |
| APK firmado | `app/dist/LangKids-English-1.0.apk` | ✅ 190 KB · `minSdk 24` · `targetSdk 35` |
| Envoltorio Android | `app/android/` | ✅ WebView + voz nativa + progreso |
| Generador de contenido | `app/tools/gen_content.py` | ✅ Regenera desde el plan de temas |
| Compilador del APK | `app/tools/build-apk.ps1` | ✅ aapt2 + javac + d8 + zipalign + apksigner |
| Test automático | `app/tools/selftest.html` | ✅ 93 de 93 comprobaciones |

**Evidencia de la verificación**

| Prueba | Resultado |
| --- | --- |
| Test de contenido y progreso en navegador | 93/93 OK |
| `apksigner verify` | firma válida (v1 + v2) |
| `aapt2 dump badging` | paquete, SDK 24-35, icono y actividad correctos |
| Permisos del APK | solo `VIBRATE` (sin `INTERNET`) |
| Instalación en Android 16 (emulador) | instalado y abierto |
| Recorrido de una clase | tarjetas → escucha → acierto que avanza ✔ |
| Voz | conectada a `com.google.android.tts` ✔ |

![Inicio de la app](img/01-inicio.png)

*Pantalla de inicio en el emulador Android 16: niveles, progreso y botón de continuar.*

---

## 1. Resumen ejecutivo

La app convierte el currículo de LangKids —hoy un documento— en una experiencia jugable: el niño elige su
nivel, avanza por unidades y clases, y en cada clase practica el vocabulario con tarjetas con voz, juegos de
escuchar y tocar, parejas de memoria, frases para ordenar y un cuestionario final. Gana estrellas, desbloquea
insignias y ve su progreso; el docente o la familia puede verlo en la pantalla de progreso.

**Decisiones clave de la v1**

| Decisión | Elección | Motivo |
| --- | --- | --- |
| Interfaz | HTML + CSS + JavaScript propios, sin frameworks | Cero dependencias, cero red, arranque instantáneo y editable sin recompilar herramientas |
| Envoltorio Android | `WebView` nativo + puente JavaScript | Un APK real y ligero (~1 MB) con acceso a lo que la web no puede hacer: voz del sistema, vibración, guardado persistente |
| Voz | `TextToSpeech` de Android (motor del dispositivo) | Pronunciación nativa en inglés **sin internet** y sin archivos de audio que inflen el APK |
| Guardado | `SharedPreferences` vía puente + `localStorage` de respaldo | El progreso sobrevive al cierre de la app |
| Contenido | `lessons.json` generado desde el plan de temas | Una sola fuente de verdad: si se edita el currículo, el contenido se regenera |
| Permisos | Ninguno (solo vibración) | Publicable en Play Store para familias sin fricción ni riesgo de privacidad |

---

## 2. Objetivo y público

**Objetivo del producto.** Que un niño de 5 a 11 años practique inglés 5-10 minutos al día de forma autónoma,
con el mismo vocabulario y las mismas estructuras del curso presencial, de modo que la app refuerce la clase y
no compita con ella.

**Usuarios**

| Usuario | Necesidad | Cómo la app la resuelve |
| --- | --- | --- |
| Niño de 5-6 años (pre-lector) | Jugar sin saber leer | Interfaz con iconos grandes, voz que lee todo lo escrito, actividades de tocar y escuchar |
| Niño de 7-9 años | Sentirse avanzando | Estrellas por clase, insignias por nivel, desbloqueo progresivo |
| Niño de 9-11 años | Reto y autonomía | Frases para ordenar, comparaciones, narración; puede saltar a su nivel real |
| Familia | Ver que sirve | Pantalla de progreso con lo aprendido y sugerencia de práctica |
| Docente | Reforzar la clase | Cada lección coincide 1:1 con una clase del plan; se puede asignar «haz la clase 3 de la unidad 2» |

**Fuera de alcance en la v1** (se evalúa para v2): cuentas de usuario y sincronización en la nube, reconocimiento
de pronunciación por micrófono, modo multijugador, panel web del docente, iOS.

---

## 3. Principios de diseño pedagógico

Se derivan directamente de los ocho principios del plan de temas y condicionan la interfaz:

1. **Escuchar antes de producir.** Toda palabra nueva aparece primero con voz; el niño puede tocar para repetir
   cuantas veces quiera. Ninguna actividad exige hablar ni escribir para avanzar.
2. **Bloques de frase, no listas.** Las estructuras de cada unidad («Can I have an apple, please?») se practican
   como frases completas en la actividad de ordenar palabras.
3. **Aprender jugando.** Cada clase se resuelve como un mini-juego de 3 a 5 rondas; nunca hay una pantalla de
   teoría.
4. **Repaso en espiral.** Cada clase repasa 2 palabras de clases anteriores de la misma unidad; el cuestionario
   de la clase 5 mezcla toda la unidad.
5. **Errores sin castigo.** Si falla, la app repite la voz, ilumina la respuesta correcta y deja reintentar.
   Nunca se pierde progreso ni hay vidas.
6. **Sesiones cortas.** Una clase = 3-6 minutos. El botón de salir siempre está visible.
7. **Sin texto imprescindible.** Todo lo esencial está en icono + voz; el texto acompaña, no bloquea.
8. **Refuerzo afectivo.** La mascota (Milo, el títere del curso) felicita cada logro con animación y sonido.

---

## 4. Del currículo a la app: mapa de contenido

El plan de temas define **4 niveles × 4 unidades × 5 clases = 80 clases**. La app replica esa estructura sin
inventar contenido nuevo:

```
Nivel (4)  →  Unidad (16)  →  Clase (80)  →  Actividades (3-5 por clase)

Nivel 1 · First Words        (5-6 años · Pre-A1)
   Unidad 1.1 Hello, Friends!          Clases 1-5
   Unidad 1.2 Rainbow Colors & Numbers Clases 1-5
   Unidad 1.3 My Body & My Family      Clases 1-5
   Unidad 1.4 Animals & Toys           Clases 1-5
Nivel 2 · Little Explorers   (6-7 años · Pre-A1/A1)
Nivel 3 · Young Speakers     (7-9 años · A1)
Nivel 4 · Story Makers       (9-11 años · A1+/A2)
```

**Cada lección de la app toma de su clase del plan:**

| Dato del plan | Uso en la app |
| --- | --- |
| «Foco de la clase» | Título de la lección |
| «Vocabulario clave» | Palabras de las tarjetas y de los juegos de escuchar/parejas |
| «Estructura modelo» | Frase para la actividad de ordenar palabras |
| «Actividad estrella» | Inspira la mecánica principal y se muestra como texto de apoyo al adulto |
| «Evidencia de aprendizaje» | Criterio de la estrella al terminar la lección |
| «Evaluación y proyecto» de la unidad | Cierre de unidad: cuestionario mixto y tarjeta de proyecto |

**Ejemplo real (Unidad 1.1, Clase 2):** vocabulario `name, boy, girl, friend`; estructura `What's your name? —
My name is ___.`; la app genera 4 tarjetas con voz, un «escucha y toca» de 4 opciones, un juego de parejas y la
frase para ordenar.

---

## 5. Catálogo de actividades interactivas

| # | Actividad | Mecánica | Qué entrena | Cuándo se usa |
| --- | --- | --- | --- | --- |
| 1 | **Tarjetas con voz** | Toca la tarjeta y escucha; desliza para avanzar; botón de repetir | Reconocimiento auditivo y vocabulario | Siempre, al abrir la clase |
| 2 | **Escucha y toca** | Suena una palabra y elige entre 3-4 dibujos | Comprensión oral | Clases 1-5 |
| 3 | **Parejas (memory)** | Descubre parejas dibujo-palabra | Memoria y lectura global | Desde la clase 2 si hay 4+ palabras |
| 4 | **Ordena la frase** | Toca las palabras en orden para formar la estructura modelo | Sintaxis y bloques de frase | Si la estructura tiene 3+ palabras |
| 5 | **¿Cuántos son?** | Cuenta objetos y toca el número | Números (Niveles 1-2) | Unidades de números |
| 6 | **Cuestionario de unidad** | 6-8 preguntas mezcladas de toda la unidad | Repaso en espiral y evaluación | Clase 5 de cada unidad |
| 7 | **Insignia de nivel** | Pantalla de celebración con la insignia del plan (`First Words Star`, etc.) | Motivación | Al completar las 20 clases |

Reglas comunes: botón de voz siempre disponible, respuesta correcta celebrada con animación y sonido, respuesta
incorrecta corregida con voz y reintento, y barra de avance visible arriba.

---

## 6. Arquitectura técnica

```
┌──────────────────────── APK Android (com.langkids.english) ────────────────────────┐
│                                                                                    │
│   MainActivity (Java)                                                              │
│   ├── WebView  ──────────────►  file:///android_asset/www/index.html                │
│   │                              ├── css/styles.css      (diseño infantil)          │
│   │                              ├── js/app.js           (pantallas y navegación)   │
│   │                              ├── js/activities.js    (7 motores de juego)       │
│   │                              ├── js/audio.js         (voz + efectos)            │
│   │                              ├── js/store.js         (progreso y estrellas)     │
│   │                              └── content/lessons.json (16 unidades, 80 clases)  │
│   ├── Puente JavaScript «Android»                                                  │
│   │     ├── speak(texto)      → TextToSpeech nativo (en-US, sin internet)          │
│   │     ├── saveProgress(json)/loadProgress() → SharedPreferences                  │
│   │     ├── vibrate(ms)       → Vibrador del dispositivo                           │
│   │     └── isAndroid()       → true (la web usa voz del navegador si es false)     │
│   └── Botón atrás → navegación interna / confirmación de salida                    │
│                                                                                    │
│   Sin permiso de INTERNET · Sin librerías externas · Sin Gradle en el build        │
└────────────────────────────────────────────────────────────────────────────────────┘
```

**¿Por qué WebView y no Kotlin + Jetpack Compose?** Porque el objetivo de la v1 es contenido y jugabilidad, no
UI nativa: con HTML/CSS/JS el contenido se itera en segundos, el APK pesa ~1 MB, funciona sin red y no necesita
Gradle ni descargar dependencias (el equipo no tiene caché de Gradle ni `cmdline-tools`, y Maven Central
respondió de forma intermitente). La app queda además publicable como **PWA** en cualquier navegador, y una
v2 puede migrar a Compose reutilizando intacto el `lessons.json` y la lógica de juego.

**Componentes y responsabilidades**

| Componente | Archivo | Responsabilidad |
| --- | --- | --- |
| Envoltorio Android | `app/android/java/.../MainActivity.java` | WebView, puente, TTS, progreso nativo, botón atrás |
| Interfaz | `app/www/index.html` + `css/styles.css` | Estructura y diseño adaptado a tablets y móviles |
| Navegación | `app/www/js/app.js` | Router de pantallas, render de niveles/unidades/clases |
| Juegos | `app/www/js/activities.js` | Un motor por tipo de actividad |
| Audio | `app/www/js/audio.js` | Voz nativa o del navegador, efectos, control de silencio |
| Progreso | `app/www/js/store.js` | Estrellas, insignias, desbloqueo, reinicio |
| Contenido | `app/content/lessons.json` | Las 80 clases derivadas del plan de temas |
| Generador | `app/tools/gen_content.py` | Reconstruye `lessons.json` desde el plan en Markdown |

---

## 7. Modelo de datos

**Contenido (`lessons.json`)** — resumido:

```json
{
  "version": "1.0",
  "levels": [{
    "id": 1, "name": "First Words", "age": "5 - 6 años", "cefr": "Pre-A1",
    "badge": "First Words Star", "emoji": "🐣",
    "units": [{
      "id": "1.1", "title": "Hello, Friends!", "emoji": "👋",
      "objective": "Saludar, despedirse, decir su nombre y expresar cómo se siente.",
      "words":   [{"en": "hello", "emoji": "👋"}, {"en": "happy", "emoji": "😊"}],
      "structures": [{"en": "What's your name? — My name is Ana."}],
      "classes": [{
        "n": 1, "focus": "Hello / Goodbye + rutina de círculo",
        "vocab": ["hello", "goodbye", "teacher"],
        "structure": "Hello, Milo! / Goodbye, Milo!",
        "activity": "El títere saluda a cada niño; canción de apertura",
        "evidence": "Responde al saludo con palabra + gesto",
        "tasks": ["flashcards", "listen", "sentence"]
      }]
    }]
  }]
}
```

**Progreso (local, nunca sale del dispositivo)**

```json
{ "stars": {"1.1.2": 3}, "done": ["1.1.1","1.1.2"], "badges": ["1"], "streak": 4, "lastDay": "2026-05-04" }
```

Las clases se desbloquean en orden; una clase se marca completada al terminar todas sus actividades, y la
estrella (1-3) depende de los aciertos al primer intento.

---

## 8. Audio, accesibilidad y experiencia infantil

- **Voz:** `TextToSpeech` del sistema en `en-US`, velocidad 0.9 (más lenta para niños) y tono normal. Si el
  dispositivo no tiene motor en inglés, la app avisa y sugiere instalarlo desde Ajustes.
- **Efectos:** aciertos y errores con sonidos cortos generados por Web Audio API (sin archivos externos).
- **Zonas táctiles:** mínimo 64 dp de alto, separación de 12 dp, sin gestos que exijan precisión.
- **Contraste y tipografía:** texto de 20-34 px, alto contraste sobre fondos claros, sin mayúsculas sostenidas.
- **Pre-lectores:** ningún botón depende de leer; los iconos llevan voz al tocarlos.
- **Accesibilidad:** etiquetas `aria-label` en botones, soporte de escalado de fuente del sistema, y opción de
  silenciar la voz sin perder los efectos.
- **Sin distracciones:** nada de publicidad, compras dentro de la app ni enlaces externos.

---

## 9. Gamificación y progresión

| Elemento | Cómo funciona |
| --- | --- |
| Estrellas | 1-3 por clase según aciertos al primer intento (3 = sin fallar) |
| Desbloqueo | Cada clase se abre al completar la anterior; las unidades, en orden |
| Insignias | Una por nivel, con el nombre del plan (`Little Explorer Badge`, `Young Speaker Award`, `Story Maker Medal`) |
| Racha | Días seguidos practicando, con la mascota celebrando a partir de 3 |
| Mascota | Milo, el títere del curso, presente en la cabecera y en las celebraciones |
| Mapa de progreso | Pantalla con las 80 clases y su estado, más el vocabulario ya practicado |

Sin vidas, sin monedas, sin cronómetros que presionen y sin comparaciones entre niños: solo avance personal.

---

## 10. Pantallas de la v1

1. **Inicio.** Mascota, saludo con el nombre del nivel si ya empezó, tarjetas de los 4 niveles con su progreso y
   botón de continuar donde se quedó.
2. **Nivel.** Ficha breve (edad, MCER, meta) y las 4 unidades con su avance y su proyecto.
3. **Unidad.** Objetivo, vocabulario de la unidad con voz, y las 5 clases con estrellas y estado de bloqueo.
4. **Lección.** Barra de avance, actividad actual y botón de salir. Al terminar: pantalla de logro con la
   evidencia de aprendizaje y las estrellas obtenidas.
5. **Progreso.** Estrellas totales, clases completadas, insignias conseguidas y racha.
6. **Ajustes.** Voz on/off, velocidad de voz, vibración on/off, reiniciar progreso (con confirmación).

---

## 11. Privacidad y modo sin conexión

- **Cero permisos de red:** el APK no declara `INTERNET`; es imposible que envíe datos.
- **Cero datos personales:** no hay registro, correo ni nombre de usuario. El progreso se guarda solo en el
  dispositivo y se borra al desinstalar.
- **Cumplimiento:** alineado con las políticas de Play para apps infantiles (Families Policy) y con la
  minimización de datos del RGPD/COPPA. La app no muestra anuncios ni enlaces a terceros.
- **Todo el contenido viaja dentro del APK:** funciona en modo avión, en el coche y sin wifi.

---

## 12. Compilación y firma del APK

El proyecto **no usa Gradle** (no hay caché de AGP ni `cmdline-tools` en el equipo y Maven Central respondió de
forma intermitente). Se compila con las herramientas del SDK ya instaladas, en un solo script:

```powershell
# app\tools\build-apk.ps1
1. aapt2 compile --dir res -o build\res.zip                      # recursos
2. aapt2 link -o build\base.apk -I android.jar --manifest AndroidManifest.xml `
       -R build\res.zip --java build\gen -A www --min-sdk-version 24 --target-sdk-version 35
3. javac -classpath android.jar -d build\classes build\gen\**\R.java java\**\MainActivity.java
4. d8 --lib android.jar --min-api 24 --output build\dex build\classes\**\*.class
5. Añadir classes.dex dentro de base.apk
6. zipalign -f 4 base.apk aligned.apk
7. apksigner sign --ks debug.keystore ... --out dist\LangKids-English-1.0.apk aligned.apk
8. aapt2 dump badging + apksigner verify                       # verificación automática
```

**Requisitos ya presentes en el equipo:** SDK en `%LOCALAPPDATA%\Android\Sdk` con plataformas android-35/36 y
build-tools 35/36, JDK 17 (`C:\Program Files\Java\jdk-17`), Node 24, Python 3.12 y `adb`.

**Para publicar en Play Store** hay que repetir la firma con un **keystore propio** (no el de depuración),
generado así:

```powershell
& "C:\Program Files\Java\jdk-17\bin\keytool.exe" -genkeypair -v -keystore langkids-release.jks `
  -alias langkids -keyalg RSA -keysize 2048 -validity 10000
# y firmar con --ks langkids-release.jks --ks-key-alias langkids
```

> Guardar ese keystore y su contraseña fuera del proyecto: sin él no se pueden publicar actualizaciones.

---

## 13. Pruebas y control de calidad

| Nivel de prueba | Qué se comprueba |
| --- | --- |
| Contenido | Que `lessons.json` tenga 4 niveles, 16 unidades, 80 clases y que ninguna lista de vocabulario esté vacía |
| Sintaxis | `node --check` sobre cada archivo JavaScript |
| Integridad del APK | `aapt2 dump badging` (paquete, versión, SDK, icono) y `apksigner verify` (firma válida) |
| En dispositivo | Instalar con `adb install -r`, abrir, recorrer una clase completa, girar/reanudar, botón atrás, modo avión |
| Experiencia infantil | Sesión de 10 minutos con un niño real: ¿entiende qué tocar sin ayuda?, ¿pide repetir?, ¿quiere seguir? |
| Accesibilidad | Fuente del sistema al 130 %, TalkBack en los botones principales, contraste verificado |

---

## 14. Publicación y distribución

**Opción A · Distribución directa (inmediata).** Enviar el APK por WhatsApp/Drive o instalarlo por cable con
`adb install`. En el teléfono hay que permitir «instalar apps de origen desconocido». Ideal para el aula y para
las familias del curso.

**Opción B · Google Play (recomendada para escalar).**
1. Cuenta de desarrollador (pago único de 25 USD).
2. Subir un **AAB** (Play exige formato de app bundle) firmado con el keystore de release; el script de build se
   amplía con `bundletool` para generarlo.
3. Completar la ficha: título, descripción, capturas, icono 512×512, gráfico destacado 1024×500.
4. Formularios obligatorios: **Data safety** (marcar «no recoge datos»), **clasificación por edades** y
   declaración de app dirigida a niños (Families Policy).
5. Revisión típica: 3-7 días.

**Opción C · PWA (sin tienda).** Publicar la carpeta `app/www` en cualquier hosting estático: en Android se abre
en Chrome y se instala con «Añadir a pantalla de inicio», con las mismas actividades (la voz la pone el
navegador).

---

## 15. Roadmap por fases

| Fase | Entregable | Estado |
| --- | --- | --- |
| **F0 · Plan** | Este documento: alcance, arquitectura, mapa de contenido y plan de pruebas | ✅ Terminado |
| **F1 · Contenido** | `lessons.json` con las 80 clases derivadas del plan de temas | ✅ Terminado (412 palabras) |
| **F2 · App web** | Pantallas, 6 motores de actividad, voz, progreso y gamificación | ✅ Terminado |
| **F3 · Envoltorio Android** | `MainActivity`, puente TTS, iconos, manifest | ✅ Terminado |
| **F4 · APK** | Compilación con aapt2/d8/apksigner y verificación | ✅ Terminado (190 KB, firmado) |
| **F5 · Pruebas** | Checklist en dispositivo real y ajustes de usabilidad infantil | 🟡 Emulador verificado; falta prueba con niños |
| **F6 · v1.1** | Pronunciación con micrófono, más palabras por lección, modo «reto diario» | Futuro |
| **F7 · v2.0** | Panel del docente, cuentas y sincronización, versión iOS con el mismo contenido | Futuro |

---

## 16. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| El dispositivo no tiene voz en inglés | La app queda muda | Detección al arrancar + aviso con instrucciones; efectos de sonido siempre disponibles |
| Palabras sin imagen clara (p. ej. «birthday») | Tarjeta pobre | Diccionario de emojis por palabra + respaldo por categoría de la unidad |
| El niño no sabe leer y se pierde | Abandono | Todo botón crítico lleva icono y voz; la navegación se hace desde dibujos |
| WebView antiguo en teléfonos viejos | Fallos de CSS/JS | Se usa JavaScript ES5-compatible y CSS sin funciones recientes; mínimo API 24 |
| Cambios en el currículo | Contenido desactualizado | `gen_content.py` regenera `lessons.json` desde el plan en Markdown |
| Publicar sin keystore de release | No se pueden publicar actualizaciones | Documentado y con comandos listos en la sección 12 |

---

## 17. Métricas de éxito

- **Producto:** una clase completada en menos de 6 minutos; 3+ clases por sesión en niños de 8 años.
- **Aprendizaje:** el niño nombra al menos 8 palabras nuevas por unidad sin apoyo.
- **Uso:** regreso a la app en 3 de 7 días (racha), sin recordatorios.
- **Familia:** puede ver el progreso sin explicación previa del docente.
- **Técnico:** APK < 5 MB, arranque < 2 s, cero fallos al girar el dispositivo o volver del segundo plano.

---

## 18. Anexo · Estructura del proyecto

```
LangKids/
├── Plan-de-Temas-LangKids-Niveles-1-a-4.md / .docx     ← currículo (fuente del contenido)
├── docs/
│   └── Plan-App-LangKids-Android.md / .docx            ← este documento
└── app/
    ├── content/lessons.json        ← 80 clases listas para la app (generado)
    ├── www/                        ← la app interactiva (también ejecutable en navegador)
    │   ├── index.html
    │   ├── css/styles.css
    │   ├── js/{app,activities,audio,store}.js
    │   ├── assets/icon.png
    │   └── manifest.webmanifest
    ├── android/
    │   ├── AndroidManifest.xml
    │   ├── java/com/langkids/english/MainActivity.java
    │   └── res/{values,mipmap-*,xml}
    ├── tools/
    │   ├── gen_content.py          ← currículo MD → lessons.json
    │   ├── make_icons.py           ← iconos de la app en 5 densidades
    │   ├── build-apk.ps1           ← compila y firma el APK
    │   └── build_docx.py           ← este plan en Word
    └── dist/LangKids-English-1.0.apk
```

---

*LangKids English · Plan de desarrollo v1.0 · Documento vivo: se actualiza al cerrar cada fase.*
