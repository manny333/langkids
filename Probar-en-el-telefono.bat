@echo off
rem ============================================================
rem  Probar-en-el-telefono.bat
rem  Levanta un servidor local con la app y muestra la direccion
rem  que debes abrir en el navegador del telefono (misma wifi).
rem  Cierra esta ventana (o pulsa Ctrl+C) para detenerlo.
rem ============================================================
title LangKids English - servidor local
cd /d "%~dp0app\www"

echo.
echo   ============================================================
echo    LangKids English - servidor local en el puerto 8080
echo   ============================================================
echo.
echo   En el TELEFONO (conectado a la misma wifi) abre:
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=* delims= " %%b in ("%%a") do echo        http://%%b:8080
)

echo.
echo   En ESTA PC puedes abrir:  http://localhost:8080
echo.
echo   Pulsa Ctrl+C o cierra esta ventana para detener el servidor.
echo.

where python >nul 2>nul
if %errorlevel%==0 (
    python -m http.server 8080
) else (
    py -m http.server 8080
)

pause
