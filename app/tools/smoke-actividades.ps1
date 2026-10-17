# =============================================================================
#  smoke-actividades.ps1 — Comprueba que cada actividad pinta lo que debe.
#
#  Carga la vista previa de cada actividad en Chrome headless y verifica que
#  aparezcan los elementos interactivos (fichas, chips, tarjetas...). Sirve
#  para detectar errores de JavaScript que dejan la pantalla sin botones.
#
#  Uso:  pwsh -File app\tools\smoke-actividades.ps1
# =============================================================================
$ErrorActionPreference = "Stop"

$App   = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Prev  = "file:///" + ((Join-Path $App "tools\preview-actividad.html") -replace '\\', '/')
$Chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"

# actividad, clase de ejemplo, marcador CSS, mínimo esperado
$Casos = @(
    @{ act = "flashcards"; clase = "1.1.1"; marcador = "flash-card"; min = 1 },
    @{ act = "listen";     clase = "1.4.1"; marcador = "class=`"tile"; min = 4 },
    @{ act = "pairs";      clase = "1.4.1"; marcador = "class=`"tile"; min = 8 },
    @{ act = "sentence";   clase = "1.1.2"; marcador = "class=`"chip"; min = 2 },
    @{ act = "count";      clase = "1.2.3"; marcador = "class=`"tile"; min = 3 },
    @{ act = "quiz";       clase = "1.1.5"; marcador = "class=`"tile"; min = 3 }
)

$fallos = 0
foreach ($c in $Casos) {
    $prof = Join-Path $env:TEMP ("lk-smoke-" + [guid]::NewGuid().ToString("N"))
    $dom  = Join-Path $env:TEMP ("lk-dom-" + $c.act + ".txt")
    $url  = "$Prev`?t=$($c.act)&c=$($c.clase)"

    Start-Process -FilePath $Chrome -ArgumentList @(
        "--headless=new", "--disable-gpu", "--no-first-run",
        "--allow-file-access-from-files", "--user-data-dir=$prof",
        "--virtual-time-budget=6000", "--dump-dom", $url
    ) -NoNewWindow -Wait -RedirectStandardOutput $dom -RedirectStandardError "$env:TEMP\lk-smoke-err.txt" | Out-Null

    $html = Get-Content $dom -Raw
    $n = ([regex]::Matches($html, [regex]::Escape($c.marcador))).Count
    $err = [regex]::Match($html, '(?s)<pre id="err">(.*?)</pre>')
    $msg = if ($err.Success) { $err.Groups[1].Value } else { "" }

    if ($n -ge $c.min -and -not $msg) {
        "OK    {0,-11} clase {1,-6} {2} x{3}" -f $c.act, $c.clase, $c.marcador, $n
    } else {
        $fallos++
        "FALLO {0,-11} clase {1,-6} {2} x{3} (min {4}) {5}" -f $c.act, $c.clase, $c.marcador, $n, $c.min, $msg
    }
}

if ($fallos -eq 0) { "`nRESULTADO: las 6 actividades pintan sus controles" }
else { "`nRESULTADO: $fallos actividades con problemas" }
exit $fallos
