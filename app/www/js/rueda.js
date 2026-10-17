/* ==========================================================================
   rueda.js — Rueda de palabras.

   Gira una ruleta con seis dibujos y se detiene en uno. El niño dice la
   palabra en voz alta, escucha cómo suena y sigue girando.
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

  var COLORES = ["#FF6B6B", "#FFB703", "#4ECDC4", "#7C61FF", "#34C759", "#38BDF8"];

  /**
   * opciones: { palabras, giros: 8 }
   */
  function montar(cont, opciones, alTerminar) {
    var pool = (opciones.palabras || []).slice();
    if (pool.length < 6) { return null; }

    var giros = opciones.giros || 8;
    var duracion = opciones.rapido ? 120 : 3400;
    var hechos = 0;
    var ronda = 0;
    var girando = false;
    var angulo = 0;
    var seleccion = [];
    var actual = null;

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "rueda-panel";

    var barra = document.createElement("div");
    barra.className = "rueda-barra";
    var progreso = document.createElement("span");
    progreso.className = "rueda-progreso";
    barra.appendChild(progreso);
    panel.appendChild(barra);

    var zona = document.createElement("div");
    zona.className = "rueda-zona";
    var rueda = document.createElement("div");
    rueda.className = "rueda";
    var aguja = document.createElement("div");
    aguja.className = "rueda-aguja";
    zona.appendChild(rueda);
    zona.appendChild(aguja);
    panel.appendChild(zona);

    var resultado = document.createElement("div");
    resultado.className = "rueda-resultado";
    panel.appendChild(resultado);

    var botones = document.createElement("div");
    botones.className = "rueda-botones";
    var girar = document.createElement("button");
    girar.className = "rueda-btn";
    girar.textContent = "🎡 Spin";
    var repetir = document.createElement("button");
    repetir.className = "rueda-btn suave";
    repetir.textContent = "🔊 Listen";
    botones.appendChild(girar);
    botones.appendChild(repetir);
    panel.appendChild(botones);
    cont.appendChild(panel);

    function actualizar() {
      progreso.textContent = hechos + " / " + giros;
    }

    function pintarRueda() {
      // seis sectores de color con su dibujo alrededor
      seleccion = barajar(pool).slice(0, 6);
      rueda.innerHTML = "";
      var paso = 360 / seleccion.length;
      var tramos = seleccion.map(function (p, i) {
        return COLORES[i % COLORES.length] + " " + (i * paso) + "deg " + ((i + 1) * paso) + "deg";
      });
      rueda.style.background = "conic-gradient(" + tramos.join(",") + ")";

      var LADO = 25;   // % del diámetro que ocupa cada dibujo
      var RADIO = 37;  // % del diámetro a la que se colocan
      seleccion.forEach(function (palabra, i) {
        var centro = (i * paso + paso / 2 - 90) * Math.PI / 180;
        var caja = document.createElement("div");
        caja.className = "rueda-icono";
        caja.style.width = LADO + "%";
        caja.style.height = LADO + "%";
        caja.style.left = (50 + RADIO * Math.cos(centro) - LADO / 2) + "%";
        caja.style.top = (50 + RADIO * Math.sin(centro) - LADO / 2) + "%";

        var ruta = dibujoDe(palabra.en, palabra.img);
        if (ruta) {
          var img = document.createElement("img");
          img.src = ruta;
          img.alt = palabra.en;
          caja.appendChild(img);
        } else {
          caja.textContent = palabra.emoji || "❓";
        }
        rueda.appendChild(caja);
      });
      rueda.style.transform = "rotate(" + angulo + "deg)";
    }

    function decir() {
      if (actual && global.Audio && global.Audio.speak) { global.Audio.speak(actual.en); }
    }

    function girarRueda() {
      if (girando || hechos >= giros) { return; }
      girando = true;
      resultado.innerHTML = "";
      var vueltas = 3 + Math.floor(Math.random() * 3);
      var destino = Math.floor(Math.random() * seleccion.length);
      var paso = 360 / seleccion.length;
      var total = angulo + vueltas * 360 + (360 - destino * paso - paso / 2);
      rueda.style.transition = "transform " + (duracion / 1000) + "s cubic-bezier(.15,.75,.2,1)";
      rueda.style.transform = "rotate(" + total + "deg)";
      angulo = total;

      setTimeout(function () {
        girando = false;
        ronda++;
        actual = seleccion[destino];
        var ruta = dibujoDe(actual.en, actual.img);
        resultado.innerHTML = "";
        if (ruta) {
          var im = document.createElement("img");
          im.className = "rueda-elegido";
          im.src = ruta;
          im.alt = actual.en;
          resultado.appendChild(im);
        }
        var txt = document.createElement("div");
        txt.className = "rueda-palabra";
        txt.textContent = actual.en;
        resultado.appendChild(txt);
        decir();
        actualizar();
      }, duracion + 100);
    }

    girar.onclick = function () { girarRueda(); };
    repetir.onclick = function () { decir(); };

    panel.addEventListener("click", function () {
      // al tocar el resultado se marca como dicho
      if (!actual || girando || panel.classList.contains("esperando")) { return; }
      if (hechos >= giros) { return; }
      hechos++;
      actualizar();
      if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
      panel.classList.add("esperando");
      setTimeout(function () {
        panel.classList.remove("esperando");
        if (hechos >= giros) {
          panel.classList.add("terminado");
          if (alTerminar) { alTerminar({ giros: giros, hechos: hechos }); }
          return;
        }
        girarRueda();
      }, 900);
    });

    pintarRueda();
    actualizar();

    return {
      seleccion: function () { return seleccion.map(function (p) { return p.en; }); },
      actual: function () { return actual ? actual.en : null; },
      hechos: function () { return hechos; },
      girando: function () { return girando; },
      _girar: girarRueda
    };
  }

  global.Rueda = { montar: montar };
})(window);
