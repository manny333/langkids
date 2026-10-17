/* ==========================================================================
   domino.js — Dominó palabra-imagen.

   La cadena empieza con un dibujo. El niño elige, entre tres fichas, la que
   lleva la PALABRA de ese dibujo; al colocarla, el otro extremo de la ficha
   (un dibujo nuevo) pasa a ser el extremo abierto. Une lectura y vocabulario.
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

  function mediaFicha(palabra, tipo) {
    var d = document.createElement("div");
    d.className = "domi-media";
    if (tipo === "img") {
      var ruta = dibujoDe(palabra.en, palabra.img);
      if (ruta) {
        var img = document.createElement("img");
        img.src = ruta;
        img.alt = palabra.en;
        d.appendChild(img);
      } else {
        d.textContent = palabra.emoji || "❓";
      }
    } else {
      d.classList.add("texto");
      d.textContent = palabra.en;
    }
    return d;
  }

  /**
   * opciones: { palabras, colocaciones: 4 }
   */
  function montar(cont, opciones, alTerminar) {
    var pool = (opciones.palabras || []).slice();
    if (pool.length < 8) { return null; }

    var colocaciones = Math.min(opciones.colocaciones || 4, pool.length - 1);
    var cadena = barajar(pool).slice(0, colocaciones + 1);
    var turno = 0;
    var aciertos = 0;
    var fallos = 0;
    var bloqueado = false;
    var fichas = [];

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "domi-panel";

    var barra = document.createElement("div");
    barra.className = "domi-barra";
    var progreso = document.createElement("span");
    progreso.className = "domi-progreso";
    barra.appendChild(progreso);
    var pista = document.createElement("span");
    pista.className = "domi-pista";
    pista.textContent = "Match the word!";
    barra.appendChild(pista);
    panel.appendChild(barra);

    var mesa = document.createElement("div");
    mesa.className = "domi-mesa";
    panel.appendChild(mesa);

    var mano = document.createElement("div");
    mano.className = "domi-mano";
    panel.appendChild(mano);
    cont.appendChild(panel);

    function actualizar() {
      progreso.textContent = Math.min(turno, colocaciones) + " / " + colocaciones;
    }

    function fichaHTML(palabraIzq, palabraDer) {
      var f = document.createElement("div");
      f.className = "domi-ficha";
      f.appendChild(mediaFicha(palabraIzq, "img"));
      var linea = document.createElement("span");
      linea.className = "domi-linea";
      f.appendChild(linea);
      f.appendChild(mediaFicha(palabraDer, "txt"));
      return f;
    }

    function pintarCadena() {
      mesa.innerHTML = "";
      var inicio = document.createElement("div");
      inicio.className = "domi-ficha inicial";
      inicio.appendChild(mediaFicha({ en: cadena[0].en, img: cadena[0].img, emoji: cadena[0].emoji }, "img"));
      mesa.appendChild(inicio);

      for (var i = 1; i <= turno; i++) {
        var f = fichaHTML(cadena[i - 1], cadena[i]);
        // el último dibujo de la cadena es el extremo abierto
        if (i === turno) { f.classList.add("abierta"); }
        mesa.appendChild(f);
      }
      if (turno === 0) { inicio.classList.add("abierta"); }
      mesa.scrollLeft = mesa.scrollWidth;
    }

    function pintarMano() {
      mano.innerHTML = "";
      if (turno >= colocaciones) { return; }

      var abierta = cadena[turno];
      var correcta = { izq: abierta, der: cadena[turno + 1], ok: true };

      // los señuelos llevan OTRA palabra y OTRO dibujo: hay que leer para elegir
      var otros = barajar(pool.filter(function (p) {
        return p.en !== abierta.en && p.en !== cadena[turno + 1].en;
      }));

      var opcionesRonda = [correcta];
      for (var i = 0; i < otros.length && opcionesRonda.length < 3; i++) {
        var der = otros[(i + 1) % otros.length];
        if (der.en === otros[i].en) { continue; }
        opcionesRonda.push({ izq: otros[i], der: der, ok: false });
      }

      fichas = [];
      barajar(opcionesRonda).forEach(function (op) {
        var b = document.createElement("button");
        b.className = "domi-opcion";
        b.dataset.palabra = op.der.en;
        b.dataset.ok = op.ok ? "1" : "0";
        b.setAttribute("aria-label", op.der.en);
        b.appendChild(mediaFicha(op.izq, "txt"));
        var linea = document.createElement("span");
        linea.className = "domi-linea";
        b.appendChild(linea);
        b.appendChild(mediaFicha(op.der, "img"));
        b.onclick = function () { elegir(b, op); };
        mano.appendChild(b);
        fichas.push(b);
      });
    }

    function elegir(nodo, op) {
      if (bloqueado) { return; }
      if (!op.ok) {
        fallos++;
        nodo.classList.add("fallo");
        if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
        setTimeout(function () { nodo.classList.remove("fallo"); }, 500);
        return;
      }

      bloqueado = true;
      aciertos++;
      nodo.classList.add("acierto");
      if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
      if (global.Audio && global.Audio.speak) { global.Audio.speak(op.der.en); }

      turno++;
      actualizar();
      setTimeout(function () {
        pintarCadena();
        bloqueado = false;
        if (turno >= colocaciones) {
          panel.classList.add("terminado");
          if (alTerminar) { alTerminar({ aciertos: aciertos, fallos: fallos, colocaciones: colocaciones }); }
          return;
        }
        pintarMano();
      }, 620);
    }

    pintarCadena();
    pintarMano();
    actualizar();

    return {
      cadena: function () { return cadena.map(function (p) { return p.en; }); },
      turno: function () { return turno; },
      aciertos: function () { return aciertos; },
      fallos: function () { return fallos; },
      fichas: function () { return fichas; },
      /** para pruebas: pulsa la ficha correcta */
      _acertar: function () {
        var b = fichas.filter(function (f) { return f.dataset.ok === "1"; })[0];
        if (b) { b.click(); }
      }
    };
  }

  global.Domino = { montar: montar };
})(window);
