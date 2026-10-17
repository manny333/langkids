@echo off
setlocal
chcp 65001 >nul
title LangKids - instalar en la tablet

rem ---------------------------------------------------------------------------
rem  Instala el APK en la tablet por USB con adb.
rem  Este metodo NO necesita activar "instalar apps de origen desconocido",
rem  asi que funciona aunque la tablet este supervisada con Family Link.
rem ---------------------------------------------------------------------------

set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
set "APK=%~dp0app\dist\LangKids-English-1.0.apk"

echo.
echo  ============================================
echo   LangKids - instalacion en la tablet
echo  ============================================
echo.

if not exist "%ADB%" (
  echo  [X] No encuentro adb en:
  echo      %ADB%
  echo      Instala las "Android SDK Platform-Tools" o usa el metodo de
  echo      detener la supervision temporalmente.
  pause
  exit /b 1
)

if not exist "%APK%" (
  echo  [X] No encuentro el APK en:
  echo      %APK%
  echo      Genera el APK con:  pwsh -File app\tools\build-apk.ps1
  pause
  exit /b 1
)

echo  1) En la tablet:
echo     - Ajustes ^> Informacion del telefono ^> toca "Numero de compilacion" 7 veces
echo     - Ajustes ^> Sistema ^> Opciones de desarrollador ^> Depuracion USB: ACTIVADA
echo  2) Conecta la tablet al PC con el cable USB
echo  3) Acepta el aviso "Permitir depuracion USB" en la tablet
echo.
pause

echo.
echo  Buscando la tablet...
"%ADB%" devices
echo.

"%ADB%" devices | findstr /r /c:"device$" >nul
if errorlevel 1 (
  echo  [X] No hay ninguna tablet conectada o no has aceptado el aviso.
  echo      Desconecta y vuelve a conectar el cable, y acepta el dialogo.
  pause
  exit /b 1
)

echo  Instalando LangKids...
"%ADB%" install -r "%APK%"
if errorlevel 1 (
  echo.
  echo  [X] No se pudo instalar. Prueba:
  echo      - desenchufar y volver a enchufar el cable
  echo      - en la tablet, revocar y volver a aceptar la depuracion USB
  echo      - si sigue igual, usa el metodo de detener la supervision
  pause
  exit /b 1
)

echo.
echo  [!] Listo. Busca "LangKids" en el cajon de aplicaciones.
echo.
pause
