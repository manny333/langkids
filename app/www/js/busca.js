/* ==========================================================================
   busca.js — Busca y toca (I spy).

   Una escena con varios objetos y una instrucción hablada: "Find the apple!".
   El niño tiene que localizarlo entre los demás. Trabaja vocabulario en
   contexto y atención visual.
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
   * opciones: { palabras, rondas: 4, objetos: 6 }
   */
  function montar(cont, opciones, alTerminar) {
    var pool = (opciones.palabras || []).slice();
    if (pool.length < 8) { return null; }

    var rondas = opciones.rondas || 4;
    var cuantos = Math.min(opciones.objetos || 6, pool.length - 1);
    var ronda = 0;
    var aciertos = 0;
    var fallos = 0;
    var objetivo = null;
    var bloqueado = false;

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "busca-panel";

    var barra = document.createElement("div");
    barra.className = "busca-barra";
    var progreso = document.createElement("span");
    progreso.className = "busca-progreso";
    barra.appendChild(progreso);
    var repite = document.createElement("button");
    repite.className = "busca-repetir";
    repite.innerHTML = "🔊 Listen again";
    repite.setAttribute("aria-label", "listen again");
    repite.onclick = function () { decir(); };
    barra.appendChild(repite);
    panel.appendChild(barra);

    var pregunta = document.createElement("div");
    pregunta.className = "busca-pregunta";
    pregunta.textContent = "Find the…";
    panel.appendChild(pregunta);

    var escena = document.createElement("div");
    escena.className = "busca-escena";
    panel.appendChild(escena);
    cont.appendChild(panel);

    var objetos = [];

    function decir() {
      if (objetivo && global.Audio && global.Audio.speak) { global.Audio.speak(objetivo.en); }
    }

    function actualizar() {
      progreso.textContent = Math.min(ronda + 1, rondas) + " / " + rondas;
    }

    function repartir(n) {
      // rejilla 3x2 con algo de desorden para que parezca una escena
      var celdas = [];
      for (var f = 0; f < 2; f++) {
        for (var c = 0; c < 3; c++) { celdas.push({ f: f, c: c }); }
      }
      return barajar(celdas).slice(0, n);
    }

    function pintarRonda() {
      bloqueado = false;
      escena.innerHTML = "";
      objetos = [];
      actualizar();

      var elegidas = barajar(pool).slice(0, cuantos);
      objetivo = elegidas[Math.floor(Math.random() * elegidas.length)];
      var puestos = repartir(elegidas.length);

      elegidas.forEach(function (palabra, i) {
        var caja = document.createElement("button");
        caja.className = "busca-objeto";
        caja.dataset.palabra = palabra.en;
        caja.setAttribute("aria-label", palabra.en);
        var celda = puestos[i];
        caja.style.left = (celda.c * 33 + 2 + Math.random() * 5) + "%";
        caja.style.top = (celda.f * 46 + 3 + Math.random() * 7) + "%";
        caja.style.width = (19 + Math.random() * 2) + "%";

        var ruta = dibujoDe(palabra.en, palabra.img);
        if (ruta) {
          var img = document.createElement("img");
          img.src = ruta;
          img.alt = palabra.en;
          caja.appendChild(img);
        } else {
          var e = document.createElement("span");
          e.className = "busca-emoji";
          e.textContent = palabra.emoji || "❓";
          caja.appendChild(e);
        }

        caja.onclick = function () { tocar(caja, palabra); };
        escena.appendChild(caja);
        objetos.push(caja);
      });

      setTimeout(decir, 320);
    }

    function tocar(caja, palabra) {
      if (bloqueado) { return; }
      if (caja.classList.contains("encontrado")) { return; }

      if (palabra.en === objetivo.en) {
        bloqueado = true;
        aciertos++;
        caja.classList.add("encontrado");
        if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
        if (global.Audio && global.Audio.speak) { global.Audio.speak(palabra.en); }
        setTimeout(function () {
          ronda++;
          if (ronda >= rondas) {
            panel.classList.add("terminado");
            if (alTerminar) { alTerminar({ aciertos: aciertos, fallos: fallos, rondas: rondas }); }
            return;
          }
          pintarRonda();
        }, 1000);
        return;
      }

      fallos++;
      caja.classList.add("fallo");
      if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
      setTimeout(function () { caja.classList.remove("fallo"); }, 500);
    }

    pintarRonda();

    return {
      ronda: function () { return ronda; },
      aciertos: function () { return aciertos; },
      fallos: function () { return fallos; },
      objetivo: function () { return objetivo ? objetivo.en : null; },
      objetos: function () { return objetos; },
      /** para pruebas: toca el objeto correcto */
      _acertar: function () {
        var b = objetos.filter(function (o) { return o.dataset.palabra === (objetivo && objetivo.en); })[0];
        if (b) { b.click(); }
      }
    };
  }

  global.Busca = { montar: montar };
})(window);
