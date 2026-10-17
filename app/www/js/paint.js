/* ==========================================================================
   paint.js — Pizarra de dibujo para niños y almacén de dibujos.

   Interfaz estilo app infantil: marco de colores, paleta vertical a la
   izquierda (con pincel arcoíris), pinceles de tres grosores, goma y botones
   redondos de acción a la derecha.

   Se guarda en la carpeta interna de la app (Android, sin permisos) o en
   localStorage cuando se abre en el navegador.
   ========================================================================== */
(function (global) {
  "use strict";

  var COLORES = [
    "arcoiris", "#E53935", "#FB8C00", "#FDD835", "#AEEA00",
    "#43A047", "#26C6DA", "#4FC3F7", "#1E88E5", "#8E24AA"
  ];
  var GROSORES = [8, 18, 34];
  var CLAVE_WEB = "langkids.dibujos.v1";
  var MAXIMO_WEB = 40;

  /* ------------------------------------------------ almacén de dibujos */
  function puente() {
    return (global.Android && global.Android.saveDrawing) ? global.Android : null;
  }

  function leerWeb() {
    try { return JSON.parse(global.localStorage.getItem(CLAVE_WEB) || "[]"); }
    catch (e) { return []; }
  }

  function escribirWeb(lista) {
    try { global.localStorage.setItem(CLAVE_WEB, JSON.stringify(lista.slice(0, MAXIMO_WEB))); }
    catch (e) { /* sin espacio */ }
  }

  var Dibujos = {
    listar: function () {
      var b = puente();
      if (b) {
        try { return JSON.parse(b.listDrawings() || "[]"); } catch (e) { return []; }
      }
      return leerWeb().map(function (d) { return { id: d.id, ts: d.ts, bytes: (d.data || "").length }; });
    },

    cargar: function (id) {
      var b = puente();
      if (b) {
        try {
          var b64 = b.loadDrawing(id);
          return b64 ? "data:image/png;base64," + b64 : "";
        } catch (e) { return ""; }
      }
      var d = leerWeb().filter(function (x) { return x.id === id; })[0];
      return d ? d.data : "";
    },

    guardar: function (dataURL) {
      var id = "d" + Date.now();
      var b = puente();
      if (b) {
        try { if (b.saveDrawing(id, String(dataURL).split(",")[1] || "")) { return id; } }
        catch (e) { /* cae al almacén web */ }
      }
      var lista = leerWeb();
      lista.unshift({ id: id, ts: Date.now(), data: dataURL });
      escribirWeb(lista);
      return id;
    },

    borrar: function (id) {
      var b = puente();
      if (b) {
        try { if (b.deleteDrawing(id)) { return true; } } catch (e) { }
      }
      escribirWeb(leerWeb().filter(function (x) { return x.id !== id; }));
      return true;
    },

    exportar: function (id) {
      var b = puente();
      if (b && b.exportDrawing) {
        try { return b.exportDrawing(id) === true; } catch (e) { }
      }
      return false;
    },

    puedeExportar: function () {
      var b = puente();
      return !!(b && b.exportDrawing);
    }
  };

  /* ------------------------------------------------ pizarra de dibujo */
  function montar(cont, alGuardar, alCerrar, alGaleria) {
    var color = COLORES[1];
    var grosor = GROSORES[1];
    var borrando = false;
    var trazos = [];
    var actual = null;
    var sucio = false;
    var tinte = 0;

    cont.innerHTML = "";
    cont.className = "paint-app";

    /* --- cerrar (X roja) --- */
    var cerrar = document.createElement("button");
    cerrar.className = "paint-cerrar";
    cerrar.innerHTML = "✕";
    cerrar.setAttribute("aria-label", "cerrar");
    cerrar.onclick = function () {
      if (sucio && trazos.length && !global.confirm("Exit without saving the drawing?")) { return; }
      if (alCerrar) { alCerrar(); } else { location.hash = "#/inicio"; }
    };
    cont.appendChild(cerrar);

    /* --- columna izquierda: pinceles + paleta + goma --- */
    var izq = document.createElement("div");
    izq.className = "paint-izq";

    var pinceles = document.createElement("div");
    pinceles.className = "paint-pinceles";
    GROSORES.forEach(function (g, i) {
      var b = document.createElement("button");
      b.className = "paint-pincel" + (g === grosor ? " on" : "");
      b.setAttribute("aria-label", "grosor " + g);
      var trazo = document.createElement("i");
      trazo.style.setProperty("--g", (4 + i * 4) + "px");
      b.appendChild(trazo);
      b.onclick = function () {
        grosor = g;
        [].forEach.call(pinceles.children, function (x) { x.classList.remove("on"); });
        b.classList.add("on");
      };
      pinceles.appendChild(b);
    });
    izq.appendChild(pinceles);

    var paleta = document.createElement("div");
    paleta.className = "paint-paleta";
    COLORES.forEach(function (c) {
      var b = document.createElement("button");
      b.className = "paint-color" + (c === color ? " on" : "");
      b.setAttribute("aria-label", "color " + c);
      if (c === "arcoiris") {
        b.classList.add("arcoiris");
      } else {
        b.style.background = c;
      }
      b.onclick = function () {
        color = c;
        borrando = false;
        goma.classList.remove("on");
        [].forEach.call(paleta.children, function (x) { x.classList.remove("on"); });
        b.classList.add("on");
      };
      paleta.appendChild(b);
    });
    izq.appendChild(paleta);

    var goma = document.createElement("button");
    goma.className = "paint-goma";
    goma.setAttribute("aria-label", "goma");
    goma.onclick = function () {
      borrando = !borrando;
      goma.classList.toggle("on", borrando);
    };
    izq.appendChild(goma);

    cont.appendChild(izq);

    /* --- lienzo --- */
    var marco = document.createElement("div");
    marco.className = "paint-marco";
    var lienzo = document.createElement("canvas");
    lienzo.className = "paint-lienzo";
    marco.appendChild(lienzo);
    cont.appendChild(marco);

    var ctx = lienzo.getContext("2d");

    /* --- columna derecha: acciones --- */
    var der = document.createElement("div");
    der.className = "paint-der";

    function accion(emoji, etiqueta, clase, alPulsar) {
      var b = document.createElement("button");
      b.className = "paint-accion " + clase;
      b.setAttribute("aria-label", etiqueta);
      b.textContent = emoji;
      b.onclick = alPulsar;
      der.appendChild(b);
      return b;
    }

    if (alGaleria) {
      accion("🖼️", "my drawings", "galeria", function () { alGaleria(); });
    }

    accion("🌈", "pintar el fondo", "fondo", function () {
      var c = color === "arcoiris" ? "#FFF3C4" : color;
      ctx.fillStyle = c;
      ctx.fillRect(0, 0, lienzo.width, lienzo.height);
      trazos.push({ fondo: c });
      sucio = true;
    });

    accion("↩", "deshacer", "deshacer", function () {
      if (!trazos.length) { return; }
      trazos.pop();
      pintar();
      sucio = true;
    });

    accion("🗑", "borrar todo", "borrar", function () {
      if (!trazos.length) { return; }
      if (!global.confirm("Clear the whole drawing?")) { return; }
      trazos = [];
      pintar();
      sucio = true;
    });

    accion("📷", "save the drawing", "guardar paint-guardar", function () {
      if (!trazos.length) {
        if (global.AppToast) { global.AppToast("Draw something first 🙂"); }
        return;
      }
      var id = Dibujos.guardar(lienzo.toDataURL("image/png"));
      sucio = false;
      if (alGuardar) { alGuardar(id); }
    });

    cont.appendChild(der);

    /* --- motor de dibujo --- */
    function ajustar() {
      var caja = marco.getBoundingClientRect();
      if (caja.width < 10 || caja.height < 10) { return; }
      var dpr = global.devicePixelRatio || 1;
      var ancho = Math.floor(caja.width * dpr);
      var alto = Math.floor(caja.height * dpr);
      if (lienzo.width === ancho && lienzo.height === alto) { return; }
      lienzo.width = ancho;
      lienzo.height = alto;
      pintar();
    }

    function punto(ev) {
      var caja = marco.getBoundingClientRect();
      var dpr = global.devicePixelRatio || 1;
      return { x: (ev.clientX - caja.left) * dpr, y: (ev.clientY - caja.top) * dpr };
    }

    function pintar() {
      var dpr = global.devicePixelRatio || 1;
      ctx.clearRect(0, 0, lienzo.width, lienzo.height);
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      trazos.forEach(function (t) {
        if (t.fondo) {
          ctx.fillStyle = t.fondo;
          ctx.fillRect(0, 0, lienzo.width, lienzo.height);
          return;
        }
        ctx.lineWidth = t.grosor * dpr;
        if (t.color === "borrar") {
          ctx.strokeStyle = "#FFFFFF";
        }
        if (t.arcoiris) {
          for (var i = 1; i < t.puntos.length; i++) {
            ctx.beginPath();
            ctx.strokeStyle = "hsl(" + ((t.base + i * 6) % 360) + ",85%,55%)";
            ctx.moveTo(t.puntos[i - 1].x, t.puntos[i - 1].y);
            ctx.lineTo(t.puntos[i].x, t.puntos[i].y);
            ctx.stroke();
          }
          return;
        }
        if (t.color !== "borrar") { ctx.strokeStyle = t.color; }
        if (t.puntos.length === 1) {
          var p = t.puntos[0];
          ctx.beginPath();
          ctx.arc(p.x, p.y, ctx.lineWidth / 2, 0, Math.PI * 2);
          ctx.fillStyle = ctx.strokeStyle;
          ctx.fill();
          return;
        }
        ctx.beginPath();
        ctx.moveTo(t.puntos[0].x, t.puntos[0].y);
        for (var j = 1; j < t.puntos.length; j++) { ctx.lineTo(t.puntos[j].x, t.puntos[j].y); }
        ctx.stroke();
      });
    }

    lienzo.addEventListener("pointerdown", function (ev) {
      ev.preventDefault();
      if (lienzo.setPointerCapture) {
        try { lienzo.setPointerCapture(ev.pointerId); } catch (e) { }
      }
      actual = {
        color: borrando ? "borrar" : color,
        grosor: borrando ? grosor * 1.8 : grosor,
        arcoiris: !borrando && color === "arcoiris",
        base: tinte,
        puntos: [punto(ev)]
      };
      trazos.push(actual);
      sucio = true;
      pintar();
    });

    lienzo.addEventListener("pointermove", function (ev) {
      if (!actual) { return; }
      ev.preventDefault();
      actual.puntos.push(punto(ev));
      pintar();
    });

    function soltar() { actual = null; }
    lienzo.addEventListener("pointerup", soltar);
    lienzo.addEventListener("pointercancel", soltar);
    lienzo.addEventListener("pointerleave", soltar);

    ajustar();
    global.addEventListener("resize", ajustar);
    setTimeout(ajustar, 60);

    return {
      ajustar: ajustar,
      hayDibujo: function () { return trazos.length > 0; },
      hayCambios: function () { return sucio; },
      datos: function () { return lienzo.toDataURL("image/png"); }
    };
  }

  global.Dibujos = Dibujos;
  global.Paint = { montar: montar, colores: COLORES };
})(window);
