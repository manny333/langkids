/* =========================================================================
   store.js — contenido, progreso, desbloqueo y ajustes.
   Persistencia: puente nativo de Android (SharedPreferences) o localStorage.
   ========================================================================= */
(function (global) {
  "use strict";

  var CONTENT = global.LANGKIDS_CONTENT || { levels: [] };
  var KEY = "langkids.progress.v1";

  var progress = {
    stars: {},        // "1.1.2": 1..3
    done: [],         // ["1.1.1", ...]
    badges: [],       // [1, 2, ...]
    streak: 0,
    lastDay: "",
    settings: { voice: true, rate: 0.85, vibrate: true, imagenes: 'a', texto: 'n', nombre: '' },
    palabras: {}
  };

  /* ---------------------------------------------------------- puente nativo */
  function bridge() {
    return (global.Android && typeof global.Android.loadProgress === "function")
      ? global.Android : null;
  }

  function load() {
    var raw = null;
    try {
      var b = bridge();
      raw = b ? b.loadProgress() : global.localStorage.getItem(KEY);
    } catch (e) { raw = null; }
    if (raw) {
      try {
        var obj = JSON.parse(raw);
        if (obj && typeof obj === "object") {
          progress.stars = obj.stars || {};
          progress.done = obj.done || [];
          progress.badges = obj.badges || [];
          progress.streak = obj.streak || 0;
          progress.lastDay = obj.lastDay || "";
          if (obj.settings) {
            progress.settings.voice = obj.settings.voice !== false;
            progress.settings.rate = obj.settings.rate || 0.85;
            progress.settings.vibrate = obj.settings.vibrate !== false;
            if (typeof obj.settings.nombre === "string") {
              progress.settings.nombre = obj.settings.nombre.slice(0, 20);
            }
            progress.settings.imagenes = obj.settings.imagenes === "b" ? "b" : "a";
            progress.settings.texto = obj.settings.texto === "g" ? "g" : "n";
          }
          if (obj.palabras && typeof obj.palabras === "object") {
            progress.palabras = obj.palabras;
          }
        }
      } catch (e) { /* progreso corrupto: se empieza de cero */ }
    }
    return progress;
  }

  function save() {
    var raw = JSON.stringify(progress);
    try {
      var b = bridge();
      if (b) { b.saveProgress(raw); }
      else { global.localStorage.setItem(KEY, raw); }
    } catch (e) { /* sin persistencia: la sesion sigue funcionando */ }
  }

  /* ---------------------------------------------------------- recorrido del curso */
  function levels() { return CONTENT.levels || []; }

  function level(id) {
    var ls = levels();
    for (var i = 0; i < ls.length; i++) { if (String(ls[i].id) === String(id)) { return ls[i]; } }
    return null;
  }

  function unit(uid) {
    var ls = levels();
    for (var i = 0; i < ls.length; i++) {
      var us = ls[i].units;
      for (var j = 0; j < us.length; j++) { if (us[j].id === uid) { return us[j]; } }
    }
    return null;
  }

  function levelOfUnit(uid) {
    var ls = levels();
    for (var i = 0; i < ls.length; i++) {
      for (var j = 0; j < ls[i].units.length; j++) {
        if (ls[i].units[j].id === uid) { return ls[i]; }
      }
    }
    return null;
  }

  function lesson(key) {
    var ls = levels();
    for (var i = 0; i < ls.length; i++) {
      for (var j = 0; j < ls[i].units.length; j++) {
        var cs = ls[i].units[j].classes;
        for (var k = 0; k < cs.length; k++) {
          if (cs[k].key === key) { return cs[k]; }
        }
      }
    }
    return null;
  }

  /** Lista plana de lecciones en orden curricular (para desbloqueo). */
  function flatLessons() {
    var out = [];
    levels().forEach(function (lv) {
      lv.units.forEach(function (u) {
        u.classes.forEach(function (c) { out.push({ key: c.key, clase: c, unit: u, level: lv }); });
      });
    });
    return out;
  }

  /* ---------------------------------------------------------- progreso */
  function isDone(key) { return progress.done.indexOf(key) !== -1; }
  function starsOf(key) { return progress.stars[key] || 0; }
  function totalStars() {
    var t = 0;
    Object.keys(progress.stars).forEach(function (k) { t += progress.stars[k]; });
    return t;
  }
  function maxStars() { return flatLessons().length * 3; }
  function doneCount() { return progress.done.length; }

  function isUnlocked(key) {
    var flat = flatLessons();
    for (var i = 0; i < flat.length; i++) {
      if (flat[i].key === key) {
        return i === 0 || isDone(flat[i - 1].key);
      }
    }
    return false;
  }

  function unitProgress(uid) {
    var u = unit(uid);
    if (!u) { return { done: 0, total: 0, stars: 0 }; }
    var d = 0, s = 0;
    u.classes.forEach(function (c) {
      if (isDone(c.key)) { d++; }
      s += starsOf(c.key);
    });
    return { done: d, total: u.classes.length, stars: s };
  }

  function levelProgress(lid) {
    var lv = level(lid);
    if (!lv) { return { done: 0, total: 0, stars: 0 }; }
    var d = 0, s = 0, t = 0;
    lv.units.forEach(function (u) {
      u.classes.forEach(function (c) {
        t++;
        if (isDone(c.key)) { d++; }
        s += starsOf(c.key);
      });
    });
    return { done: d, total: t, stars: s };
  }

  function finishLesson(key, stars) {
    if (progress.done.indexOf(key) === -1) { progress.done.push(key); }
    if (stars > starsOf(key)) { progress.stars[key] = stars; }
    touchStreak();
    save();
  }

  function touchStreak() {
    var hoy = new Date().toISOString().slice(0, 10);
    if (progress.lastDay === hoy) { return; }
    var ayer = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    progress.streak = (progress.lastDay === ayer) ? progress.streak + 1 : 1;
    progress.lastDay = hoy;
  }

  /** Devuelve la insignia recien ganada (o null). */
  function checkBadge(levelId) {
    var lp = levelProgress(levelId);
    if (lp.total > 0 && lp.done === lp.total && progress.badges.indexOf(levelId) === -1) {
      progress.badges.push(levelId);
      save();
      return level(levelId);
    }
    return null;
  }

  function hasBadge(levelId) { return progress.badges.indexOf(levelId) !== -1; }

  function reset() {
    progress = {
      stars: {}, done: [], badges: [], streak: 0, lastDay: "",
      settings: progress.settings
    };
    save();
  }

  /** Primera leccion no completada, para el boton "Continuar". */
  function nextLesson() {
    var flat = flatLessons();
    for (var i = 0; i < flat.length; i++) {
      if (!isDone(flat[i].key)) { return flat[i]; }
    }
    return null;
  }


  /* ---------------------------------------------- ilustraciones */
  /** Ya solo hay una tanda de ilustraciones: la ruta se devuelve tal cual. */
  function rutaImagen(src) {
    return src;
  }

  function tieneV2() {
    return false;
  }

  /** Se mantiene por compatibilidad: ya no hay dos juegos de ilustraciones. */
  function setImagenes(cual) {
    progress.settings.imagenes = "a";
    save();
    return progress.settings.imagenes;
  }


  /* ---------------------------------------------- memoria por palabra */
  function notaPalabra(en, bien) {
    if (!en) { return; }
    var k = String(en).toLowerCase();
    var m = progress.palabras[k] || { a: 0, f: 0, t: 0 };
    if (bien) { m.a++; } else { m.f++; }
    m.t = Date.now();
    progress.palabras[k] = m;
    save();
  }

  function notaDe(en) {
    return progress.palabras[String(en).toLowerCase()] || null;
  }

  /** Palabras ordenadas por necesidad de repaso: primero las falladas y las nunca vistas. */
  function palabrasPrioritarias(palabras, cuantas) {
    var lista = (palabras || []).slice();
    var ahora = Date.now();
    lista.sort(function (x, y) {
      var a = notaDe(x.en), b = notaDe(y.en);
      var pesoA = a ? (a.f * 3 - a.a) : 2;          // nunca vista = prioridad media-alta
      var pesoB = b ? (b.f * 3 - b.a) : 2;
      if (pesoA !== pesoB) { return pesoB - pesoA; }
      var tA = a ? a.t : 0, tB = b ? b.t : 0;        // las más olvidadas primero
      return tA - tB;
    });
    return lista.slice(0, cuantas || 10);
  }

  function nombre() { return (progress.settings.nombre || "").trim(); }

  function setNombre(valor) {
    progress.settings.nombre = String(valor || "").trim().slice(0, 20);
    save();
    return progress.settings.nombre;
  }

  global.Store = {
    load: load, save: save, raw: function () { return progress; },
    levels: levels, level: level, unit: unit, lesson: lesson, levelOfUnit: levelOfUnit,
    flatLessons: flatLessons, isDone: isDone, starsOf: starsOf, totalStars: totalStars,
    maxStars: maxStars, doneCount: doneCount, isUnlocked: isUnlocked,
    unitProgress: unitProgress, levelProgress: levelProgress, finishLesson: finishLesson,
    checkBadge: checkBadge, hasBadge: hasBadge, reset: reset, nextLesson: nextLesson,
    settings: function () { return progress.settings; },
    rutaImagen: rutaImagen, setImagenes: setImagenes, tieneV2: tieneV2,
    notaPalabra: notaPalabra, notaDe: notaDe, palabrasPrioritarias: palabrasPrioritarias,
    nombre: nombre, setNombre: setNombre
  };
})(window);
