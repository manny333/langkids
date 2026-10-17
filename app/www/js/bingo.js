/* ==========================================================================
   bingo.js — Bingo de palabras.

   El tablero es una rejilla 3x3 con nueve ilustraciones. La app dice una
   palabra en inglés y el niño toca el dibujo que corresponde. Al completar
   las nueve tarjetas, ¡bingo!
   ========================================================================== */
(function (global) {
  "use strict";

  function barajar(lista) {
    var a = lista.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /** Devuelve la ilustración de una palabra (curso o extra de memorama). */
  function dibujoDe(palabra, img) {
    if (img) { return global.Store ? global.Store.rutaImagen(img) : img; }
    var extra = global.LANGKIDS_IMG_MEMO || [];
    var buscar = String(palabra).toLowerCase();
    if (extra.indexOf(buscar) !== -1) { return "assets/img-memo/" + buscar + ".webp"; }
    return null;
  }

  /**
   * Monta un tablero de bingo.
   * opciones: { palabras: [{en, img, emoji}], titulo: "Level 1" }
   */
  function montar(cont, opciones, alGanar) {
    var pool = (opciones.palabras || []).slice();
    if (pool.length < 9) { return null; }

    var elegidas = barajar(pool).slice(0, 9);
    var orden = barajar(elegidas);
    var turno = 0;
    var aciertos = 0;
    var fallos = 0;

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "bingo-panel";

    var barra = document.createElement("div");
    barra.className = "bingo-barra";
    var progreso = document.createElement("span");
    progreso.className = "bingo-progreso";
    barra.appendChild(progreso);

    var repetir = document.createElement("button");
    repetir.className = "bingo-repetir";
    repetir.setAttribute("aria-label", "listen again");
    repetir.innerHTML = "🔊 Listen again";
    repetir.onclick = function () { decir(); };
    barra.appendChild(repetir);
    panel.appendChild(barra);

    var tablero = document.createElement("div");
    tablero.className = "bingo-tablero";
    panel.appendChild(tablero);
    cont.appendChild(panel);

    var celdas = elegidas.map(function (palabra) {
      var b = document.createElement("button");
      b.className = "bingo-celda";
      b.setAttribute("aria-label", palabra.en);
      b.dataset.palabra = palabra.en;

      var ruta = dibujoDe(palabra.en, palabra.img);
      if (ruta) {
        var img = document.createElement("img");
        img.src = ruta;
        img.alt = palabra.en;
        b.appendChild(img);
      } else {
        var e = document.createElement("span");
        e.className = "bingo-emoji";
        e.textContent = palabra.emoji || "❓";
        b.appendChild(e);
      }

      var marca = document.createElement("span");
      marca.className = "bingo-marca";
      marca.textContent = "✓";
      b.appendChild(marca);

      b.onclick = function () { tocar(b, palabra); };
      tablero.appendChild(b);
      return b;
    });

    function actualizar() {
      progreso.textContent = aciertos + " / 9";
    }
    actualizar();

    function decir() {
      var actual = orden[turno];
      if (!actual) { return; }
      if (global.Audio && global.Audio.speak) { global.Audio.speak(actual.en); }
    }

    function tocar(nodo, palabra) {
      if (nodo.classList.contains("hecha")) { return; }
      var actual = orden[turno];

      if (actual && palabra.en === actual.en) {
        nodo.classList.add("hecha");
        if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
        aciertos++;
        turno++;
        actualizar();
        if (aciertos >= 9) {
          panel.classList.add("ganado");
          if (alGanar) { alGanar({ aciertos: aciertos, fallos: fallos }); }
          return;
        }
        setTimeout(decir, 700);
        return;
      }

      // fallo: se marca un momento y se avisa
      fallos++;
      nodo.classList.add("fallo");
      if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
      setTimeout(function () { nodo.classList.remove("fallo"); }, 520);
    }

    setTimeout(decir, 500);

    return {
      celdas: celdas,
      orden: orden,
      aciertos: function () { return aciertos; },
      fallos: function () { return fallos; },
      actual: function () { return orden[turno] ? orden[turno].en : null; }
    };
  }

  global.Bingo = { montar: montar, dibujoDe: dibujoDe };
})(window);
