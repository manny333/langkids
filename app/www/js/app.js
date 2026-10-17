/* =========================================================================
   app.js — pantallas, navegación y flujo de las lecciones.
   ========================================================================= */
(function (global) {
  "use strict";

  var screen = document.getElementById("screen");
  var toastEl = document.getElementById("toast");
  var caja = document.getElementById("celebrate");
  var confirmEl = document.getElementById("confirm");
  var VERSION = "1.0";

  /* ------------------------------------------------------------- UI helpers */
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) { e.className = cls; }
    if (html !== undefined) { e.innerHTML = html; }
    return e;
  }

  var toastTimer = null;
  function toast(msg, ms) {
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    if (toastTimer) { clearTimeout(toastTimer); }
    toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, ms || 2200);
  }

  var celebrando = null;
  var pedidoNombre = false;

  /* confeti: se lanza al terminar una clase o ganar una insignia */
  var COLORES = ["#FFC93C", "#FF6B6B", "#22C7C7", "#8B5CF6", "#58CC02", "#FF8FB1"];
  function confeti() {
    var caja = document.getElementById("confetti");
    if (!caja) {
      caja = el("div");
      caja.id = "confetti";
      document.body.appendChild(caja);
    }
    caja.innerHTML = "";
    for (var i = 0; i < 44; i++) {
      var p = document.createElement("i");
      p.style.left = (Math.random() * 100) + "%";
      p.style.background = COLORES[i % COLORES.length];
      p.style.animationDuration = (1.5 + Math.random() * 1.5) + "s";
      p.style.animationDelay = (Math.random() * 0.6) + "s";
      p.style.opacity = "0.95";
      caja.appendChild(p);
    }
    setTimeout(function () { caja.innerHTML = ""; }, 3400);
  }

  function celebrar(cfg) {
    document.getElementById("celebrate-emoji").textContent = cfg.emoji || "🎉";
    var titulo = cfg.titulo || "Great job!";
    var quien = Store.nombre();
    if (quien && cfg.conNombre !== false) {
      // "Bingo! Congratulations!" -> "Bingo! Congratulations, Emma!"
      titulo = /\.$/.test(titulo)
        ? titulo.replace(/\.$/, ", " + quien + ".")
        : titulo + ", " + quien;
    }
    document.getElementById("celebrate-title").textContent = titulo;
    document.getElementById("celebrate-text").textContent = cfg.texto || "";
    var cont = document.getElementById("celebrate-stars");
    cont.innerHTML = "";
    if (cfg.estrellas) {
      for (var i = 1; i <= 3; i++) {
        var s = el("span", i <= cfg.estrellas ? "" : "off", "⭐");
        cont.appendChild(s);
      }
    }
    caja.classList.remove("hidden");
    if (global.Audio && global.Audio.tada) { global.Audio.tada(); }
    if (cfg.estrellas && cfg.estrellas >= 2) { confeti(); }
    celebrando = cfg.alCerrar || null;
  }

  document.getElementById("celebrate-btn").onclick = function () {
    caja.classList.add("hidden");
    var f = celebrando; celebrando = null;
    if (f) { f(); } else { location.hash = "#/"; }
  };

  function preguntar(titulo, texto, alSi) {
    document.getElementById("confirm-title").textContent = titulo;
    document.getElementById("confirm-text").textContent = texto;
    confirmEl.classList.remove("hidden");
    document.getElementById("confirm-yes").onclick = function () {
      confirmEl.classList.add("hidden");
      alSi();
    };
    document.getElementById("confirm-no").onclick = function () {
      confirmEl.classList.add("hidden");
    };
  }

  global.UI = { toast: toast, celebrar: celebrar, preguntar: preguntar };

  /* ------------------------------------------------------------- piezas comunes */
  function estrellas(n) {
    var d = el("div", "stars-row");
    for (var i = 1; i <= 3; i++) {
      d.appendChild(el("span", i <= n ? "" : "off", "⭐"));
    }
    return d;
  }

  function barra(valor, total) {
    var b = el("div", "bar");
    var i = el("i");
    i.style.width = (total ? Math.round((valor / total) * 100) : 0) + "%";
    b.appendChild(i);
    return b;
  }

  function heroe(mensaje) {
    var h = el("div", "hero");
    h.appendChild(el("div", "milo", "🐵"));
    h.appendChild(el("div", "msg", mensaje));
    return h;
  }

  function tituloH1(txt) { return el("h1", null, txt); }

  /* ------------------------------------------------------------- inicio */
  /** Aplica el tamaño de texto elegido en Ajustes. */
  function aplicarTexto() {
    var grande = Store.settings().texto === "g";
    document.body.classList.toggle("texto-grande", grande);
  }

  function pintarInicio() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-inicio");

    var panel = el("div", "lanzador");

    function opcion(id, emoji, titulo, sub, destino, tono) {
      var b = el("button", "lanzador-opcion " + tono);
      var arte = (global.LANGKIDS_INICIO || {})[id];
      if (arte) {
        var pic = document.createElement("img");
        pic.className = "lanzador-img";
        pic.src = arte;
        pic.alt = titulo;
        b.appendChild(pic);
      } else {
        b.appendChild(el("div", "lanzador-emoji", emoji));
      }
      b.appendChild(el("div", "lanzador-titulo", titulo));
      if (sub) { b.appendChild(el("div", "lanzador-sub", sub)); }
      b.onclick = function () { location.hash = destino; };
      panel.appendChild(b);
      return b;
    }

    var sig = Store.nextLesson();
    opcion("clases", "📚", "English Classes", sig ? (sig.unit.title + " · Class " + sig.clase.n) : "All levels", "#/clases", "tono-clases");
    opcion("pintar", "🎨", "Paint", "Draw and save", "#/pintar", "tono-pintar");
        opcion("juegos", "🎮", "Games", "Memory · Bingo · I Spy", "#/juegos", "tono-juegos");
opcion("progreso", "📊", "My Progress", Store.totalStars() + " ⭐ of " + Store.maxStars(), "#/progreso", "tono-progreso");

    screen.appendChild(panel);
  }

  function pintarClases() {
    screen.innerHTML = "";
    var total = Store.totalStars();
    var nombreNivel = "";
    var sig = Store.nextLesson();
    if (sig) { nombreNivel = sig.level.name; }
    screen.appendChild(heroe(nombreNivel
      ? "Hello! Let's learn English. Next: <b>" + sig.unit.title + "</b>."
      : "Amazing! You finished the whole course. You can replay any class. 🏆"));

    if (sig) {
      var btn = el("button", "big-btn orange",
        "▶ Continue: " + sig.unit.title + " · Class " + sig.clase.n);
      btn.onclick = function () { location.hash = "#/clase/" + sig.key; };
      screen.appendChild(btn);
      screen.appendChild(el("div", null, "<div style='height:14px'></div>"));
    }

    screen.appendChild(el("h2", null, "Levels"));
    var listaNiveles = el("div", "lista niveles-grid");
    Store.levels().forEach(function (lv) {
      var p = Store.levelProgress(lv.id);
      var c = el("div", "card tap tone-" + ((lv.id - 1) % 4 + 1) + (p.done === p.total ? " done" : ""));
      var portadas = global.LANGKIDS_NIVELES || {};
      if (portadas[lv.id]) {
        var pic = document.createElement("img");
        pic.className = "card-portada";
        pic.src = portadas[lv.id];
        pic.alt = "Level " + lv.id;
        c.appendChild(pic);
      } else {
        c.appendChild(el("div", "emoji", lv.emoji || "📘"));
      }
      var g = el("div", "grow");
      g.appendChild(el("div", "title", "Level " + lv.id + " · " + lv.name));
      g.appendChild(el("div", "sub", String(lv.age || "").replace("años", "years").replace("ano", "year") + " · " + String(lv.cefr || "").replace(" inicial", " starter") + " · " + p.done + "/" + p.total + " classes"));
      g.appendChild(barra(p.done, p.total));
      c.appendChild(g);
      var st = el("div", "center");
      st.appendChild(el("div", null, "<b>" + p.stars + "</b>⭐"));
      if (Store.hasBadge(lv.id)) { st.appendChild(el("div", null, lv.badgeEmoji || "🏅")); }
      c.appendChild(st);
      c.onclick = function () { location.hash = "#/nivel/" + lv.id; };
      listaNiveles.appendChild(c);
    });
    screen.appendChild(listaNiveles);

    screen.appendChild(el("p", "muted",
      "<b>" + total + "</b> ⭐ of " + Store.maxStars() + " · <b>" + Store.doneCount() +
      "</b> of 80 classes"));
  }

  /* ------------------------------------------------------------- nivel */
  function pintarNivel(id) {
    var lv = Store.level(id);
    screen.innerHTML = "";
    if (!lv) { location.hash = "#/"; return; }
    screen.appendChild(tituloH1(lv.emoji + " Level " + lv.id + " · " + lv.name));
    screen.appendChild(el("p", "muted", String(lv.age || "").replace("años", "years").replace("ano", "year") + " · " + String(lv.cefr || "").replace(" inicial", " starter") + " · " + String(lv.duration || "").replace("min por clase", "min per class").replace("clases por semana", "classes a week")));
    if (lv.goal) { screen.appendChild(el("p", null, lv.goal)); }

    var p = Store.levelProgress(lv.id);
    screen.appendChild(barra(p.done, p.total));
    screen.appendChild(el("p", "muted", p.done + " of " + p.total + " classes · " + p.stars + " ⭐"));

    var uw = el("button", "big-btn ghost", "◀ Back to levels");
    uw.onclick = function () { location.hash = "#/"; };
    screen.appendChild(uw);
    screen.appendChild(el("div", null, "<div style='height:12px'></div>"));

    screen.appendChild(el("h2", null, "Units"));
    var listaUnidades = el("div", "lista");
    lv.units.forEach(function (u, idx) {
      var up = Store.unitProgress(u.id);
      var bloqueada = idx > 0 && Store.unitProgress(lv.units[idx - 1].id).done === 0 &&
                      up.done === 0 && !Store.isDone(lv.units[idx - 1].classes[4].key);
      var c = el("div", "card tap tone-" + (idx % 4 + 1) + (up.done === up.total ? " done" : (bloqueada ? " locked" : " abierta")));
      c.appendChild(el("div", "emoji", u.emoji));
      var g = el("div", "grow");
      g.appendChild(el("div", "title", u.id + " · " + u.title));
      g.appendChild(el("div", "sub", up.done + "/" + up.total + " classes · " + u.words.length + " words"));
      g.appendChild(barra(up.done, up.total));
      c.appendChild(g);
      c.onclick = function () { location.hash = "#/unidad/" + u.id; };
      listaUnidades.appendChild(c);
    });
    screen.appendChild(listaUnidades);

    var b = el("div", "card center");
    b.appendChild(el("div", "badge-big", lv.badgeEmoji || "🏅"));
    b.appendChild(el("div", null, "<b>" + lv.badge + "</b>"));
    b.appendChild(el("p", "muted", Store.hasBadge(lv.id)
      ? "Badge earned!" : "Finish the 20 classes of this level to earn it."));
    screen.appendChild(b);
  }

  /* ------------------------------------------------------------- unidad */
  function pintarUnidad(uid) {
    var u = Store.unit(uid), lv = Store.levelOfUnit(uid);
    screen.innerHTML = "";
    if (!u) { location.hash = "#/"; return; }

    screen.appendChild(tituloH1(u.emoji + " " + u.id + " · " + u.title));
    screen.appendChild(el("p", null, "<b>Goal:</b> " + u.objective));
    var up = Store.unitProgress(uid);
    screen.appendChild(barra(up.done, up.total));

    var volver = el("button", "big-btn ghost", "◀ Level " + lv.id + ": " + lv.name);
    volver.onclick = function () { location.hash = "#/nivel/" + lv.id; };
    screen.appendChild(volver);
    screen.appendChild(el("div", null, "<div style='height:14px'></div>"));

    var cuento = cuentosDeUnidad(uid);
    if (cuento) {
      var bCuento = el("button", "big-btn cuento-acceso", "📖 Read the story: " + cuento.titulo);
      bCuento.onclick = function () { location.hash = "#/cuento/" + uid; };
      screen.appendChild(bCuento);
      screen.appendChild(el("div", null, "<div style='height:10px'></div>"));
    }

    screen.appendChild(el("h2", null, "Classes"));
    var listaClases = el("div", "lista");
    u.classes.forEach(function (c) {
      var abierta = Store.isUnlocked(c.key);
      var hecha = Store.isDone(c.key);
      var card = el("div", "card tap" + (hecha ? " done" : (abierta ? " current" : " locked")));
      card.appendChild(el("div", "emoji", hecha ? "✅" : (abierta ? "▶️" : "🔒")));
      var g = el("div", "grow");
      g.appendChild(el("div", "title", "Class " + c.n + " · " + c.focus));
      g.appendChild(el("div", "sub", c.words.length + " words · " + c.tasks.length + " activities"));
      card.appendChild(g);
      card.appendChild(estrellas(Store.starsOf(c.key)));
      card.onclick = function () {
        if (!abierta) { toast("Termina la clase anterior para abrir esta 🔒"); return; }
        location.hash = "#/clase/" + c.key;
      };
      listaClases.appendChild(card);
    });
    screen.appendChild(listaClases);

    screen.appendChild(el("h2", null, "Unit words"));
    var lista = el("div", "chip-list");
    u.words.forEach(function (w) {
      var b = el("button", null, w.emoji + " " + w.en);
      b.onclick = function () { global.Audio.speak(w.en); };
      lista.appendChild(b);
    });
    screen.appendChild(lista);

    screen.appendChild(el("h2", null, "Sentences to practise"));
    var listaFrases = el("div", "lista");
    u.structures.forEach(function (s) {
      // admite {en:"..."} y también texto plano, por si el contenido viene de otra versión
      var texto = (typeof s === "string") ? s : (s && s.en ? s.en : "");
      if (!texto) { return; }
      var card = el("div", "card tap");
      card.appendChild(el("div", "emoji", "💬"));
      var g = el("div", "grow");
      g.appendChild(el("div", "title", texto));
      card.appendChild(g);
      card.onclick = function () { global.Audio.speak(texto); };
      listaFrases.appendChild(card);
    });
    screen.appendChild(listaFrases);

    screen.appendChild(el("h2", null, "For the parent"));
    var info = el("div", "card");
    info.appendChild(el("p", null, "<b>Song & routine:</b> " + (u.song || "—")));
    info.appendChild(el("p", null, "<b>Class games:</b> " + (u.games || "—")));
    info.appendChild(el("p", null, "<b>Materials:</b> " + (u.materials || "—")));
    info.appendChild(el("p", null, "<b>Assessment:</b> " + (u.evaluation || "—")));
    info.appendChild(el("p", null, "<b>Project:</b> " + (u.project || "—")));
    screen.appendChild(info);
  }

  /* ------------------------------------------------------------- lección */
  function pintarLeccion(key) {
    var leccion = Store.lesson(key);
    screen.innerHTML = "";
    if (!leccion) { location.hash = "#/"; return; }
    var uid = key.split(".").slice(0, 2).join(".");
    var u = Store.unit(uid), lv = Store.levelOfUnit(uid);

    if (!Store.isUnlocked(key)) {
      toast("This class is still locked 🔒");
      location.hash = "#/unidad/" + uid;
      return;
    }

    var tareas = leccion.tasks.filter(function (t) { return global.Activities.existe(t); });
    if (!tareas.length) { tareas = ["flashcards"]; }

    var estado = { i: 0, fallos: 0 };
    var ctx = {
      lesson: leccion, unit: u, level: lv, num: 1, total: tareas.length,
      responder: function (perfecto) { if (!perfecto) { estado.fallos++; } }
    };

    function cabeceraLeccion() {
      var h = el("div");
      var t = el("div", "act-head");
      var salir = el("button", "icon-btn soft", "✕");
      salir.setAttribute("aria-label", "Salir de la clase");
      salir.onclick = function () { location.hash = "#/unidad/" + uid; };
      t.appendChild(salir);
      t.appendChild(el("span", "step", u.title + " · Class " + leccion.n));
      h.appendChild(t);
      h.appendChild(el("div", "act-title", leccion.focus));
      return h;
    }

    function paso() {
      screen.innerHTML = "";
      screen.classList.add("pantalla-actividad");
      screen.appendChild(cabeceraLeccion());
      var cont = el("div");
      cont.id = "act-container";
      ctx.num = estado.i + 1;
      screen.appendChild(cont);
      global.Audio.desbloquear();
      global.Activities.start(tareas[estado.i], ctx, cont, siguiente);
    }

    function siguiente() {
      estado.i++;
      if (estado.i < tareas.length) { paso(); }
      else { terminar(); }
    }

    function terminar() {
      var fallos = estado.fallos;
      var stars = fallos === 0 ? 3 : (fallos <= 2 ? 2 : 1);
      Store.finishLesson(key, stars);

      var insignia = Store.checkBadge(lv.id);
      var texto = leccion.evidence ? "Lo-logrado: " + leccion.evidence : "Class complete!";
      celebrar({
        emoji: insignia ? (insignia.badgeEmoji || "🏅") : "🎉",
        titulo: insignia ? "Badge earned!" : "Class complete!",
        texto: insignia ? ("Ganaste: " + insignia.badge) : texto,
        estrellas: stars,
        alCerrar: function () {
          var up = Store.unitProgress(uid);
          location.hash = (up.done === up.total) ? "#/nivel/" + lv.id : "#/unidad/" + uid;
        }
      });
    }

    paso();
  }

  /* ------------------------------------------------------------- progreso */
  function pintarProgreso() {
    screen.innerHTML = "";
    screen.appendChild(tituloH1("📊 My Progress"));
    var volverProg = el("button", "big-btn ghost", "◀ Back to Settings");
    volverProg.onclick = function () { location.hash = "#/ajustes"; };
    screen.appendChild(volverProg);
    var total = Store.totalStars();
    screen.appendChild(heroe("You have <b>" + total + "</b> stars and <b>" + Store.doneCount() +
      "</b> classes. Keep it up!"));
    screen.appendChild(barra(total, Store.maxStars()));
    screen.appendChild(el("p", "muted", total + " of " + Store.maxStars() + " stars earned"));

    var racha = Store.raw().streak || 0;
    var card = el("div", "card center");
    card.appendChild(el("div", "badge-big", racha >= 3 ? "🔥" : "📅"));
    card.appendChild(el("div", null, "<b>" + racha + "</b> " + (racha === 1 ? "day in a row" : "days in a row")));
    card.appendChild(el("p", "muted", "Practise a little every day and your pet will be very happy."));
    screen.appendChild(card);

    screen.appendChild(el("h2", null, "Badges"));
    Store.levels().forEach(function (lv) {
      var p = Store.levelProgress(lv.id);
      var c = el("div", "card tap" + (Store.hasBadge(lv.id) ? " done" : ""));
      c.appendChild(el("div", "emoji", Store.hasBadge(lv.id) ? (lv.badgeEmoji || "🏅") : "🔒"));
      var g = el("div", "grow");
      g.appendChild(el("div", "title", lv.badge));
      g.appendChild(el("div", "sub", "Level " + lv.id + " · " + p.done + "/" + p.total + " classes"));
      g.appendChild(barra(p.done, p.total));
      c.appendChild(g);
      c.onclick = function () { location.hash = "#/nivel/" + lv.id; };
      listaNiveles.appendChild(c);
    });
    screen.appendChild(listaNiveles);
  }

  /* ------------------------------------------------------------- ajustes */
  function pintarAjustes() {
    var s = Store.settings();
    screen.innerHTML = "";
    screen.appendChild(tituloH1("⚙️ Settings"));

    var accesos = el("div", "ajustes-accesos");
    var bProg = el("button", "ajuste-acceso", "📊 My Progress");
    bProg.onclick = function () { location.hash = "#/progreso"; };
    accesos.appendChild(bProg);
    screen.appendChild(accesos);

    var card = el("div", "card");

    var filaNombre = el("button", "ajuste-nombre");
    filaNombre.appendChild(el("span", null, "🙂 Your name"));
    filaNombre.appendChild(el("b", null, Store.nombre() || "Add"));
    filaNombre.onclick = function () { location.hash = "#/nombre"; };
    card.appendChild(filaNombre);

    function filaSwitch(etiqueta, valor, alCambiar) {
      var row = el("div", "switch-row");
      row.appendChild(el("div", null, etiqueta));
      var b = el("button", "switch" + (valor ? " on" : ""));
      b.appendChild(el("i"));
      b.setAttribute("aria-label", etiqueta);
      b.onclick = function () { alCambiar(!valor); pintarAjustes(); };
      row.appendChild(b);
      return row;
    }

    card.appendChild(filaSwitch("🔊 English voice", s.voice !== false, function (v) {
      s.voice = v; Store.save();
      if (v) { global.Audio.speak("Hello! Let's learn English."); }
      else { global.Audio.stop(); }
    }));
    card.appendChild(filaSwitch("📳 Vibrate when correct", s.vibrate !== false, function (v) {
      s.vibrate = v; Store.save();
    }));

    /* --- juego de ilustraciones: clásicas o nuevas --- */
    if (Store.tieneV2()) {
      var juegos = el("div", "switch-row");
      juegos.appendChild(el("div", null, "🎨 Illustrations"));
      var seg = el("div", "seg");
      [["a", "Classic"], ["b", "New"]].forEach(function (op) {
        var b = el("button", (s.imagenes === "b" ? "b" : "a") === op[0] ? "seg-on" : "", op[1]);
        b.onclick = function () { Store.setImagenes(op[0]); pintarAjustes(); };
        seg.appendChild(b);
      });
      juegos.appendChild(seg);
      card.appendChild(juegos);
      var tam = el("div", "switch-row");
      tam.appendChild(el("div", null, "🔠 Text size"));
      var segT = el("div", "seg");
      [["n", "Normal"], ["g", "Large"]].forEach(function (op) {
        var b = el("button", (s.texto === "g" ? "g" : "n") === op[0] ? "seg-on" : "", op[1]);
        b.onclick = function () { s.texto = op[0]; Store.save(); aplicarTexto(); pintarAjustes(); };
        segT.appendChild(b);
      });
      tam.appendChild(segT);
      card.appendChild(tam);

      var nuevas = (global.LANGKIDS_IMG_V2 || []).length;
      var totalPalabras = 328;
      var pct = Math.min(100, Math.round(nuevas * 100 / totalPalabras));
      var barra = el("div", "prog-mini");
      var relleno = el("div", "prog-mini-fill");
      relleno.style.width = pct + "%";
      barra.appendChild(relleno);
      card.appendChild(barra);
      card.appendChild(el("div", "muted",
        nuevas + " of " + totalPalabras + " words already have the new picture (" + pct + "%). " +
        "The rest still show the classic one."));
    }

    var vel = el("div", "switch-row");
    vel.appendChild(el("div", null, "🐢 Voice speed"));
    var input = document.createElement("input");
    input.type = "range"; input.min = "0.6"; input.max = "1.1"; input.step = "0.05";
    input.value = String(s.rate || 0.85);
    input.style.width = "150px";
    input.onchange = function () {
      s.rate = parseFloat(input.value); Store.save();
      global.Audio.speak("This is my voice.");
    };
    vel.appendChild(input);
    card.appendChild(vel);

    screen.appendChild(card);

    var probar = el("button", "big-btn", "🔊 Test the voice");
    probar.onclick = function () { global.Audio.speak("Hello! My name is Milo. Let's play!"); };
    screen.appendChild(probar);
    screen.appendChild(el("div", null, "<div style='height:10px'></div>"));

    if (!global.Audio.vozDisponible()) {
      screen.appendChild(el("div", "audio-warn",
        "This device has no English voice installed. Add one in Settings → " +
        "Idioma y entrada de texto → Salida de texto a voz. Los juegos funcionan igual, sin voz."));
    }

    var reiniciar = el("button", "big-btn ghost", "🗑️ Reset my progress");
    reiniciar.onclick = function () {
      preguntar("Reset progress?", "Stars and finished classes will be erased.", function () {
        Store.reset();
        toast("Progress reset");
        location.hash = "#/";
      });
    };
    screen.appendChild(reiniciar);

    var acerca = el("div", "card");
    acerca.appendChild(el("p", null, "<b>LangKids English</b> · version " + VERSION));
    acerca.appendChild(el("p", "muted",
      "Built from the LangKids curriculum: 4 levels, 16 units and 80 classes. " +
      "Works offline, asks for no permissions and collects no data: all progress " +
      "is stored on this device."));
    var creditos = el("p", "muted", "16 units · " + Store.flatLessons().length + " classes loaded");
    acerca.appendChild(creditos);

    // atribución de las fotos (requisito de la API de Pixabay)
    var cr = global.LANGKIDS_CREDITS;
    if (cr && cr.imagenes) {
      var claves = Object.keys(cr.imagenes);
      if (claves.length) {
        acerca.appendChild(el("p", null, "<b>Pictures:</b> Pixabay (pixabay.com) · " +
          "Pixabay Content License · " + claves.length + " images"));
        var autores = {};
        claves.forEach(function (k) {
          var a = cr.imagenes[k].autor || "—";
          autores[a] = (autores[a] || 0) + 1;
        });
        var lista = Object.keys(autores).sort(function (a, b) { return autores[b] - autores[a]; });
        acerca.appendChild(el("p", "muted", "Photographers: " + lista.join(", ") + "."));
        acerca.appendChild(el("p", "muted",
          "Downloaded and bundled for offline educational use; every image keeps its " +
          "authorship record in the credits file."));
      }
    }
    screen.appendChild(acerca);
  }













  /* ------------------------------------------------------------- nombre */
  function pintarNombre(esPrimeraVez) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");

    var caja = el("div", "nombre-caja");
    caja.appendChild(el("div", "nombre-emoji", "👋"));
    caja.appendChild(el("h2", "nombre-titulo", esPrimeraVez
      ? "What's your name?"
      : "Your name"));
    caja.appendChild(el("p", "muted", esPrimeraVez
      ? "We will use it to say hello and to celebrate your progress."
      : "Type a new name to change it."));

    var entrada = document.createElement("input");
    entrada.className = "nombre-input";
    entrada.type = "text";
    entrada.maxLength = 20;
    entrada.placeholder = "e.g. Emma";
    entrada.value = Store.nombre();
    entrada.setAttribute("autocomplete", "off");
    entrada.setAttribute("spellcheck", "false");
    caja.appendChild(entrada);

    var fila = el("div", "nombre-fila");
    var guardarBtn = el("button", "big-btn", esPrimeraVez ? "Let's start!" : "Save");
    guardarBtn.onclick = function () {
      var limpio = entrada.value.replace(/[^A-Za-zÀ-ÿ' -]/g, "").trim().slice(0, 20);
      if (!limpio) {
        toast("Type your name 🙂");
        entrada.focus();
        return;
      }
      Store.setNombre(limpio);
      aplicarNombre();
      if (global.Audio && global.Audio.speak) { global.Audio.speak("Hello " + limpio + "!"); }
      location.hash = esPrimeraVez ? "#/inicio" : "#/ajustes";
    };
    fila.appendChild(guardarBtn);

    if (esPrimeraVez) {
      var luego = el("button", "big-btn gris", "Later");
      luego.onclick = function () { location.hash = "#/inicio"; };
      fila.appendChild(luego);
    }
    caja.appendChild(fila);
    screen.appendChild(caja);

    entrada.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter") { guardarBtn.click(); }
    });
    setTimeout(function () { try { entrada.focus(); } catch (e) {} }, 200);
  }

  /** Pinta el saludo con su nombre en la barra superior. */
  function aplicarNombre() {
    var titulo = document.getElementById("topbar-title");
    if (!titulo) { return; }
    var quien = Store.nombre();
    titulo.textContent = quien ? "Hi, " + quien + "!" : "LangKids";
  }

  /* ------------------------------------------------------------- juegos */
  var JUEGOS = [
    { id: "memo", emoji: "🃏", titulo: "Memory Games", sub: "Find the pairs", ruta: "#/memoramas", tono: "tono-memo" },
    { id: "bingo", emoji: "🔊", titulo: "Word Bingo", sub: "Listen and tap", ruta: "#/bingo", tono: "tono-bingo" },
    { id: "falta", emoji: "❓", titulo: "What's Missing?", sub: "Look and remember", ruta: "#/falta", tono: "tono-falta" },
    { id: "traza", emoji: "✍️", titulo: "Trace the Word", sub: "Write with your finger", ruta: "#/traza", tono: "tono-traza" },
    { id: "domino", emoji: "🧩", titulo: "Word Domino", sub: "Match word & picture", ruta: "#/domino", tono: "tono-domino" },
    { id: "busca", emoji: "🔍", titulo: "I Spy", sub: "Find the object", ruta: "#/busca", tono: "tono-busca" },
    { id: "repaso", emoji: "🧠", titulo: "Smart Review", sub: "10 words for you", ruta: "#/repaso", tono: "tono-repaso" },
    { id: "rueda", emoji: "🎡", titulo: "Word Wheel", sub: "Spin and say it", ruta: "#/rueda", tono: "tono-rueda" }
  ];

  function pintarJuegos() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/inicio"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🎮 Games"));
    screen.appendChild(cab);

    var grid = el("div", "juegos-grid");
    var portadas = global.LANGKIDS_INICIO || {};
    JUEGOS.forEach(function (j) {
      var b = el("button", "juego-tarjeta " + j.tono);
      if (portadas[j.id]) {
        var pic = document.createElement("img");
        pic.className = "juego-img";
        pic.src = portadas[j.id];
        pic.alt = j.titulo;
        b.appendChild(pic);
      } else {
        b.appendChild(el("div", "juego-emoji", j.emoji));
      }
      b.appendChild(el("div", "juego-titulo", j.titulo));
      b.appendChild(el("div", "juego-sub", j.sub));
      b.onclick = function () { location.hash = j.ruta; };
      grid.appendChild(b);
    });
    screen.appendChild(grid);
  }



  /* ---------------------------------------------------- cuento de la unidad */
  function cuentosDeUnidad(uid) {
    var todos = global.LANGKIDS_CUENTOS || {};
    return todos[uid] || null;
  }

  function pintarCuento(uid) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cuento = cuentosDeUnidad(uid);
    if (!cuento) { location.hash = "#/unidad/" + uid; return; }
    var u = Store.unit(uid);

    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/unidad/" + uid; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "📖 " + cuento.titulo));
    screen.appendChild(cab);

    global.Cuento.montar(screen, { cuento: cuento }, function (r) {
      celebrar({
        emoji: "📖",
        titulo: "Story finished! Congratulations!",
        texto: "You answered " + r.aciertos + " of " + r.preguntas + " questions" +
               (r.fallos ? " with " + r.fallos + (r.fallos === 1 ? " miss." : " misses.") : "."),
        estrellas: r.fallos === 0 ? 3 : (r.fallos <= 2 ? 2 : 1),
        alCerrar: function () { location.hash = "#/unidad/" + uid; }
      });
    });
  }

  /* ---------------------------------------------------- rueda de palabras */
  function pintarRuedaMenu() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/juegos"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🎡 Word Wheel"));
    screen.appendChild(cab);
    screen.appendChild(el("p", "muted",
      "Spin the wheel, say the word out loud and listen to it."));

    var grid = el("div", "bingo-niveles");
    Store.levels().forEach(function (lv) {
      var cuantas = palabrasDelNivel(lv.id).length;
      var b = el("button", "bingo-nivel tone-" + ((lv.id - 1) % 4 + 1));
      var portadas = global.LANGKIDS_NIVELES || {};
      if (portadas[lv.id]) {
        var pic = document.createElement("img");
        pic.className = "nivel-portada";
        pic.src = portadas[lv.id];
        pic.alt = "Level " + lv.id;
        b.appendChild(pic);
      } else {
        b.appendChild(el("div", "bingo-nivel-emoji", lv.emoji || "📘"));
      }
      b.appendChild(el("div", "bingo-nivel-titulo", "Level " + lv.id));
      b.appendChild(el("div", "bingo-nivel-sub", cuantas + " words"));
      b.onclick = function () { location.hash = "#/rueda/" + lv.id; };
      grid.appendChild(b);
    });
    screen.appendChild(grid);
  }

  function pintarRueda(id) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var lv = Store.level(id);
    var palabras = palabrasDelNivel(id);
    if (!lv || palabras.length < 6) { location.hash = "#/rueda"; return; }

    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/rueda"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🎡 " + lv.emoji + " Level " + lv.id));
    screen.appendChild(cab);

    global.Rueda.montar(screen, { palabras: palabras, giros: 6 }, function (r) {
      celebrar({
        emoji: "🎡",
        titulo: "You said them all! Congratulations!",
        texto: "You said " + r.giros + " words out loud.",
        estrellas: 3,
        alCerrar: function () { location.hash = "#/rueda"; }
      });
    });
  }

  /* ---------------------------------------------------- busca y toca */
  function pintarBuscaMenu() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/inicio"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🔍 I Spy"));
    screen.appendChild(cab);
    screen.appendChild(el("p", "muted",
      "Listen and find the object in the scene."));

    var grid = el("div", "bingo-niveles");
    Store.levels().forEach(function (lv) {
      var cuantas = palabrasDelNivel(lv.id).length;
      var b = el("button", "bingo-nivel tone-" + ((lv.id - 1) % 4 + 1));
      var portadas = global.LANGKIDS_NIVELES || {};
      if (portadas[lv.id]) {
        var pic = document.createElement("img");
        pic.className = "nivel-portada";
        pic.src = portadas[lv.id];
        pic.alt = "Level " + lv.id;
        b.appendChild(pic);
      } else {
        b.appendChild(el("div", "bingo-nivel-emoji", lv.emoji || "📘"));
      }
      b.appendChild(el("div", "bingo-nivel-titulo", "Level " + lv.id));
      b.appendChild(el("div", "bingo-nivel-sub", cuantas + " words"));
      b.onclick = function () { location.hash = "#/busca/" + lv.id; };
      grid.appendChild(b);
    });
    screen.appendChild(grid);
  }

  function pintarBusca(id) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var lv = Store.level(id);
    var palabras = palabrasDelNivel(id);
    if (!lv || palabras.length < 8) { location.hash = "#/busca"; return; }

    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/busca"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🔍 " + lv.emoji + " Level " + lv.id));
    screen.appendChild(cab);

    global.Busca.montar(screen, { palabras: palabras, rondas: 4, objetos: 6 }, function (r) {
      var estrellas = r.fallos === 0 ? 3 : (r.fallos <= 2 ? 2 : 1);
      celebrar({
        emoji: "🔍",
        titulo: "You found them all! Congratulations!",
        texto: "You spotted " + r.aciertos + " objects" +
               (r.fallos ? " with " + r.fallos + (r.fallos === 1 ? " miss." : " misses.") : "."),
        estrellas: estrellas,
        alCerrar: function () { location.hash = "#/busca"; }
      });
    });
  }

  /* ---------------------------------------------------- dominó palabra-imagen */
  function pintarDominoMenu() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/inicio"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🧩 Word Domino"));
    screen.appendChild(cab);
    screen.appendChild(el("p", "muted",
      "Read the word and match it with the picture."));

    var grid = el("div", "bingo-niveles");
    Store.levels().forEach(function (lv) {
      var cuantas = palabrasDelNivel(lv.id).length;
      var b = el("button", "bingo-nivel tone-" + ((lv.id - 1) % 4 + 1));
      var portadas = global.LANGKIDS_NIVELES || {};
      if (portadas[lv.id]) {
        var pic = document.createElement("img");
        pic.className = "nivel-portada";
        pic.src = portadas[lv.id];
        pic.alt = "Level " + lv.id;
        b.appendChild(pic);
      } else {
        b.appendChild(el("div", "bingo-nivel-emoji", lv.emoji || "📘"));
      }
      b.appendChild(el("div", "bingo-nivel-titulo", "Level " + lv.id));
      b.appendChild(el("div", "bingo-nivel-sub", cuantas + " words"));
      b.onclick = function () { location.hash = "#/domino/" + lv.id; };
      grid.appendChild(b);
    });
    screen.appendChild(grid);
  }

  function pintarDomino(id) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var lv = Store.level(id);
    var palabras = palabrasDelNivel(id);
    if (!lv || palabras.length < 8) { location.hash = "#/domino"; return; }

    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/domino"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🧩 " + lv.emoji + " Level " + lv.id));
    screen.appendChild(cab);

    global.Domino.montar(screen, { palabras: palabras, colocaciones: 4 }, function (r) {
      var estrellas = r.fallos === 0 ? 3 : (r.fallos <= 2 ? 2 : 1);
      celebrar({
        emoji: "🧩",
        titulo: "Great reading! Congratulations!",
        texto: "You matched " + r.colocaciones + " dominoes" +
               (r.fallos ? " with " + r.fallos + (r.fallos === 1 ? " miss." : " misses.") : "."),
        estrellas: estrellas,
        alCerrar: function () { location.hash = "#/domino"; }
      });
    });
  }

  /* ---------------------------------------------------- repaso inteligente */
  function palabrasDelCurso() {
    var vistas = {};
    var out = [];
    Store.levels().forEach(function (lv) {
      lv.units.forEach(function (u) {
        u.words.forEach(function (w) {
          if (!w.img || vistas[w.en]) { return; }
          vistas[w.en] = true;
          out.push({ en: w.en, img: w.img, emoji: w.emoji });
        });
      });
    });
    return out;
  }

  function pintarRepaso() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/inicio"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🧠 Smart Review"));
    screen.appendChild(cab);

    var palabras = palabrasDelCurso();
    if (palabras.length < 4) {
      screen.appendChild(el("p", "muted", "There are not enough words yet."));
      return;
    }

    var debiles = Store.palabrasPrioritarias(palabras, 10);
    var falladas = debiles.filter(function (p) {
      var n = Store.notaDe(p.en);
      return n && n.f > 0;
    }).length;
    screen.appendChild(el("p", "muted",
      "10 words picked for you" + (falladas
        ? ". You have " + falladas + " to practise more."
        : ". Let's see how many you remember.")));

    global.Repaso.montar(screen, { palabras: palabras, cuantas: 10 }, function (r) {
      var estrellas = r.fallos === 0 ? 3 : (r.fallos <= 2 ? 2 : 1);
      celebrar({
        emoji: "🧠",
        titulo: "Review finished! Congratulations!",
        texto: "You got " + r.aciertos + " of " + r.cuantas + " right" +
               (r.fallos ? " with " + r.fallos + (r.fallos === 1 ? " miss." : " misses.") : "."),
        estrellas: estrellas,
        alCerrar: function () { location.hash = "#/inicio"; }
      });
    });
  }

  /* ---------------------------------------------------- trazar palabra */
  function pintarTrazaMenu() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/inicio"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "✍️ Trace the Word"));
    screen.appendChild(cab);
    screen.appendChild(el("p", "muted",
      "Trace the letters with your finger. Listen to the word first!"));

    var grid = el("div", "bingo-niveles");
    Store.levels().forEach(function (lv) {
      var cuantas = palabrasDelNivel(lv.id).length;
      var b = el("button", "bingo-nivel tone-" + ((lv.id - 1) % 4 + 1));
      var portadas = global.LANGKIDS_NIVELES || {};
      if (portadas[lv.id]) {
        var pic = document.createElement("img");
        pic.className = "nivel-portada";
        pic.src = portadas[lv.id];
        pic.alt = "Level " + lv.id;
        b.appendChild(pic);
      } else {
        b.appendChild(el("div", "bingo-nivel-emoji", lv.emoji || "📘"));
      }
      b.appendChild(el("div", "bingo-nivel-titulo", "Level " + lv.id));
      b.appendChild(el("div", "bingo-nivel-sub", cuantas + " words"));
      b.onclick = function () { location.hash = "#/traza/" + lv.id; };
      grid.appendChild(b);
    });
    screen.appendChild(grid);
  }

  function pintarTraza(id) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var lv = Store.level(id);
    var palabras = palabrasDelNivel(id);
    if (!lv || !palabras.length) { location.hash = "#/traza"; return; }

    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/traza"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "✍️ " + lv.emoji + " Level " + lv.id));
    screen.appendChild(cab);

    global.Traza.montar(screen, { palabras: palabras, cuantas: 5 }, function (r) {
      celebrar({
        emoji: "✍️",
        titulo: "Beautiful writing! Congratulations!",
        texto: "You traced " + r.hechas + " words.",
        estrellas: 3,
        alCerrar: function () { location.hash = "#/traza"; }
      });
    });
  }

  /* ---------------------------------------------------- ¿qué falta? */
  function pintarFaltaMenu() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/inicio"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "❓ What's Missing?"));
    screen.appendChild(cab);
    screen.appendChild(el("p", "muted",
      "Look at the pictures. One disappears — tap the one that is missing."));

    var grid = el("div", "bingo-niveles");
    Store.levels().forEach(function (lv) {
      var cuantas = palabrasDelNivel(lv.id).length;
      var b = el("button", "bingo-nivel tone-" + ((lv.id - 1) % 4 + 1));
      var portadas = global.LANGKIDS_NIVELES || {};
      if (portadas[lv.id]) {
        var pic = document.createElement("img");
        pic.className = "nivel-portada";
        pic.src = portadas[lv.id];
        pic.alt = "Level " + lv.id;
        b.appendChild(pic);
      } else {
        b.appendChild(el("div", "bingo-nivel-emoji", lv.emoji || "📘"));
      }
      b.appendChild(el("div", "bingo-nivel-titulo", "Level " + lv.id));
      b.appendChild(el("div", "bingo-nivel-sub", cuantas + " words"));
      b.onclick = function () { location.hash = "#/falta/" + lv.id; };
      grid.appendChild(b);
    });
    screen.appendChild(grid);
  }

  function pintarFalta(id) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var lv = Store.level(id);
    var palabras = palabrasDelNivel(id);
    if (!lv || palabras.length < 6) { location.hash = "#/falta"; return; }

    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/falta"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "❓ " + lv.emoji + " Level " + lv.id));
    screen.appendChild(cab);

    global.Falta.montar(screen, { palabras: palabras, rondas: 4 }, function (r) {
      var estrellas = r.fallos === 0 ? 3 : (r.fallos <= 2 ? 2 : 1);
      celebrar({
        emoji: "🧠",
        titulo: "Great memory! Congratulations!",
        texto: "You remembered all " + r.rondas + " words" +
               (r.fallos === 0 ? " without a single miss." : " with " + r.fallos +
                (r.fallos === 1 ? " miss." : " misses.")),
        estrellas: estrellas,
        alCerrar: function () { location.hash = "#/falta"; }
      });
    });
  }

  /* ------------------------------------------------------------- bingo */
  function palabrasDelNivel(id) {
    var lv = Store.level(id);
    if (!lv) { return []; }
    var vistas = {};
    var out = [];
    lv.units.forEach(function (u) {
      u.words.forEach(function (w) {
        if (!w.img || vistas[w.en]) { return; }
        vistas[w.en] = true;
        out.push({ en: w.en, img: w.img, emoji: w.emoji });
      });
    });
    return out;
  }

  function pintarBingoMenu() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/inicio"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🔊 Word Bingo"));
    screen.appendChild(cab);

    screen.appendChild(el("p", "muted",
      "Listen to the word and tap the right picture."));

    var grid = el("div", "bingo-niveles");
    Store.levels().forEach(function (lv) {
      var cuantas = palabrasDelNivel(lv.id).length;
      var b = el("button", "bingo-nivel tone-" + ((lv.id - 1) % 4 + 1));
      var portadas = global.LANGKIDS_NIVELES || {};
      if (portadas[lv.id]) {
        var pic = document.createElement("img");
        pic.className = "nivel-portada";
        pic.src = portadas[lv.id];
        pic.alt = "Level " + lv.id;
        b.appendChild(pic);
      } else {
        b.appendChild(el("div", "bingo-nivel-emoji", lv.emoji || "📘"));
      }
      b.appendChild(el("div", "bingo-nivel-titulo", "Level " + lv.id));
      b.appendChild(el("div", "bingo-nivel-sub", cuantas + " words"));
      b.onclick = function () { location.hash = "#/bingo/" + lv.id; };
      grid.appendChild(b);
    });
    screen.appendChild(grid);
  }

  function pintarBingo(id) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var lv = Store.level(id);
    var palabras = palabrasDelNivel(id);
    if (!lv || palabras.length < 9) { location.hash = "#/bingo"; return; }

    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/bingo"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🔊 Bingo · " + lv.emoji + " Level " + lv.id));
    screen.appendChild(cab);

    global.Bingo.montar(screen, { palabras: palabras, titulo: "Level " + lv.id }, function (r) {
      var estrellas = r.fallos === 0 ? 3 : (r.fallos <= 3 ? 2 : 1);
      celebrar({
        emoji: "🎊",
        titulo: "Bingo! Congratulations!",
        texto: "You found all 9 words with " + r.fallos +
               (r.fallos === 1 ? " miss." : " misses."),
        estrellas: estrellas,
        alCerrar: function () { location.hash = "#/bingo"; }
      });
    });
  }

  /* ------------------------------------------------------------- memoramas */
  function pintarMemoramas() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/inicio"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🃏 Memory Games"));
    screen.appendChild(cab);

    var grid = el("div", "memo-mazos");
    Object.keys(global.Memorama.mazos).forEach(function (id) {
      var mazo = global.Memorama.mazos[id];
      var b = el("button", "memo-mazo " + mazo.tono);
      var portadas = global.LANGKIDS_MAZOS || {};
      if (portadas[id]) {
        var img = document.createElement("img");
        img.className = "memo-mazo-img";
        img.src = portadas[id];
        img.alt = mazo.titulo;
        b.appendChild(img);
      } else {
        b.appendChild(el("div", "memo-mazo-emoji", mazo.emoji));
      }
      b.appendChild(el("div", "memo-mazo-titulo", mazo.titulo));
      b.appendChild(el("div", "memo-mazo-sub", mazo.parejas.length + " pairs"));
      b.onclick = function () { location.hash = "#/memorama/" + id; };
      grid.appendChild(b);
    });
    screen.appendChild(grid);
  }

  function pintarMemorama(id) {
    screen.innerHTML = "";
    screen.classList.add("pantalla-memo");
    var mazo = global.Memorama.mazos[id];
    if (!mazo) { location.hash = "#/memoramas"; return; }

    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back");
    atras.onclick = function () { location.hash = "#/memoramas"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", mazo.emoji + " " + mazo.titulo));
    screen.appendChild(cab);

    global.Memorama.montar(screen, id, function (r) {
      var estrellas = r.intentos <= r.total ? 3 : (r.intentos <= r.total * 2 ? 2 : 1);
      celebrar({
        emoji: "🃏",
        titulo: "Well done! Congratulations!",
        texto: "You found all " + r.total + " pairs in " + r.intentos +
               (r.intentos === 1 ? " move." : " moves."),
        estrellas: estrellas,
        alCerrar: function () { location.hash = "#/memoramas"; }
      });
    });
  }

  /* ------------------------------------------------------------- pintar */
  function pintarPizarra() {
    screen.innerHTML = "";
    screen.classList.add("pantalla-pintar");
    var app = global.Paint.montar(screen, function (id) {
      toast("Saved! It is in My Drawings 🖼️");
      setTimeout(function () { pintarGaleria(id); }, 700);
    }, function () { location.hash = "#/inicio"; },
       function () { location.hash = "#/galeria"; });
    setTimeout(function () { app.ajustar(); }, 150);
  }

  /* ------------------------------------------------------------- galería */
  function pintarGaleria(destacar) {
    var lista = global.Dibujos.listar();
    screen.innerHTML = "";
    var cab = el("div", "paint-cabecera");
    var atras = el("button", "paint-volver", "‹");
    atras.setAttribute("aria-label", "back to paint");
    atras.onclick = function () { location.hash = "#/pintar"; };
    cab.appendChild(atras);
    cab.appendChild(el("div", "paint-titulo", "🖼️ My Drawings"));
    screen.appendChild(cab);

    if (!lista.length) {
      screen.appendChild(el("p", "muted", "No drawings yet. Open 🎨 Paint and save the first one."));
      var ir = el("button", "big-btn", "🎨 Paint now");
      ir.onclick = function () { location.hash = "#/pintar"; };
      screen.appendChild(ir);
      return;
    }

    var grid = el("div", "gal-grid");
    lista.forEach(function (d) {
      var caja = el("div", "gal-item" + (d.id === destacar ? " nueva" : ""));
      var img = document.createElement("img");
      img.alt = "dibujo";
      img.loading = "lazy";
      img.src = global.Dibujos.cargar(d.id);
      caja.appendChild(img);
      var fecha = new Date(d.ts || Date.now());
      caja.appendChild(el("div", "gal-fecha",
        fecha.getDate() + "/" + (fecha.getMonth() + 1) + " " +
        ("0" + fecha.getHours()).slice(-2) + ":" + ("0" + fecha.getMinutes()).slice(-2)));
      caja.onclick = function () { verDibujo(d); };
      grid.appendChild(caja);
    });
    screen.appendChild(grid);
  }

  function verDibujo(d) {
    var capa = el("div", "visor");
    var caja = el("div", "visor-caja");
    var img = document.createElement("img");
    img.src = global.Dibujos.cargar(d.id);
    caja.appendChild(img);

    var fila = el("div", "gal-acciones");
    if (global.Dibujos.puedeExportar()) {
      var exp = el("button", "big-btn ghost", "📥 Save to phone");
      exp.onclick = function () {
        exp.textContent = global.Dibujos.exportar(d.id)
          ? "✅ Guardado en Fotos/LangKids"
          : "😕 Could not save";
      };
      fila.appendChild(exp);
    }
    var borrar = el("button", "big-btn ghost", "🗑️ Delete");
    borrar.onclick = function () {
      if (!global.confirm("Delete this drawing?")) { return; }
      global.Dibujos.borrar(d.id);
      document.body.removeChild(capa);
      pintarGaleria();
    };
    fila.appendChild(borrar);

    var cerrar = el("button", "big-btn", "Close");
    cerrar.onclick = function () { document.body.removeChild(capa); };
    fila.appendChild(cerrar);

    caja.appendChild(fila);
    capa.appendChild(caja);
    capa.onclick = function (ev) { if (ev.target === capa) { document.body.removeChild(capa); } };
    document.body.appendChild(capa);
  }

  /** Aviso breve en pantalla. */
  function toast(txt) {
    var t = el("div", "toast", txt);
    document.body.appendChild(t);
    setTimeout(function () { t.classList.add("ver"); }, 20);
    setTimeout(function () {
      t.classList.remove("ver");
      setTimeout(function () { if (t.parentNode) { t.parentNode.removeChild(t); } }, 300);
    }, 1900);
  }
  global.AppToast = toast;

  /* ------------------------------------------------------------- router */
  function ruta() {
    aplicarNombre();
    screen.classList.remove("pantalla-pintar");
    screen.classList.remove("pantalla-inicio");
    screen.classList.remove("pantalla-memo");
    var hash = location.hash || "#/";
    // la pizarra va a pantalla completa: sin barra superior ni pestañas
    var enPintura = hash.indexOf("#/pintar") === 0;
    document.body.classList.toggle("modo-pintura", enPintura);
    // durante la leccion se oculta la barra inferior: mas espacio y cero distracciones
    var enLeccion = hash.indexOf("#/clase/") === 0;
    screen.style.paddingBottom = enLeccion ? "24px" : "28px";
    // la pizarra ocupa todo: sin relleno
    if (enPintura) { screen.style.paddingBottom = "0px"; }
    var m;

    if ((m = hash.match(/^#\/nivel\/(\d+)/))) { pintarNivel(m[1]); return; }
    if ((m = hash.match(/^#\/unidad\/([\d.]+)/))) { pintarUnidad(m[1]); return; }
    if ((m = hash.match(/^#\/clase\/([\d.]+)/))) { pintarLeccion(m[1]); return; }
    if (hash.indexOf("#/pintar") === 0) { pintarPizarra(); return; }
    if (hash.indexOf("#/galeria") === 0) { pintarGaleria(); return; }
    if ((m = hash.match(/^#\/bingo\/(\d+)/))) { pintarBingo(m[1]); return; }
    if (hash.indexOf("#/bingo") === 0) { pintarBingoMenu(); return; }
    if ((m = hash.match(/^#\/falta\/(\d+)/))) { pintarFalta(m[1]); return; }
    if (hash.indexOf("#/falta") === 0) { pintarFaltaMenu(); return; }
    if ((m = hash.match(/^#\/traza\/(\d+)/))) { pintarTraza(m[1]); return; }
    if (hash.indexOf("#/traza") === 0) { pintarTrazaMenu(); return; }
    if (hash.indexOf("#/repaso") === 0) { pintarRepaso(); return; }
    if ((m = hash.match(/^#\/cuento\/([\d.]+)/))) { pintarCuento(m[1]); return; }
    if ((m = hash.match(/^#\/domino\/(\d+)/))) { pintarDomino(m[1]); return; }
    if (hash.indexOf("#/domino") === 0) { pintarDominoMenu(); return; }
    if ((m = hash.match(/^#\/busca\/(\d+)/))) { pintarBusca(m[1]); return; }
    if (hash.indexOf("#/busca") === 0) { pintarBuscaMenu(); return; }
    if (hash.indexOf("#/juegos") === 0) { pintarJuegos(); return; }
    if ((hash === "#/" || hash === "" || hash === "#/inicio") && !Store.nombre() && !pedidoNombre) {
      pedidoNombre = true;
      pintarNombre(true);
      return;
    }
    if (hash.indexOf("#/nombre") === 0) { pintarNombre(Store.nombre() === ""); return; }
    if ((m = hash.match(/^#\/rueda\/(\d+)/))) { pintarRueda(m[1]); return; }
    if (hash.indexOf("#/rueda") === 0) { pintarRuedaMenu(); return; }
    if ((m = hash.match(/^#\/memorama\/(\w+)/))) { pintarMemorama(m[1]); return; }
    if (hash.indexOf("#/memoramas") === 0) { pintarMemoramas(); return; }
    if (hash.indexOf("#/clases") === 0) { pintarClases(); return; }
    if (hash.indexOf("#/progreso") === 0) { pintarProgreso(); return; }
    if (hash.indexOf("#/ajustes") === 0) { pintarAjustes(); return; }
    pintarInicio();
  }

  /* ------------------------------------------------------------- arranque */
  function refrescarEstrellas() {
    document.getElementById("star-count").textContent = String(Store.totalStars());
  }

  document.getElementById("btn-home").onclick = function () { location.hash = "#/"; };
  // primer toque: habilita el audio del navegador
  document.addEventListener("touchstart", function () { global.Audio.desbloquear(); }, { once: true });
  document.addEventListener("click", function () { global.Audio.desbloquear(); }, { once: true });

  aplicarTexto();

  document.getElementById("btn-ajustes").onclick = function () { location.hash = "#/ajustes"; };
  document.getElementById("btn-home").onclick = function () { location.hash = "#/inicio"; };

  window.addEventListener("hashchange", function () {
    ruta();
    refrescarEstrellas();
    screen.scrollTop = 0;
  });

  /** Usado por el botón atrás de Android. Devuelve true si navegó dentro de la app. */
  global.AppBack = function () {
    if (!caja.classList.contains("hidden")) { caja.classList.add("hidden"); return true; }
    if (!confirmEl.classList.contains("hidden")) { confirmEl.classList.add("hidden"); return true; }
    var hash = location.hash || "#/";
    if (hash.indexOf("#/clase/") === 0) {
      location.hash = "#/unidad/" + hash.split("/")[2].split(".").slice(0, 2).join(".");
      return true;
    }
    if (hash.indexOf("#/unidad/") === 0) {
      var u = Store.levelOfUnit(hash.split("/")[2]);
      location.hash = u ? "#/nivel/" + u.id : "#/";
      return true;
    }
    if (hash.indexOf("#/nivel/") === 0 || hash.indexOf("#/progreso") === 0 ||
        hash.indexOf("#/ajustes") === 0) {
      location.hash = "#/";
      return true;
    }
    return false;
  };

  Store.load();
  ruta();
  refrescarEstrellas();
})(window);
