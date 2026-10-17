package com.langkids.english;

import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.speech.tts.TextToSpeech;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.TextView;

import java.util.Locale;

/**
 * LangKids English — contenedor Android de la app interactiva.
 *
 * La interfaz vive en assets/www (HTML+CSS+JS). Este Activity aporta lo que la
 * web no puede hacer sola: voz del sistema (TextToSpeech), vibracion y guardado
 * permanente del progreso. No usa red ni librerias externas.
 */
public class MainActivity extends Activity {

    private static final String PREFS = "langkids";
    private static final String CLAVE_PROGRESO = "progress";

    private WebView web;
    private TextToSpeech tts;
    private volatile boolean ttsListo = false;
    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle estado) {
        super.onCreate(estado);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);

        FrameLayout raiz = new FrameLayout(this);
        raiz.setBackgroundColor(0xFFF4F9FB);

        try {
            web = new WebView(this);
            WebSettings s = web.getSettings();
            s.setJavaScriptEnabled(true);
            s.setDomStorageEnabled(true);
            s.setAllowFileAccess(true);
            s.setMediaPlaybackRequiresUserGesture(false);
            s.setSupportZoom(false);
            s.setBuiltInZoomControls(false);
            s.setTextZoom(100); // respeta el escalado del sistema sin romper el diseno
            web.setWebViewClient(new WebViewClient());
            web.setBackgroundColor(0xFFF4F9FB);
            web.setOverScrollMode(View.OVER_SCROLL_NEVER);
            web.setLongClickable(false);
            web.setHapticFeedbackEnabled(false);
            web.addJavascriptInterface(new Puente(), "Android");
            raiz.addView(web, new FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
            try {
                web.loadUrl("file:///android_asset/www/index.html");
                android.util.Log.i("LangKids", "cargando assets/www/index.html");
            } catch (Throwable t) {
                android.util.Log.e("LangKids", "no se pudo cargar la app web: " + t);
            }
            web.loadUrl("file:///android_asset/www/index.html");
        } catch (Throwable t) {
            TextView aviso = new TextView(this);
            aviso.setText("No se pudo abrir la app en este dispositivo.\n\n" + t.getMessage());
            aviso.setPadding(40, 80, 40, 40);
            raiz.addView(aviso);
        }

        setContentView(raiz);
        iniciarVoz();
    }

    private void iniciarVoz() {
        try {
            tts = new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
                @Override
                public void onInit(int estado) {
                    if (estado != TextToSpeech.SUCCESS || tts == null) {
                        ttsListo = false;
                        return;
                    }
                    int r = tts.setLanguage(Locale.US);
                    ttsListo = (r != TextToSpeech.LANG_MISSING_DATA
                            && r != TextToSpeech.LANG_NOT_SUPPORTED);
                    if (ttsListo) {
                        tts.setSpeechRate(0.85f);
                        tts.setPitch(1.05f);
                    }
                }
            });
        } catch (Throwable t) {
            ttsListo = false;
        }
    }

    /* ------------------------------------------------------------------ puente JS */
    private class Puente {

        @JavascriptInterface
        public boolean isAndroid() {
            return true;
        }

        /** true si hay un motor de voz en ingles disponible en el dispositivo. */
        @JavascriptInterface
        public boolean hasVoice() {
            return ttsListo;
        }

        @JavascriptInterface
        public void speak(final String texto, final double velocidad) {
            if (texto == null || texto.length() == 0) {
                return;
            }
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (tts == null || !ttsListo) {
                        return;
                    }
                    try {
                        tts.setSpeechRate((float) velocidad);
                        if (Build.VERSION.SDK_INT >= 21) {
                            tts.speak(texto, TextToSpeech.QUEUE_FLUSH, null, "langkids");
                        } else {
                            tts.speak(texto, TextToSpeech.QUEUE_FLUSH, null);
                        }
                    } catch (Throwable ignored) { }
                }
            });
        }

        @JavascriptInterface
        public void stopSpeak() {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (tts != null) {
                        try { tts.stop(); } catch (Throwable ignored) { }
                    }
                }
            });
        }

        @JavascriptInterface
        public void vibrate(final int ms) {
            try {
                Vibrator v = (Vibrator) getSystemService(VIBRATOR_SERVICE);
                if (v == null || !v.hasVibrator()) {
                    return;
                }
                if (Build.VERSION.SDK_INT >= 26) {
                    v.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE));
                } else {
                    v.vibrate(ms);
                }
            } catch (Throwable ignored) { }
        }

        @JavascriptInterface
        public void saveProgress(String json) {
            if (json == null) {
                return;
            }
            prefs.edit().putString(CLAVE_PROGRESO, json).apply();
        }

        @JavascriptInterface
        public String loadProgress() {
            return prefs.getString(CLAVE_PROGRESO, null);
        }
    }

    /* ------------------------------------------------------------------ navegacion */
    @Override
    public void onBackPressed() {
        if (web == null) {
            super.onBackPressed();
            return;
        }
        web.evaluateJavascript("(window.AppBack ? window.AppBack() : false)", new ValueCallback<String>() {
            @Override
            public void onReceiveValue(String valor) {
                if (!"true".equals(valor)) {
                    finish();
                }
            }
        });
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (tts != null) {
            try { tts.stop(); } catch (Throwable ignored) { }
        }
    }


    /* ------------------------- dibujos de los niños ------------------------- */

    /** Carpeta interna donde se guardan los dibujos (no necesita permisos). */
    private java.io.File carpetaDibujos() {
        java.io.File d = new java.io.File(getFilesDir(), "dibujos");
        if (!d.exists()) { d.mkdirs(); }
        return d;
    }

    private static String limpio(String id) {
        if (id == null) { return ""; }
        return id.replaceAll("[^A-Za-z0-9_-]", "");
    }

    /** Guarda un dibujo en PNG (base64 sin el prefijo data:). */
    @JavascriptInterface
    public boolean saveDrawing(String id, String base64) {
        try {
            String nombre = limpio(id);
            if (nombre.length() == 0 || base64 == null) { return false; }
            byte[] datos = android.util.Base64.decode(base64, android.util.Base64.DEFAULT);
            java.io.File f = new java.io.File(carpetaDibujos(), nombre + ".png");
            java.io.FileOutputStream salida = new java.io.FileOutputStream(f);
            salida.write(datos);
            salida.close();
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    /** Lista de dibujos, del más nuevo al más viejo, en JSON. */
    @JavascriptInterface
    public String listDrawings() {
        try {
            java.io.File[] archivos = carpetaDibujos().listFiles();
            java.util.List<java.io.File> lista = new java.util.ArrayList<java.io.File>();
            if (archivos != null) {
                for (java.io.File f : archivos) {
                    if (f.getName().endsWith(".png")) { lista.add(f); }
                }
            }
            java.util.Collections.sort(lista, new java.util.Comparator<java.io.File>() {
                @Override
                public int compare(java.io.File a, java.io.File b) {
                    return Long.compare(b.lastModified(), a.lastModified());
                }
            });
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < lista.size(); i++) {
                java.io.File f = lista.get(i);
                if (i > 0) { sb.append(','); }
                sb.append("{\"id\":\"").append(limpio(f.getName().replace(".png", "")))
                  .append("\",\"ts\":").append(f.lastModified())
                  .append(",\"bytes\":").append(f.length()).append('}');
            }
            return sb.append(']').toString();
        } catch (Throwable t) {
            return "[]";
        }
    }

    /** Devuelve el dibujo en base64 (sin cabecera data:) o cadena vacía. */
    @JavascriptInterface
    public String loadDrawing(String id) {
        try {
            java.io.File f = new java.io.File(carpetaDibujos(), limpio(id) + ".png");
            if (!f.exists()) { return ""; }
            java.io.FileInputStream in = new java.io.FileInputStream(f);
            java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) { out.write(buf, 0, n); }
            in.close();
            return android.util.Base64.encodeToString(out.toByteArray(), android.util.Base64.NO_WRAP);
        } catch (Throwable t) {
            return "";
        }
    }

    @JavascriptInterface
    public boolean deleteDrawing(String id) {
        try {
            java.io.File f = new java.io.File(carpetaDibujos(), limpio(id) + ".png");
            return f.exists() && f.delete();
        } catch (Throwable t) {
            return false;
        }
    }

    /** Copia el dibujo a la galería del teléfono (Álbum LangKids). Android 10+. */
    @JavascriptInterface
    public boolean exportDrawing(String id) {
        if (Build.VERSION.SDK_INT < 29) { return false; }
        try {
            java.io.File f = new java.io.File(carpetaDibujos(), limpio(id) + ".png");
            if (!f.exists()) { return false; }
            android.content.ContentValues cv = new android.content.ContentValues();
            cv.put(android.provider.MediaStore.Images.Media.DISPLAY_NAME, "langkids-" + limpio(id) + ".png");
            cv.put(android.provider.MediaStore.Images.Media.MIME_TYPE, "image/png");
            cv.put(android.provider.MediaStore.Images.Media.RELATIVE_PATH,
                   android.os.Environment.DIRECTORY_PICTURES + "/LangKids");
            android.net.Uri destino = getContentResolver().insert(
                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI, cv);
            if (destino == null) { return false; }
            java.io.FileInputStream in = new java.io.FileInputStream(f);
            java.io.OutputStream out = getContentResolver().openOutputStream(destino);
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) { out.write(buf, 0, n); }
            in.close();
            out.close();
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    @Override
    protected void onDestroy() {
        if (tts != null) {
            try {
                tts.stop();
                tts.shutdown();
            } catch (Throwable ignored) { }
            tts = null;
        }
        if (web != null) {
            try {
                web.removeJavascriptInterface("Android");
                web.destroy();
            } catch (Throwable ignored) { }
            web = null;
        }
        super.onDestroy();
    }
}
