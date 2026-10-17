/* ==========================================================================
   repaso.js — Repaso inteligente.

   Sesión corta de 10 palabras elegidas por el Store (primero las que el niño
   ha fallado). Alterna dos tipos de pregunta para trabajar escucha y lectura:
     · oír la palabra  -> tocar el dibujo
     · ver el dibujo   -> tocar la palabra escrita
   Cada respuesta se anota en la memoria por palabra.
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
    return null;
  }

  /**
   * opciones: { palabras: [...], cuantas: 10, alAnotar: fn }
   */
  function montar(cont, opciones, alTerminar) {
    var todas = (opciones.palabras || []).slice();
    if (todas.length < 4) { return null; }

    var cuantas = Math.min(opciones.cuantas || 10, todas.length);
    var ronda = 0;
    var aciertos = 0;
    var fallos = 0;
    var resuelto = false;
    var elegidas = global.Store
      ? global.Store.palabrasPrioritarias(todas, cuantas)
      : barajar(todas).slice(0, cuantas);

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "repaso-panel";

    var barra = document.createElement("div");
    barra.className = "repaso-barra";
    var progreso = document.createElement("span");
    progreso.className = "repaso-progreso";
    barra.appendChild(progreso);
    var repite = document.createElement("button");
    repite.className = "repaso-repetir";
    repite.setAttribute("aria-label", "listen again");
    repite.innerHTML = "🔊 Listen again";
    barra.appendChild(repite);
    panel.appendChild(barra);

    var enunciado = document.createElement("div");
    enunciado.className = "repaso-enunciado";
    panel.appendChild(enunciado);

    var cuerpo = document.createElement("div");
    cuerpo.className = "repaso-cuerpo";
    panel.appendChild(cuerpo);
    cont.appendChild(panel);

    var opcionesActuales = [];

    function actualizar() {
      progreso.textContent = Math.min(ronda + 1, cuantas) + " / " + cuantas;
    }

    function decir() {
      var p = elegidas[ronda];
      if (p && global.Audio && global.Audio.speak) { global.Audio.speak(p.en); }
    }
    repite.onclick = function () { decir(); };

    function pintarRonda() {
      resuelto = false;
      cuerpo.innerHTML = "";
      enunciado.innerHTML = "";
      actualizar();

      var objetivo = elegidas[ronda];
      if (!objetivo) { terminar(); return; }

      var escuchar = (ronda % 2 === 0);   // alterna escucha / lectura
      var distractores = barajar(todas.filter(function (p) { return p.en !== objetivo.en; })).slice(0, 3);
      opcionesActuales = barajar([objetivo].concat(distractores));

      cuerpo.className = "repaso-cuerpo" + (escuchar ? " solo-imagenes" : "");
      if (escuchar) {
        enunciado.appendChild(document.createTextNode("Listen… then tap the picture"));
        enunciado.className = "repaso-enunciado";
        setTimeout(decir, 350);
      } else {
        var ruta = dibujoDe(objetivo.en, objetivo.img);
        var marco = document.createElement("div");
        marco.className = "repaso-foto";
        if (ruta) {
          var img = document.createElement("img");
          img.src = ruta;
          img.alt = objetivo.en;
          marco.appendChild(img);
        } else {
          marco.textContent = objetivo.emoji || "❓";
        }
        cuerpo.appendChild(marco);
        enunciado.textContent = "Tap the correct word";
      }

      var grid = document.createElement("div");
      grid.className = "repaso-opciones" + (escuchar ? "" : " solo-texto");
      opcionesActuales.forEach(function (palabra) {
        var b = document.createElement("button");
        b.className = "repaso-opcion";
        b.dataset.palabra = palabra.en;
        b.setAttribute("aria-label", palabra.en);

        if (escuchar) {
          var r = dibujoDe(palabra.en, palabra.img);
          if (r) {
            var im = document.createElement("img");
            im.src = r;
            im.alt = palabra.en;
            b.appendChild(im);
          } else {
            var e = document.createElement("span");
            e.className = "repaso-emoji";
            e.textContent = palabra.emoji || "❓";
            b.appendChild(e);
          }
        } else {
          b.textContent = palabra.en;
        }

        b.onclick = function () { responder(b, palabra, objetivo); };
        grid.appendChild(b);
      });
      cuerpo.appendChild(grid);
      actualizar();
    }

    function responder(boton, palabra, objetivo) {
      if (resuelto) { return; }
      var bien = palabra.en === objetivo.en;

      if (global.Store) { global.Store.notaPalabra(objetivo.en, bien); }
      if (opciones.alAnotar) { opciones.alAnotar(objetivo.en, bien); }

      if (!bien) {
        fallos++;
        boton.classList.add("fallo");
        if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
        setTimeout(function () { boton.classList.remove("fallo"); }, 500);
        return;
      }

      resuelto = true;
      aciertos++;
      boton.classList.add("acierto");
      if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
      if (global.Audio && global.Audio.speak) { global.Audio.speak(objetivo.en); }
      ronda++;
      setTimeout(function () {
        if (ronda >= cuantas) { terminar(); } else { pintarRonda(); }
      }, 900);
    }

    function terminar() {
      panel.classList.add("terminado");
      if (alTerminar) { alTerminar({ aciertos: aciertos, fallos: fallos, cuantas: cuantas }); }
    }

    pintarRonda();

    return {
      ronda: function () { return ronda; },
      aciertos: function () { return aciertos; },
      fallos: function () { return fallos; },
      elegidas: function () { return elegidas.map(function (p) { return p.en; }); },
      opciones: function () { return opcionesActuales.map(function (p) { return p.en; }); },
      /** para pruebas: responde la opción correcta */
      _acertar: function () {
        var objetivo = elegidas[ronda];
        if (!objetivo) { return; }
        var botones = [].slice.call(cuerpo.querySelectorAll(".repaso-opcion"));
        var bueno = botones.filter(function (b) { return b.dataset.palabra === objetivo.en; })[0];
        if (bueno) { bueno.click(); }
      }
    };
  }

  global.Repaso = { montar: montar };
})(window);
