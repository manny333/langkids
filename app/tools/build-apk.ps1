# =============================================================================
#  build-apk.ps1 — Compila y firma el APK de LangKids English.
#
#  No usa Gradle: aprovecha las herramientas del SDK Android ya instaladas
#  (aapt2, d8, zipalign, apksigner) y el JDK para javac y keytool.
#
#  Uso:   pwsh -File app\tools\build-apk.ps1
# =============================================================================
$ErrorActionPreference = "Stop"

$App      = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)   # ...\app
$Android  = Join-Path $App "android"
$Www      = Join-Path $App "www"
$Build    = Join-Path $App "build"
$Dist     = Join-Path $App "dist"
$Sdk      = $env:ANDROID_HOME
if (-not $Sdk) { $Sdk = "$env:LOCALAPPDATA\Android\Sdk" }
$Jdk      = "C:\Program Files\Java\jdk-17"
$env:JAVA_HOME = $Jdk

$BuildTools = Join-Path $Sdk "build-tools\35.0.0"
$AndroidJar = Join-Path $Sdk "platforms\android-35\android.jar"
$Nombre     = "LangKids-English-1.0.apk"
$Paquete    = "com.langkids.english"

function Paso($n, $texto) { Write-Host "`n[$n] $texto" -ForegroundColor Cyan }
function Comprobar($cond, $msg) { if (-not $cond) { throw "FALTA: $msg" } }

Paso 1 "Comprobando herramientas"
foreach ($t in @("$BuildTools\aapt2.exe", "$BuildTools\d8.bat", "$BuildTools\zipalign.exe",
                 "$BuildTools\apksigner.bat", $AndroidJar, "$Jdk\bin\javac.exe",
                 "$Jdk\bin\keytool.exe")) {
    Comprobar (Test-Path $t) $t
}
Write-Host "   SDK: $Sdk"

Paso 2 "Preparando carpetas de trabajo"
if (Test-Path $Build) { Remove-Item $Build -Recurse -Force }
New-Item -ItemType Directory -Path "$Build\gen", "$Build\classes", "$Build\dex",
          "$Build\assets\www", $Dist -Force | Out-Null

# la app web se copia a assets/www (dentro del APK: assets/www/index.html)
Copy-Item "$Www\*" "$Build\assets\www" -Recurse -Force
$nArchivos = (Get-ChildItem "$Build\assets\www" -Recurse -File).Count
Write-Host "   app web copiada: $nArchivos archivos"

Paso 3 "Compilando recursos (aapt2 compile)"
& "$BuildTools\aapt2.exe" compile --dir "$Android\res" -o "$Build\res.zip"
Comprobar ($LASTEXITCODE -eq 0) "aapt2 compile"

Paso 4 "Enlazando recursos (aapt2 link)"
# No se usa -A: aapt2 en Windows escribe los assets con barras invertidas y
# Android no los encuentra. Los assets los empaqueta el paso 7 con pack_apk.py.
& "$BuildTools\aapt2.exe" link -o "$Build\base.apk" `
    -I $AndroidJar `
    --manifest "$Android\AndroidManifest.xml" `
    -R "$Build\res.zip" `
    --java "$Build\gen" `
    --min-sdk-version 24 --target-sdk-version 35 `
    --auto-add-overlay
Comprobar ($LASTEXITCODE -eq 0) "aapt2 link"

Paso 5 "Compilando Java (javac)"
$RJava = Get-ChildItem "$Build\gen" -Recurse -Filter "R.java" | Select-Object -First 1
Comprobar ($RJava) "R.java generado por aapt2"
$fuentes = @($RJava.FullName) + (Get-ChildItem "$Android\java" -Recurse -Filter "*.java" |
                                 Select-Object -ExpandProperty FullName)
& "$Jdk\bin\javac.exe" -encoding UTF-8 -nowarn -source 8 -target 8 `
    -bootclasspath $AndroidJar -classpath $AndroidJar `
    -d "$Build\classes" $fuentes 2>&1 | Where-Object { $_ -notmatch "bootstrap class path|source value 8|target value 8|deprecat" }
Comprobar ($LASTEXITCODE -eq 0) "javac"

Paso 6 "Generando classes.dex (d8)"
$clases = Get-ChildItem "$Build\classes" -Recurse -Filter "*.class" |
          Select-Object -ExpandProperty FullName
Comprobar ($clases.Count -gt 0) "clases compiladas"
& "$BuildTools\d8.bat" --lib $AndroidJar --min-api 24 --output "$Build\dex" $clases
Comprobar (Test-Path "$Build\dex\classes.dex") "classes.dex"

Paso 7 "Empaquetando assets/www y classes.dex con rutas POSIX"
$Python = "C:\Users\EMMAN\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }
& $Python "$PSScriptRoot\pack_apk.py" "$Build\base.apk" "$Build\assets" `
    "$Build\dex\classes.dex" "$Build\packed.apk"
Comprobar ($LASTEXITCODE -eq 0) "pack_apk.py"
Write-Host "   APK sin firmar: $([math]::Round((Get-Item "$Build\packed.apk").Length/1KB,1)) KB"

Paso 8 "Alineando (zipalign)"
& "$BuildTools\zipalign.exe" -f -p 4 "$Build\packed.apk" "$Build\aligned.apk"
Comprobar ($LASTEXITCODE -eq 0) "zipalign"

Paso 9 "Firmando (apksigner)"
$keystore = Join-Path $App "keystore\langkids-debug.jks"
if (-not (Test-Path $keystore)) {
    New-Item -ItemType Directory -Path (Split-Path $keystore) -Force | Out-Null
    Write-Host "   creando keystore de depuracion…"
    & "$Jdk\bin\keytool.exe" -genkeypair -v -keystore $keystore `
        -storepass langkids -keypass langkids -alias langkids `
        -keyalg RSA -keysize 2048 -validity 10000 `
        -dname "CN=LangKids English, O=LangKids, L=Lima, C=PE" | Out-Null
}
$salida = Join-Path $Dist $Nombre
& "$BuildTools\apksigner.bat" sign --ks $keystore --ks-pass pass:langkids `
    --key-pass pass:langkids --ks-key-alias langkids `
    --v1-signing-enabled true --v2-signing-enabled true `
    --out $salida "$Build\aligned.apk"
Comprobar ($LASTEXITCODE -eq 0) "apksigner sign"

Paso 10 "Verificando el APK"
& "$BuildTools\apksigner.bat" verify --print-certs $salida | Select-Object -First 6
$badging = & "$BuildTools\aapt2.exe" dump badging $salida
$badging | Select-String -Pattern "^package|^application-label|^sdkVersion|^targetSdkVersion|^launchable-activity|^application-icon-320" | ForEach-Object { "   " + $_.Line }

$mb = [math]::Round((Get-Item $salida).Length / 1MB, 2)
Write-Host "`nLISTO: $salida ($mb MB)" -ForegroundColor Green
Write-Host "Instalar en un telefono conectado por USB:  adb install -r `"$salida`"" -ForegroundColor Green
