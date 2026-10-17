/* ==========================================================================
   traza.js — Trazar la palabra (writing practice).

   Muestra la palabra en gris claro y el niño la repasa con el dedo. Cuando
   cubre la mayor parte de las letras, la palabra se marca como hecha y se
   escucha en inglés. Sirve de puente entre reconocer el dibujo y escribir.
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
   * opciones: { palabras, meta: 0.42, cuantas: 5, color: "#7C61FF" }
   */
  function montar(cont, opciones, alTerminar) {
    var pool = (opciones.palabras || []).slice();
    if (!pool.length) { return null; }

    var meta = opciones.meta === undefined ? 0.42 : opciones.meta;
    var cuantas = Math.min(opciones.cuantas || 5, pool.length);
    var color = opciones.color || "#7C61FF";
    var lista = barajar(pool).slice(0, cuantas);

    var indice = 0;
    var trazos = [];
    var actual = null;
    var cubierta = 0;
    var hechas = 0;
    var fallos = 0;
    var bloqueado = false;

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "traza-panel";

    /* --- cabecera: imagen + palabra --- */
    var cab = document.createElement("div");
    cab.className = "traza-cab";
    var miniatura = document.createElement("img");
    miniatura.className = "traza-mini";
    miniatura.alt = "";
    cab.appendChild(miniatura);

    var bloque = document.createElement("div");
    bloque.className = "traza-texto";
    var palabraTxt = document.createElement("div");
    palabraTxt.className = "traza-palabra";
    bloque.appendChild(palabraTxt);
    var progreso = document.createElement("div");
    progreso.className = "traza-progreso";
    bloque.appendChild(progreso);
    cab.appendChild(bloque);

    var escuchar = document.createElement("button");
    escuchar.className = "traza-btn";
    escuchar.innerHTML = "🔊";
    escuchar.setAttribute("aria-label", "listen");
    escuchar.onclick = function () { decir(); };
    cab.appendChild(escuchar);
    panel.appendChild(cab);

    /* --- lienzo --- */
    var marco = document.createElement("div");
    marco.className = "traza-marco";
    var lienzo = document.createElement("canvas");
    lienzo.className = "traza-lienzo";
    marco.appendChild(lienzo);
    panel.appendChild(marco);

    var pie = document.createElement("div");
    pie.className = "traza-pie";
    var limpiar = document.createElement("button");
    limpiar.className = "traza-btn largo";
    limpiar.textContent = "🧽 Clear";
    limpiar.onclick = function () { trazos = []; pintar(); medir(); };
    pie.appendChild(limpiar);
    panel.appendChild(pie);

    cont.appendChild(panel);

    var ctx = lienzo.getContext("2d");
    var mascara = document.createElement("canvas");
    var mctx = mascara.getContext("2d");
    // capa que contiene solo lo que pinta el niño (sin la letra guía)
    var tinta = document.createElement("canvas");
    var ictx = tinta.getContext("2d");
    var pincel = 26;
    var dpr = 1;

    function palabraActual() { return lista[indice]; }

    function decir() {
      var p = palabraActual();
      if (p && global.Audio && global.Audio.speak) { global.Audio.speak(p.en); }
    }

    function ajustar() {
      var caja = marco.getBoundingClientRect();
      if (caja.width < 20 || caja.height < 20) { return; }
      dpr = global.devicePixelRatio || 1;
      lienzo.width = Math.floor(caja.width * dpr);
      lienzo.height = Math.floor(caja.height * dpr);
      mascara.width = lienzo.width;
      mascara.height = lienzo.height;
      tinta.width = lienzo.width;
      tinta.height = lienzo.height;
      construirMascara();
      pintar();
      medir();
    }

    function construirMascara() {
      var ancho = mascara.width, alto = mascara.height;
      mctx.clearRect(0, 0, ancho, alto);
      var palabra = palabraActual();
      if (!palabra) { return; }
      var tam = Math.min(alto * 0.62, ancho / Math.max(3.6, palabra.en.length * 0.62));
      mctx.font = "800 " + tam + "px 'Baloo 2', 'Nunito', system-ui, sans-serif";
      mctx.textAlign = "center";
      mctx.textBaseline = "middle";
      mctx.fillStyle = "#000";
      mctx.fillText(palabra.en, ancho / 2, alto / 2);
    }

    function pintar() {
      ctx.clearRect(0, 0, lienzo.width, lienzo.height);
      ictx.clearRect(0, 0, tinta.width, tinta.height);

      // la palabra en gris claro
      var palabra = palabraActual();
      if (palabra) {
        var tam = Math.min(lienzo.height * 0.62, lienzo.width / Math.max(3.6, palabra.en.length * 0.62));
        ctx.font = "800 " + tam + "px 'Baloo 2', 'Nunito', system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = "rgba(43,45,66,.20)";
        ctx.fillText(palabra.en, lienzo.width / 2, lienzo.height / 2);
      }

      // los trazos del niño
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.strokeStyle = color;
      ctx.lineWidth = pincel * dpr;
      trazos.forEach(function (t) {
        [ctx, ictx].forEach(function (c) {
          c.lineCap = "round";
          c.lineJoin = "round";
          c.strokeStyle = "#000";
          c.fillStyle = "#000";
          c.lineWidth = pincel * dpr;
          if (t.puntos.length === 1) {
            var p = t.puntos[0];
            c.beginPath();
            c.arc(p.x, p.y, c.lineWidth / 2, 0, Math.PI * 2);
            c.fill();
            return;
          }
          c.beginPath();
          c.moveTo(t.puntos[0].x, t.puntos[0].y);
          for (var i = 1; i < t.puntos.length; i++) { c.lineTo(t.puntos[i].x, t.puntos[i].y); }
          c.stroke();
        });
      });
      // el color del trazo se aplica aparte para la vista
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
    }

    /** Mide qué parte de las letras está cubierta por los trazos. */
    function medir() {
      if (!mascara.width) { return 0; }
      var m = mctx.getImageData(0, 0, mascara.width, mascara.height).data;
      var p = ictx.getImageData(0, 0, tinta.width, tinta.height).data;
      var total = 0, tapados = 0;
      var salto = 3;
      var ancho = mascara.width;
      for (var y = 0; y < mascara.height; y += salto) {
        for (var x = 0; x < ancho; x += salto) {
          var i = (y * ancho + x) * 4 + 3;
          if (m[i] < 120) { continue; }
          total++;
          if (p[i] > 40) { tapados++; }
        }
      }
      cubierta = total ? (tapados / total) : 0;
      progreso.textContent = Math.round(cubierta * 100) + "% · " +
        (indice + 1) + " / " + cuantas;

      if (cubierta >= meta && !bloqueado) { completar(); }
      return cubierta;
    }

    function completar() {
      bloqueado = true;
      hechas++;
      panel.classList.add("hecho");
      if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
      decir();
      setTimeout(function () {
        panel.classList.remove("hecho");
        indice++;
        trazos = [];
        cubierta = 0;
        bloqueado = false;
        if (indice >= cuantas) {
          panel.classList.add("terminado");
          if (alTerminar) { alTerminar({ hechas: hechas, fallos: fallos, cuantas: cuantas }); }
          return;
        }
        pintarRonda();
      }, 1100);
    }

    function pintarRonda() {
      var p = palabraActual();
      if (!p) { return; }
      palabraTxt.textContent = p.en;
      var ruta = dibujoDe(p.en, p.img);
      if (ruta) { miniatura.src = ruta; miniatura.style.display = ""; }
      else { miniatura.removeAttribute("src"); miniatura.style.display = "none"; }
      construirMascara();
      pintar();
      medir();
      setTimeout(decir, 350);
    }

    /* --- dibujo con el dedo --- */
    function punto(ev) {
      var caja = marco.getBoundingClientRect();
      return { x: (ev.clientX - caja.left) * dpr, y: (ev.clientY - caja.top) * dpr };
    }

    lienzo.addEventListener("pointerdown", function (ev) {
      ev.preventDefault();
      if (bloqueado) { return; }
      if (lienzo.setPointerCapture) {
        try { lienzo.setPointerCapture(ev.pointerId); } catch (e) { }
      }
      actual = { puntos: [punto(ev)] };
      trazos.push(actual);
      pintar();
    });

    lienzo.addEventListener("pointermove", function (ev) {
      if (!actual || bloqueado) { return; }
      ev.preventDefault();
      actual.puntos.push(punto(ev));
      pintar();
    });

    function soltar() {
      if (!actual) { return; }
      actual = null;
      medir();
    }
    lienzo.addEventListener("pointerup", soltar);
    lienzo.addEventListener("pointercancel", soltar);
    lienzo.addEventListener("pointerleave", soltar);

    global.addEventListener("resize", ajustar);
    setTimeout(ajustar, 80);
    setTimeout(ajustar, 260);
    pintarRonda();

    return {
      ajustar: ajustar,
      cobertura: function () { return cubierta; },
      palabra: function () { return palabraActual() ? palabraActual().en : null; },
      hechas: function () { return hechas; },
      ronda: function () { return indice; },
      meta: meta,
      /** para pruebas: marca la palabra como cubierta */
      _forzar: function () { completar(); }
    };
  }

  global.Traza = { montar: montar };
})(window);
