/* =========================================================================
   audio.js — voz (TextToSpeech nativo o del navegador) y efectos de sonido.
   Todo funciona sin internet.
   ========================================================================= */
(function (global) {
  "use strict";

  var ctxAudio = null;
  var vozLista = false;
  var vozElegida = null;
  var avisoMostrado = false;

  /* ------------------------------------------------------------- puente nativo */
  function nativo() {
    return (global.Android && typeof global.Android.speak === "function") ? global.Android : null;
  }

  /* ------------------------------------------------------------- voz del navegador */
  function prepararVoces() {
    if (!global.speechSynthesis) { return; }
    var voces = global.speechSynthesis.getVoices() || [];
    for (var i = 0; i < voces.length; i++) {
      var v = voces[i];
      if (/^en(-|_)?/i.test(v.lang)) {
        vozElegida = v;
        vozLista = true;
        if (/en-US|en_US/i.test(v.lang)) { break; }   // preferimos ingles americano
      }
    }
    if (!vozLista && voces.length) { vozLista = true; }  // al menos algo se oira
  }

  if (global.speechSynthesis) {
    prepararVoces();
    global.speechSynthesis.onvoiceschanged = prepararVoces;
  }

  function vozDisponible() {
    if (nativo()) { return true; }
    return !!(global.speechSynthesis && global.speechSynthesis.getVoices &&
              global.speechSynthesis.getVoices().length > 0);
  }

  /* ------------------------------------------------------------- hablar */
  function speak(texto, opciones) {
    if (!texto) { return; }
    var s = global.Store ? global.Store.settings() : { voice: true, rate: 0.85 };
    if (!s.voice) { return; }
    var rate = (opciones && opciones.rate) || s.rate || 0.85;

    var b = nativo();
    if (b) {
      try { b.speak(String(texto), Number(rate)); return; } catch (e) { /* sigue abajo */ }
    }
    if (!global.speechSynthesis) { avisoVoz(); return; }
    try {
      global.speechSynthesis.cancel();
      var u = new global.SpeechSynthesisUtterance(String(texto));
      u.lang = "en-US";
      u.rate = rate;
      u.pitch = 1.05;
      if (vozElegida) { u.voice = vozElegida; }
      global.speechSynthesis.speak(u);
    } catch (e) { avisoVoz(); }
  }

  function stop() {
    var b = nativo();
    if (b && typeof b.stopSpeak === "function") { try { b.stopSpeak(); } catch (e) {} }
    if (global.speechSynthesis) { try { global.speechSynthesis.cancel(); } catch (e) {} }
  }

  function avisoVoz() {
    if (avisoMostrado) { return; }
    avisoMostrado = true;
    if (global.UI && global.UI.toast) {
      global.UI.toast("Este dispositivo no tiene voz en inglés instalada");
    }
  }

  /* ------------------------------------------------------------- efectos */
  function ac() {
    if (!ctxAudio) {
      var AC = global.AudioContext || global.webkitAudioContext;
      if (!AC) { return null; }
      try { ctxAudio = new AC(); } catch (e) { return null; }
    }
    if (ctxAudio.state === "suspended") { try { ctxAudio.resume(); } catch (e) {} }
    return ctxAudio;
  }

  function tono(freq, inicio, dur, tipo, vol) {
    var a = ac();
    if (!a) { return; }
    var o = a.createOscillator();
    var g = a.createGain();
    o.type = tipo || "sine";
    o.frequency.value = freq;
    g.gain.setValueAtTime(0, a.currentTime + inicio);
    g.gain.linearRampToValueAtTime(vol || 0.18, a.currentTime + inicio + 0.02);
    g.gain.exponentialRampToValueAtTime(0.001, a.currentTime + inicio + dur);
    o.connect(g); g.connect(a.destination);
    o.start(a.currentTime + inicio);
    o.stop(a.currentTime + inicio + dur + 0.05);
  }

  function ding() { tono(880, 0, 0.16, "sine", 0.2); tono(1320, 0.09, 0.18, "sine", 0.15); }
  function buzz() { tono(200, 0, 0.22, "square", 0.12); }
  function tada() {
    tono(660, 0, 0.14); tono(880, 0.12, 0.14); tono(1100, 0.24, 0.28);
  }
  function clic() { tono(520, 0, 0.06, "triangle", 0.1); }

  /* ------------------------------------------------------------- vibracion */
  function vibrate(ms) {
    var s = global.Store ? global.Store.settings() : { vibrate: true };
    if (!s.vibrate) { return; }
    var b = nativo();
    if (b && typeof b.vibrate === "function") { try { b.vibrate(ms || 30); return; } catch (e) {} }
    if (global.navigator && global.navigator.vibrate) { try { global.navigator.vibrate(ms || 30); } catch (e) {} }
  }

  function desbloquear() { ac(); }   // se llama en el primer toque del usuario

  global.Audio = {
    speak: speak, stop: stop, ding: ding, buzz: buzz, tada: tada, clic: clic,
    vibrate: vibrate, desbloquear: desbloquear, vozDisponible: vozDisponible
  };
})(window);
