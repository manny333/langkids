/* =========================================================================
   activities.js — motores de juego de LangKids.
   Seis actividades: tarjetas con voz, escucha y toca, parejas, ordena la
   frase, ¿cuántos son? y cuestionario de unidad.
   ========================================================================= */
(function (global) {
  "use strict";

  /* ------------------------------------------------------------- utilidades */
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) { e.className = cls; }
    if (html !== undefined && html !== null) { e.innerHTML = html; }
    return e;
  }

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function cap(arr, max) {
    if (arr.length <= max) { return arr.slice(); }
    var out = [], paso = arr.length / max;
    for (var i = 0; i < max; i++) { out.push(arr[Math.floor(i * paso)]); }
    return out;
  }

  function unicas(palabras) {
    var vistas = {}, out = [];
    palabras.forEach(function (w) {
      var k = (w && w.en ? w.en : "").toLowerCase();
      if (k && !vistas[k]) { vistas[k] = 1; out.push(w); }
    });
    return out;
  }

  /** Deja una sola palabra por dibujo: dos imagenes iguales hacen trampa. */
  function dibujosUnicos(palabras) {
    var vistos = {}, out = [];
    palabras.forEach(function (w) {
      var e = w.emoji || "";
      if (e && !vistos[e]) { vistos[e] = 1; out.push(w); }
    });
    return out;
  }

  function normalizar(s) {
    return String(s).toLowerCase().replace(/[.,!?;:¡¿"«»]/g, "").replace(/\s+/g, " ").trim();
  }

  function hablar(txt) { if (global.Audio && global.Audio.speak) { global.Audio.speak(txt); } }

  /**
   * Devuelve el dibujo de una palabra: foto si existe, emoji si no.
   * Se usa en tarjetas, fichas y cuestionarios.
   */
  function figura(w, clase) {
    if (w && w.img) {
      var caja = el("div", clase, "");
      var img = document.createElement("img");
      img.alt = w.en || "";
      img.src = global.Store ? global.Store.rutaImagen(w.img) : w.img;
      if (img.src.indexOf("img-v2") !== -1) {
        img.onerror = function () { img.src = w.img; };   // si falta, vuelve a la clasica
      }
      caja.appendChild(img);
      return caja;
    }
    return el("div", clase, (w && w.emoji) || "");
  }

  function botonVoz(txt, etiqueta) {
    var b = el("button", "big-btn ghost", "🔊 " + (etiqueta || "Listen"));
    b.setAttribute("aria-label", "Listen to " + txt);
    b.onclick = function (ev) {
      ev.stopPropagation();
      if (global.Audio && global.Audio.desbloquear) { global.Audio.desbloquear(); }
      hablar(txt);
    };
    return b;
  }

  function cabecera(cont, n, total, titulo) {
    var h = el("div", "act-head");
    h.appendChild(el("span", "step", "Activity " + n + " of " + total));
    cont.appendChild(h);
    cont.appendChild(el("div", "act-title", titulo));
  }

  function progreso(cont, hechos, total) {
    var b = el("div", "bar");
    var i = el("i");
    i.style.width = Math.round((hechos / total) * 100) + "%";
    b.appendChild(i);
    cont.appendChild(b);
    cont.appendChild(el("div", null, "<div style='height:10px'></div>"));
  }

  /* =========================================================================
     1) TARJETAS CON VOZ
     ========================================================================= */
  function tarjetas(ctx, cont, onDone) {
    var palabras = cap(unicas(ctx.lesson.words.length ? ctx.lesson.words : ctx.unit.words), 12);
    var i = 0;

    function pintar() {
      cont.innerHTML = "";
      cabecera(cont, ctx.num, ctx.total, "Word cards");
      progreso(cont, i, palabras.length);

      var w = palabras[i];
      var card = el("div", "flash-card pop");
      card.appendChild(figura(w, "big-emoji"));
      card.appendChild(el("div", "word", w.en));
      var sonido = botonVoz(w.en, "Listen");
      sonido.className = "big-btn";
      card.appendChild(sonido);
      cont.appendChild(card);

      var nav = el("div", "row");
      var prev = el("button", "big-btn ghost", "◀ Back");
      prev.disabled = (i === 0);
      prev.onclick = function () { if (i > 0) { i--; pintar(); } };
      var next = el("button", "big-btn", (i === palabras.length - 1) ? "Done! ✓" : "Next ▶");
      next.onclick = function () {
        if (global.Audio && global.Audio.clic) { global.Audio.clic(); }
        if (i === palabras.length - 1) { onDone(); } else { i++; pintar(); }
      };
      nav.appendChild(prev); nav.appendChild(next);
      cont.appendChild(nav);

      hablar(w.en);
    }
    pintar();
  }

  /* =========================================================================
     2) ESCUCHA Y TOCA  (también alimenta el cuestionario)
     ========================================================================= */
  function rondaEscucha(cont, objetivo, opciones, alResponder) {
    var zona = el("div");
    var rep = botonVoz(objetivo.en, "Repetir");
    rep.onclick = function () { hablar(objetivo.en); };
    zona.appendChild(rep);
    zona.appendChild(el("div", null, "<div style='height:12px'></div>"));

    var grid = el("div", "grid2");
    var resuelto = false;

    opciones.forEach(function (op) {
      var t = el("div", "tile");
      t.appendChild(figura(op, "t-emoji"));
      t.appendChild(el("div", "t-word", op.en));
      t.onclick = function () {
        if (resuelto) { return; }
        if (normalizar(op.en) === normalizar(objetivo.en)) {
          resuelto = true;
          t.className = "tile ok pop";
          if (global.Audio && global.Audio.ding) { global.Audio.ding(); global.Audio.vibrate(25); }
          hablar(objetivo.en);
          setTimeout(alResponder, 850);
        } else {
          t.className = "tile bad";
          if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); global.Audio.vibrate(60); }
          setTimeout(function () { t.className = "tile"; }, 500);
          alResponder(false);
        }
      };
      grid.appendChild(t);
    });
    zona.appendChild(grid);
    cont.appendChild(zona);
    setTimeout(function () { hablar(objetivo.en); }, 350);
  }

  function escucha(ctx, cont, onDone) {
    var pool = unicas(ctx.unit.words);
    var objetivos = cap(dibujosUnicos(unicas(ctx.lesson.words.length ? ctx.lesson.words : pool)), 6);
    var i = 0, fallos = 0;

    function pintar() {
      cont.innerHTML = "";
      cabecera(cont, ctx.num, ctx.total, "Listen and tap 👂");
      progreso(cont, i, objetivos.length);
      var objetivo = objetivos[i];
      var otros = shuffle(pool.filter(function (w) {
        return normalizar(w.en) !== normalizar(objetivo.en) && w.emoji !== objetivo.emoji;
      })).slice(0, 3);
      var opciones = shuffle(otros.concat([objetivo]));

      rondaEscucha(cont, objetivo, opciones, function (acerto) {
        if (acerto === false) { fallos++; return; }
        ctx.responder(fallos === 0);
        fallos = 0;
        i++;
        if (i >= objetivos.length) { onDone(); } else { pintar(); }
      });
    }
    pintar();
  }

  /* =========================================================================
     3) PAREJAS (memoria)
     ========================================================================= */
  function parejas(ctx, cont, onDone) {
    var palabras = cap(dibujosUnicos(unicas(ctx.lesson.words.length ? ctx.lesson.words : ctx.unit.words)), 6);
    var cartas = [];
    palabras.forEach(function (w, idx) {
      cartas.push({ id: idx, tipo: "emoji", texto: w.emoji, img: w.img, palabra: w.en });
      cartas.push({ id: idx, tipo: "word", texto: w.en, palabra: w.en });
    });
    cartas = shuffle(cartas);

    var abiertas = [], bloqueado = false, encontradas = 0, fallos = 0;

    cont.innerHTML = "";
    cabecera(cont, ctx.num, ctx.total, "Pairs 🃏");

    var barra = el("div", "pares-barra");
    var marcador = el("span", "pares-marcador", "0 / " + palabras.length + " pairs");
    barra.appendChild(marcador);
    cont.appendChild(barra);

    var grid = el("div", "pares-grid");
    // columnas segun cuantas cartas haya: siempre dos filas si caben
    var filas = cartas.length <= 10 ? 2 : 3;
    var columnas = Math.ceil(cartas.length / filas);
    grid.style.gridTemplateColumns = "repeat(" + columnas + ", minmax(0, 1fr))";
    grid.style.gridTemplateRows = "repeat(" + filas + ", minmax(0, 1fr))";
    cont.appendChild(grid);

    function refrescarMarcador() {
      marcador.textContent = encontradas + " / " + palabras.length + " pairs";
    }

    cartas.forEach(function (c, pos) {
      var t = el("div", "tile flip");
      t.innerHTML = "<div class='t-dorso'><span>?</span></div>";
      t.onclick = function () {
        if (bloqueado || abiertas.indexOf(pos) !== -1 || t.classList.contains("ok")) { return; }
        t.className = "tile pop" + (c.tipo === "emoji" ? "" : "");
        t.innerHTML = (c.tipo === "emoji")
          ? (c.img ? "<div class='t-emoji'><img src='" + (global.Store ? global.Store.rutaImagen(c.img) : c.img) + "' alt='" + c.palabra + "'></div>" : "<div class='t-emoji'>" + c.texto + "</div>")
          : "<div class='t-word'>" + c.texto + "</div>";
        if (c.tipo === "word") { hablar(c.palabra); }
        abiertas.push(pos);

        if (abiertas.length === 2) {
          var a = cartas[abiertas[0]], b = cartas[abiertas[1]];
          var nodos = grid.children;
          if (a.id === b.id) {
            nodos[abiertas[0]].className = "tile ok";
            nodos[abiertas[1]].className = "tile ok";
            if (global.Audio && global.Audio.ding) { global.Audio.ding(); global.Audio.vibrate(25); }
            encontradas++;
            refrescarMarcador();
            abiertas = [];
            if (encontradas === palabras.length) {
              ctx.responder(fallos === 0);
              setTimeout(onDone, 700);
            }
          } else {
            fallos++;
            bloqueado = true;
            var p1 = abiertas[0], p2 = abiertas[1];
            nodos[p1].className = "tile bad"; nodos[p2].className = "tile bad";
            if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
            setTimeout(function () {
              [p1, p2].forEach(function (p) {
                nodos[p].className = "tile flip";
                nodos[p].innerHTML = "<div class='t-dorso'><span>?</span></div>";
              });
              abiertas = []; bloqueado = false;
            }, 850);
          }
        }
      };
      grid.appendChild(t);
    });
  }

  /* =========================================================================
     4) ORDENA LA FRASE
     ========================================================================= */
  function frase(ctx, cont, onDone) {
    var oracion = ctx.lesson.sentence || (ctx.unit.structures[0] && ctx.unit.structures[0].en) || "";
    var tokens = String(oracion).split(/\s+/).filter(function (t) { return t; });
    var mezclados = shuffle(tokens);
    var colocados = [];
    var fallos = 0;

    cont.innerHTML = "";
    cabecera(cont, ctx.num, ctx.total, "Build the sentence 🧩");
    cont.appendChild(el("p", "muted", "Tap the words in order to build the sentence."));
    cont.appendChild(botonVoz(oracion, "Listen to the sentence"));
    cont.appendChild(el("div", null, "<div style='height:12px'></div>"));

    var zona = el("div", "sentence-zone");
    cont.appendChild(zona);
    var fuente = el("div", "word-pool");
    cont.appendChild(fuente);

    function pintar() {
      zona.innerHTML = "";
      if (!colocados.length) {
        zona.appendChild(el("span", "muted", "Tap the words below…"));
      }
      colocados.forEach(function (t, idx) {
        var c = el("button", "chip placed", t);
        c.onclick = function () {
          colocados.splice(idx, 1);
          pintar();
        };
        zona.appendChild(c);
      });
      fuente.innerHTML = "";
      mezclados.forEach(function (t, idx) {
        var usado = colocados.indexOf(t) !== -1 && contar(t) <= contarEn(colocados, t);
        var c = el("button", "chip" + (usado ? " used" : ""), t);
        c.onclick = function () {
          if (c.classList.contains("used")) { return; }
          if (global.Audio && global.Audio.clic) { global.Audio.clic(); }
          colocados.push(t);
          pintar();
          if (colocados.length === tokens.length) { comprobar(); }
        };
        fuente.appendChild(c);
      });
    }

    function contar(t) { return tokens.filter(function (x) { return x === t; }).length; }
    function contarEn(arr, t) { return arr.filter(function (x) { return x === t; }).length; }

    function comprobar() {
      if (normalizar(colocados.join(" ")) === normalizar(tokens.join(" "))) {
        if (global.Audio && global.Audio.tada) { global.Audio.tada(); global.Audio.vibrate(40); }
        hablar(tokens.join(" "));
        zona.className = "sentence-zone pop";
        ctx.responder(fallos === 0);
        setTimeout(onDone, 1200);
      } else {
        fallos++;
        if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); global.Audio.vibrate(60); }
        zona.className = "sentence-zone";
        setTimeout(function () {
          hablar(tokens.join(" "));
          colocados = [];
          pintar();
        }, 500);
      }
    }

    pintar();
  }

  /* =========================================================================
     5) ¿CUÁNTOS SON?
     ========================================================================= */
  var NUMEROS = {
    one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8,
    nine: 9, ten: 10
  };

  function numerosDe(unit) {
    return unicas(unit.words).filter(function (w) {
      return NUMEROS[normalizar(w.en)] !== undefined;
    });
  }

  function cuantos(ctx, cont, onDone) {
    var nums = numerosDe(ctx.unit);
    var pool = unicas(ctx.unit.words).filter(function (w) { return NUMEROS[normalizar(w.en)] === undefined; });
    if (nums.length < 3 || !pool.length) { onDone(); return; }

    var rondas = 4, i = 0, fallos = 0;

    function pintar() {
      cont.innerHTML = "";
      cabecera(cont, ctx.num, ctx.total, "How many? 🔢");
      progreso(cont, i, rondas);

      var objetivo = nums[Math.floor(Math.random() * nums.length)];
      var n = NUMEROS[normalizar(objetivo.en)];
      n = Math.min(n, 10);
      // el dibujo que se repite para contar (concreto y fácil de contar)
      var DIBUJOS = ["⭐", "🍎", "🐟", "🎈", "⚽"];
      var dibujo = DIBUJOS[Math.floor(Math.random() * DIBUJOS.length)];

      var card = el("div", "flash-card");
      var fila = el("div", null, "");
      fila.style.fontSize = "34px";
      fila.style.lineHeight = "1.35";
      var texto = "";
      for (var k = 0; k < n; k++) { texto += dibujo; }
      fila.innerHTML = texto;
      card.appendChild(fila);
      cont.appendChild(card);

      cont.appendChild(el("div", "act-title", "How many?"));

      var opciones = shuffle(nums).slice(0, 3);
      var contiene = opciones.some(function (o) { return o.en === objetivo.en; });
      if (!contiene) { opciones[0] = objetivo; }
      opciones = shuffle(opciones);

      var grid = el("div", "grid3");
      opciones.forEach(function (op) {
        var t = el("div", "tile");
        t.appendChild(figura(op, "t-emoji"));
        t.appendChild(el("div", "t-word", op.en));
        t.onclick = function () {
          if (op.en === objetivo.en) {
            t.className = "tile ok pop";
            if (global.Audio && global.Audio.ding) { global.Audio.ding(); global.Audio.vibrate(25); }
            hablar(objetivo.en);
            ctx.responder(fallos === 0);
            fallos = 0;
            i++;
            setTimeout(function () { if (i >= rondas) { onDone(); } else { pintar(); } }, 800);
          } else {
            fallos++;
            t.className = "tile bad";
            if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
            setTimeout(function () { t.className = "tile"; }, 500);
          }
        };
        grid.appendChild(t);
      });
      cont.appendChild(grid);
      setTimeout(function () { hablar("How many?"); }, 300);
    }
    pintar();
  }

  /* =========================================================================
     6) CUESTIONARIO DE UNIDAD
     ========================================================================= */
  function cuestionario(ctx, cont, onDone) {
    var pool = unicas(ctx.unit.words);
    var objetivos = cap(shuffle(pool), Math.min(8, pool.length));
    var i = 0, fallos = 0;

    function pintar() {
      cont.innerHTML = "";
      cabecera(cont, ctx.num, ctx.total, "Unit quiz 🏁");
      progreso(cont, i, objetivos.length);

      var objetivo = objetivos[i];
      var tipo = (i % 3 === 2) ? "palabra" : "escucha";

      if (tipo === "escucha") {
        var otros = shuffle(pool.filter(function (w) {
          return w.en !== objetivo.en && w.emoji !== objetivo.emoji;
        })).slice(0, 3);
        rondaEscucha(cont, objetivo, shuffle(otros.concat([objetivo])), function (acerto) {
          if (acerto === false) { fallos++; return; }
          ctx.responder(fallos === 0);
          fallos = 0;
          i++;
          if (i >= objetivos.length) { onDone(); } else { pintar(); }
        });
      } else {
        var card = el("div", "flash-card");
        card.appendChild(figura(objetivo, "big-emoji"));
        cont.appendChild(card);
        cont.appendChild(el("div", "act-title", "What is it in English?"));
        var grid = el("div", "grid2");
        var distractores = shuffle(pool.filter(function (w) {
          return w.en !== objetivo.en && w.emoji !== objetivo.emoji;
        })).slice(0, 3);
        shuffle(distractores.concat([objetivo])).forEach(function (op) {
          var t = el("div", "tile");
          t.appendChild(el("div", "t-word", op.en));
          t.onclick = function () {
            if (op.en === objetivo.en) {
              t.className = "tile ok pop";
              if (global.Audio && global.Audio.ding) { global.Audio.ding(); global.Audio.vibrate(25); }
              hablar(objetivo.en);
              ctx.responder(fallos === 0);
              fallos = 0;
              i++;
              setTimeout(function () { if (i >= objetivos.length) { onDone(); } else { pintar(); } }, 800);
            } else {
              fallos++;
              t.className = "tile bad";
              if (global.Audio && global.Audio.buzz) { global.Audio.buzz(); }
              setTimeout(function () { t.className = "tile"; }, 500);
            }
          };
          grid.appendChild(t);
        });
        cont.appendChild(grid);
      }
    }
    pintar();
  }

  /* =========================================================================
     registro
     ========================================================================= */
  var MOTORES = {
    flashcards: tarjetas,
    listen: escucha,
    pairs: parejas,
    sentence: frase,
    count: cuantos,
    quiz: cuestionario
  };

  var TITULOS = {
    flashcards: "Word cards",
    listen: "Escucha y toca",
    pairs: "Parejas",
    sentence: "Ordena la frase",
    count: "How many?",
    quiz: "Cuestionario"
  };

  global.Activities = {
    start: function (tarea, ctx, contenedor, alTerminar) {
      var motor = MOTORES[tarea] || tarjetas;
      motor(ctx, contenedor, alTerminar);
    },
    titulo: function (t) { return TITULOS[t] || t; },
    existe: function (t) { return !!MOTORES[t]; }
  };
})(window);
