/* ==========================================================================
   memorama.js — Juegos de parejas (memorama) temáticos.

   Cada mazo es una lista de palabras con su emoji. Si la palabra tiene
   ilustración en el curso, se usa la ilustración en lugar del emoji.
   ========================================================================== */
(function (global) {
  "use strict";

  var MAZOS = {
    animales: {
      titulo: "Animals", emoji: "🦁", tono: "mz-animales",
      parejas: [
        { en: "lion", emoji: "🦁" }, { en: "tiger", emoji: "🐯" },
        { en: "elephant", emoji: "🐘" }, { en: "monkey", emoji: "🐵" },
        { en: "bear", emoji: "🐻" }, { en: "zebra", emoji: "🦓" }
      ]
    },
    frutas: {
      titulo: "Fruits", emoji: "🍎", tono: "mz-frutas",
      parejas: [
        { en: "apple", emoji: "🍎" }, { en: "banana", emoji: "🍌" },
        { en: "grapes", emoji: "🍇" }, { en: "strawberry", emoji: "🍓" },
        { en: "orange", emoji: "🍊" }, { en: "watermelon", emoji: "🍉" }
      ]
    },
    mar: {
      titulo: "Sea Animals", emoji: "🐬", tono: "mz-mar",
      parejas: [
        { en: "fish", emoji: "🐟" }, { en: "octopus", emoji: "🐙" },
        { en: "whale", emoji: "🐳" }, { en: "crab", emoji: "🦀" },
        { en: "dolphin", emoji: "🐬" }, { en: "shark", emoji: "🦈" }
      ]
    },
    colores: {
      titulo: "Colors", emoji: "🎨", tono: "mz-colores",
      parejas: [
        { en: "red", emoji: "🔴" }, { en: "blue", emoji: "🔵" },
        { en: "yellow", emoji: "🟡" }, { en: "green", emoji: "🟢" },
        { en: "orange", emoji: "🟠" }, { en: "purple", emoji: "🟣" }
      ]
    },
    numeros: {
      titulo: "Numbers", emoji: "🔢", tono: "mz-numeros",
      parejas: [
        { en: "one", emoji: "1️⃣" }, { en: "two", emoji: "2️⃣" },
        { en: "three", emoji: "3️⃣" }, { en: "four", emoji: "4️⃣" },
        { en: "five", emoji: "5️⃣" }, { en: "six", emoji: "6️⃣" }
      ]
    },
    cuerpo: {
      titulo: "Body", emoji: "👀", tono: "mz-cuerpo",
      parejas: [
        { en: "eyes", emoji: "👀" }, { en: "ears", emoji: "👂" },
        { en: "nose", emoji: "👃" }, { en: "mouth", emoji: "👄" },
        { en: "teeth", emoji: "🦷" }, { en: "hands", emoji: "🙌" }
      ]
    },
    ropa: {
      titulo: "Clothes", emoji: "👕", tono: "mz-ropa",
      parejas: [
        { en: "hat", emoji: "👒" }, { en: "jacket", emoji: "🧥" },
        { en: "shorts", emoji: "🩳" }, { en: "shoes", emoji: "👟" },
        { en: "socks", emoji: "🧦" }, { en: "dress", emoji: "👗" }
      ]
    },
    transporte: {
      titulo: "Transport", emoji: "🚌", tono: "mz-transporte",
      parejas: [
        { en: "bus", emoji: "🚌" }, { en: "car", emoji: "🚗" },
        { en: "plane", emoji: "✈️" }, { en: "boat", emoji: "⛵" },
        { en: "taxi", emoji: "🚕" }, { en: "underground", emoji: "🚇" }
      ]
    },
    escuela: {
      titulo: "School", emoji: "✏️", tono: "mz-escuela",
      parejas: [
        { en: "pencil", emoji: "✏️" }, { en: "pen", emoji: "🖊️" },
        { en: "book", emoji: "📕" }, { en: "notebook", emoji: "📒" },
        { en: "ruler", emoji: "📏" }, { en: "scissors", emoji: "✂️" }
      ]
    },
    emociones: {
      titulo: "Emotions", emoji: "😊", tono: "mz-emociones",
      parejas: [
        { en: "happy", emoji: "😄" }, { en: "sad", emoji: "😢" },
        { en: "angry", emoji: "😠" }, { en: "sleepy", emoji: "😴" },
        { en: "scared", emoji: "😨" }, { en: "love", emoji: "😍" }
      ]
    }
  };

  /** Busca la ilustración de una palabra: primero en el curso, luego en las extra. */
  function imagenDe(palabra) {
    var buscar = String(palabra).toLowerCase();
    var extra = global.LANGKIDS_IMG_MEMO || [];
    if (extra.indexOf(buscar) !== -1) { return "assets/img-memo/" + buscar + ".webp"; }
    var niveles = (global.Store && global.Store.levels) ? global.Store.levels() : [];
    for (var i = 0; i < niveles.length; i++) {
      for (var j = 0; j < niveles[i].units.length; j++) {
        var palabras = niveles[i].units[j].words;
        for (var k = 0; k < palabras.length; k++) {
          if (String(palabras[k].en).toLowerCase() === buscar && palabras[k].img) {
            return global.Store ? global.Store.rutaImagen(palabras[k].img) : palabras[k].img;
          }
        }
      }
    }
    return null;
  }

  function barajar(lista) {
    var a = lista.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /**
   * Monta un memorama dentro de `cont`.
   * Devuelve un objeto con el estado para las pruebas.
   */
  function montar(cont, idMazo, alGanar) {
    var mazo = MAZOS[idMazo];
    if (!mazo) { return null; }

    var cartas = [];
    mazo.parejas.forEach(function (p, i) {
      cartas.push({ par: i, palabra: p.en, emoji: p.emoji, img: imagenDe(p.en) });
      cartas.push({ par: i, palabra: p.en, emoji: p.emoji, img: imagenDe(p.en) });
    });
    cartas = barajar(cartas);

    var abiertas = [];
    var encontradas = 0;
    var intentos = 0;
    var bloqueado = false;
    var totalPares = mazo.parejas.length;

    cont.innerHTML = "";
    var panel = document.createElement("div");
    panel.className = "memo-panel " + mazo.tono;

    var marcador = document.createElement("div");
    marcador.className = "memo-marcador";
    marcador.innerHTML = "<span class='memo-pares'>0 / " + totalPares + "</span>" +
                         "<span class='memo-intentos'>0 moves</span>";
    panel.appendChild(marcador);

    var tablero = document.createElement("div");
    tablero.className = "memo-tablero";
    panel.appendChild(tablero);
    cont.appendChild(panel);

    var nodos = cartas.map(function (carta, i) {
      var b = document.createElement("button");
      b.className = "memo-carta";
      b.setAttribute("aria-label", "card " + (i + 1));
      b.dataset.par = String(carta.par);
      b.dataset.palabra = carta.palabra;

      var cara = document.createElement("div");
      cara.className = "memo-cara";
      if (carta.img) {
        var img = document.createElement("img");
        img.src = carta.img;
        img.alt = carta.palabra;
        cara.appendChild(img);
      } else {
        cara.textContent = carta.emoji;
      }
      b.appendChild(cara);

      b.onclick = function () { tocar(b, carta); };
      tablero.appendChild(b);
      return b;
    });

    function actualizarMarcador() {
      marcador.querySelector(".memo-pares").textContent = encontradas + " / " + totalPares;
      marcador.querySelector(".memo-intentos").textContent = intentos + " moves";
    }

    function tocar(nodo, carta) {
      if (bloqueado) { return; }
      if (nodo.classList.contains("abierta") || nodo.classList.contains("hecha")) { return; }

      nodo.classList.add("abierta");
      if (global.Audio && global.Audio.speak) { global.Audio.speak(carta.palabra); }
      abiertas.push({ nodo: nodo, carta: carta });

      if (abiertas.length < 2) { return; }

      intentos++;
      actualizarMarcador();
      var a = abiertas[0], b = abiertas[1];

      if (a.carta.par === b.carta.par) {
        a.nodo.classList.add("hecha");
        b.nodo.classList.add("hecha");
        if (global.Audio && global.Audio.ding) { global.Audio.ding(); }
        encontradas++;
        actualizarMarcador();
        abiertas = [];
        if (encontradas === totalPares) {
          setTimeout(function () {
            panel.classList.add("ganado");
            if (alGanar) { alGanar({ intentos: intentos, total: totalPares }); }
          }, 420);
        }
        return;
      }

      bloqueado = true;
      setTimeout(function () {
        a.nodo.classList.remove("abierta");
        b.nodo.classList.remove("abierta");
        abiertas = [];
        bloqueado = false;
      }, 760);
    }

    actualizarMarcador();

    return {
      _debug: function () { return { abiertas: abiertas.length, intentos: intentos, bloqueado: bloqueado }; },
      totalPares: totalPares,
      cartas: nodos,
      encontradas: function () { return encontradas; },
      intentos: function () { return intentos; }
    };
  }

  global.Memorama = { mazos: MAZOS, montar: montar, imagenDe: imagenDe };
})(window);
