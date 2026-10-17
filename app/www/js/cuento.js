/* ==========================================================================
   cuento.js — Cuentos cortos por unidad.

   Cada cuento son cuatro escenas de una frase y, al final, dos preguntas de
   comprensión. La app lee la frase en inglés y el niño puede tocar las
   palabras del cuento para oírlas otra vez.
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

  function imgDe(palabra) {
    var lv = (global.LANGKIDS_CONTENT || {}).levels || [];
    for (var i = 0; i < lv.length; i++) {
      for (var j = 0; j < lv[i].units.length; j++) {
        var ws = lv[i].units[j].words || [];
        for (var k = 0; k < ws.length; k++) {
          if (ws[k].en.toLowerCase() === String(palabra).toLowerCase() && ws[k].img) {
            return ws[k].img;
          }
        }
      }
    }
    var extra = global.LANGKIDS_IMG_MEMO || [];
    if (extra.indexOf(String(palabra).toLowerCase()) !== -1) {
      return "assets/img-memo/" + String(palabra).toLowerCase() + ".webp";
    }
    return null;
  }

  function emojiDe(palabra) {
    var lv = (global.LANGKIDS_CONTENT || {}).levels || [];
    for (var i = 0; i < lv.length; i++) {
      for (var j = 0; j < lv[i].units.length; j++) {
        var ws = lv[i].units[j].words || [];
        for (var k = 0; k < ws.length; k++) {
          if (ws[k].en.toLowerCase() === String(palabra).toLowerCase()) {
            return ws[k].emoji || "❓";
          }
        }
      }
    }
    return "❓";
  }

  /**
   * opciones: { cuento: {titulo, escenas:[{texto, palabras}], preguntas:[{palabra}]} }
   */
  function montar(cont, opciones, alTerminar) {
    var cuento = opciones.cuento;
    if (!cuento || !cuento.escenas || !cuento.escenas.length) { return null; }

    var escena = 0;
    var preguntas = cuento.preguntas || [];
    var enPreguntas = false;
    var indicePregunta = 0;
    var aciertos = 0;
    var fallos = 0;

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "cuento-panel";

    var barra = document.createElement("div");
    barra.className = "cuento-barra";
    var progreso = document.createElement("span");
    progreso.className = "cuento-progreso";
    barra.appendChild(progreso);
    var repetir = document.createElement("button");
    repetir.className = "cuento-repetir";
    repetir.innerHTML = "🔊 Read again";
    barra.appendChild(repetir);
    panel.appendChild(barra);

    var pagina = document.createElement("div");
    pagina.className = "cuento-pagina";
    panel.appendChild(pagina);

    var pie = document.createElement("div");
    pie.className = "cuento-pie";
    var siguiente = document.createElement("button");
    siguiente.className = "cuento-btn";
    siguiente.textContent = "Next ▶";
    pie.appendChild(siguiente);
    panel.appendChild(pie);
    cont.appendChild(panel);

    function actualizar() {
      if (enPreguntas) {
        progreso.textContent = "Question " + (indicePregunta + 1) + " / " + preguntas.length;
      } else {
        progreso.textContent = "Page " + (escena + 1) + " / " + cuento.escenas.length;
      }
    }

    function leerEscena() {
      var e = cuento.escenas[escena];
      if (e && global.Audio && global.Audio.speak) { global.Audio.speak(e.texto); }
    }

    function leerPregunta() {
      var p = preguntas[indicePregunta];
      if (p && global.Audio && global.Audio.speak) {
        global.Audio.speak("Find " + p.palabra + ". " + (p.texto || ""));
      }
    }

    repetir.onclick = function () {
      if (enPreguntas) { leerPregunta(); } else { leerEscena(); }
    };

    function pintarEscena() {
      actualizar();
      pagina.innerHTML = "";
      pie.style.display = "";

      var e = cuento.escenas[escena];
      var texto = document.createElement("p");
      texto.className = "cuento-texto";
      texto.textContent = e.texto;
      pagina.appendChild(texto);

      var tira = document.createElement("div");
      tira.className = "cuento-tira";
      (e.palabras || []).forEach(function (palabra) {
        var b = document.createElement("button");
        b.className = "cuento-ficha";
        var ruta = imgDe(palabra);
        if (ruta) {
          var img = document.createElement("img");
          img.src = ruta;
          img.alt = palabra;
          b.appendChild(img);
        } else {
          var em = document.createElement("span");
          em.className = "cuento-emoji";
          em.textContent = emojiDe(palabra);
          b.appendChild(em);
        }
        var et = document.createElement("span");
        et.className = "cuento-palabra";
        et.textContent = palabra;
        b.appendChild(et);
        b.onclick = function () {
          if (global.Audio && global.Audio.speak) { global.Audio.speak(palabra); }
        };
        tira.appendChild(b);
      });
      pagina.appendChild(tira);

      setTimeout(leerEscena, 300);
    }

    function pintarPregunta() {
      actualizar();
      pagina.innerHTML = "";
      pie.style.display = "none";

      var p = preguntas[indicePregunta];
      var titulo = document.createElement("p");
      titulo.className = "cuento-texto";
      titulo.textContent = "Which one is " + p.palabra + "?";
      pagina.appendChild(titulo);

      var opciones = barajar(p.opciones && p.opciones.length ? p.opciones : [p.palabra]);
      var fila = document.createElement("div");
      fila.className = "cuento-opciones";
      opciones.forEach(function (palabra) {
        var b = document.createElement("button");
        b.className = "cuento-opcion";
        b.dataset.palabra = palabra;
        var ruta = imgDe(palabra);
        if (ruta) {
          var img = document.createElement("img");
          img.src = ruta;
          img.alt = palabra;
          b.appendChild(img);
        } else {
          var em = document.createElement("span");
          em.className = "cuento-emoji";
          em.textContent = emojiDe(palabra);
          b.appendChild(em);
        }
        b.onclick = function () { responder(b, palabra, p); };
        fila.appendChild(b);
      });
      pagina.appendChild(fila);
      setTimeout(leerPregunta, 300);
    }

    function responder(boton, palabra, pregunta) {
      if (boton.classList.contains("ok") || boton.classList.contains("ko")) { return; }
      if (palabra === pregunta.palabra) {
        boton.classList.add("ok");
        aciertos++;
        if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
        if (global.Audio && global.Audio.speak) { global.Audio.speak(palabra); }
        setTimeout(function () {
          indicePregunta++;
          if (indicePregunta >= preguntas.length) {
            terminar();
          } else {
            pintarPregunta();
          }
        }, 900);
        return;
      }
      fallos++;
      boton.classList.add("ko");
      if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
      setTimeout(function () { boton.classList.remove("ko"); }, 500);
    }

    function terminar() {
      panel.classList.add("terminado");
      if (alTerminar) { alTerminar({ aciertos: aciertos, fallos: fallos, preguntas: preguntas.length }); }
    }

    siguiente.onclick = function () {
      if (enPreguntas) { return; }
      if (escena + 1 < cuento.escenas.length) {
        escena++;
        pintarEscena();
        return;
      }
      if (preguntas.length) {
        enPreguntas = true;
        indicePregunta = 0;
        pintarPregunta();
      } else {
        terminar();
      }
    };

    pintarEscena();

    return {
      escena: function () { return escena; },
      enPreguntas: function () { return enPreguntas; },
      aciertos: function () { return aciertos; },
      fallos: function () { return fallos; },
      siguiente: function () { siguiente.click(); }
    };
  }

  global.Cuento = { montar: montar, imgDe: imgDe };
})(window);
