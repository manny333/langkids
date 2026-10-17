/* ==========================================================================
   falta.js — "¿Qué falta?" (What's missing?)

   Se muestran cuatro dibujos unos segundos. Luego uno desaparece y el niño
   tiene que tocar cuál era. Trabaja memoria visual y vocabulario.
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

  function dibujoDe(palabra, img) {
    if (img) { return global.Store ? global.Store.rutaImagen(img) : img; }
    var extra = global.LANGKIDS_IMG_MEMO || [];
    var buscar = String(palabra).toLowerCase();
    if (extra.indexOf(buscar) !== -1) { return "assets/img-memo/" + buscar + ".webp"; }
    return null;
  }

  /**
   * opciones: { palabras: [{en, img, emoji}], rondas: 4, espera: 2600 }
   */
  function montar(cont, opciones, alTerminar) {
    var pool = (opciones.palabras || []).slice();
    if (pool.length < 6) { return null; }

    var rondas = opciones.rondas || 4;
    var espera = (opciones.espera === undefined) ? 2600 : opciones.espera;
    var ronda = 0;
    var aciertos = 0;
    var fallos = 0;
    var fase = "mostrando";
    var faltante = null;
    var actuales = [];
    var temporizador = null;

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "falta-panel";

    var barra = document.createElement("div");
    barra.className = "falta-barra";
    var progreso = document.createElement("span");
    progreso.className = "falta-progreso";
    barra.appendChild(progreso);
    var pista = document.createElement("span");
    pista.className = "falta-pista";
    barra.appendChild(pista);
    panel.appendChild(barra);

    var escenario = document.createElement("div");
    escenario.className = "falta-escenario";
    panel.appendChild(escenario);

    var opcionescaja = document.createElement("div");
    opcionescaja.className = "falta-opciones";
    panel.appendChild(opcionescaja);
    cont.appendChild(panel);

    var huecos = [];
    var botones = [];

    function actualizar() {
      progreso.textContent = Math.min(ronda + 1, rondas) + " / " + rondas;
      pista.textContent = fase === "mostrando" ? "Look carefully…" : "What's missing?";
    }

    function limpiar() {
      if (temporizador) { clearTimeout(temporizador); temporizador = null; }
      escenario.innerHTML = "";
      opcionescaja.innerHTML = "";
      huecos = [];
      botones = [];
    }

    function pintarRonda() {
      limpiar();
      fase = "mostrando";
      actualizar();

      actuales = barajar(pool).slice(0, 4);
      faltante = actuales[Math.floor(Math.random() * 4)];

      actuales.forEach(function (palabra) {
        var hueco = document.createElement("div");
        hueco.className = "falta-hueco";
        hueco.dataset.palabra = palabra.en;

        var ruta = dibujoDe(palabra.en, palabra.img);
        if (ruta) {
          var img = document.createElement("img");
          img.src = ruta;
          img.alt = palabra.en;
          hueco.appendChild(img);
        } else {
          var e = document.createElement("span");
          e.className = "falta-emoji";
          e.textContent = palabra.emoji || "❓";
          hueco.appendChild(e);
        }
        escenario.appendChild(hueco);
        huecos.push(hueco);
      });

      temporizador = setTimeout(pasarAPregunta, espera);
    }

    function pasarAPregunta() {
      fase = "preguntando";
      actualizar();

      // el hueco del que falta se queda vacío
      huecos.forEach(function (h) {
        if (h.dataset.palabra === faltante.en) {
          h.classList.add("vacio");
          h.innerHTML = "";
        }
      });

      // opciones: el que falta + 3 distractores
      var distractores = barajar(pool.filter(function (p) { return p.en !== faltante.en; })).slice(0, 3);
      var opcionesRonda = barajar([faltante].concat(distractores));

      opcionesRonda.forEach(function (palabra) {
        var b = document.createElement("button");
        b.className = "falta-opcion";
        b.dataset.palabra = palabra.en;
        b.setAttribute("aria-label", palabra.en);

        var ruta = dibujoDe(palabra.en, palabra.img);
        if (ruta) {
          var img = document.createElement("img");
          img.src = ruta;
          img.alt = palabra.en;
          b.appendChild(img);
        } else {
          var e = document.createElement("span");
          e.className = "falta-emoji";
          e.textContent = palabra.emoji || "❓";
          b.appendChild(e);
        }

        b.onclick = function () { responder(b, palabra); };
        opcionescaja.appendChild(b);
        botones.push(b);
      });
    }

    function responder(boton, palabra) {
      if (fase !== "preguntando") { return; }
      if (boton.classList.contains("fallo") || boton.classList.contains("acierto")) { return; }

      if (palabra.en === faltante.en) {
        boton.classList.add("acierto");
        if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
        if (global.Audio && global.Audio.speak) { global.Audio.speak(palabra.en); }
        aciertos++;
        // rellenar el hueco vacío
        huecos.forEach(function (h) {
          if (h.dataset.palabra === faltante.en) {
            h.classList.remove("vacio");
            var ruta = dibujoDe(faltante.en, faltante.img);
            h.innerHTML = "";
            if (ruta) {
              var img = document.createElement("img");
              img.src = ruta;
              img.alt = faltante.en;
              h.appendChild(img);
            } else {
              h.textContent = faltante.emoji || "❓";
            }
            h.classList.add("encontrado");
          }
        });
        fase = "resuelto";
        ronda++;
        if (ronda >= rondas) {
          panel.classList.add("terminado");
          setTimeout(function () {
            if (alTerminar) { alTerminar({ aciertos: aciertos, fallos: fallos, rondas: rondas }); }
          }, 900);
          return;
        }
        temporizador = setTimeout(pintarRonda, 1100);
        return;
      }

      fallos++;
      boton.classList.add("fallo");
      if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
      setTimeout(function () { boton.classList.remove("fallo"); }, 500);
    }

    pintarRonda();

    return {
      huecos: function () { return huecos; },
      botones: function () { return botones; },
      fase: function () { return fase; },
      faltante: function () { return faltante ? faltante.en : null; },
      ronda: function () { return ronda; },
      aciertos: function () { return aciertos; },
      fallos: function () { return fallos; }
    };
  }

  global.Falta = { montar: montar, dibujoDe: dibujoDe };
})(window);
