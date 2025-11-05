@echo off
title Social Media Scraper
color 0a
setlocal enabledelayedexpansion

echo =======================================
echo      INSTAGRAM SCRAPER
echo =======================================
echo.

REM Check if Python is installed
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)

REM Check if pip is installed
echo Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no esta disponible.
    echo Instalando pip...
    python -m ensurepip --upgrade
)

REM Check and install required packages
echo Verificando paquetes necesarios...
echo.

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo ERROR: requirements.txt no encontrado.
    pause
    exit /b 1
)

REM Read requirements.txt and check each package
for /f "usebackq tokens=1 delims=>=" %%p in ("requirements.txt") do (
    set "package_name=%%p"
    echo Verificando !package_name!...
    python -m pip show "!package_name!" >nul 2>&1
    if errorlevel 1 (
        echo   [!] !package_name! no esta instalado. Instalando...
        python -m pip install "!package_name!" >nul 2>&1
        if errorlevel 1 (
            echo   [ERROR] No se pudo instalar !package_name!
        ) else (
            echo   [OK] !package_name! instalado correctamente
        )
    ) else (
        echo   [OK] !package_name! ya esta instalado
    )
)

echo.
echo Verificacion completada.
echo =======================================
echo.

echo 1. Instagram
echo 0. Salir
echo.

set /p choice="Selecciona una opcion (0-1): "

if "%choice%"=="0" exit
if "%choice%"=="1" set platform=instagram

echo.
set /p count="Cuantos videos deseas scrapear? (max 10): "

if %count% GTR 10 (
    echo Error: Solo puedes ingresar hasta 10 videos por ejecucion.
    exit /b
)

echo.
echo Ingresa los %count% links de Instagram:
set links=

for /l %%i in (1,1,%count%) do (
    set /p link="Link %%i: "
    set links=!links! %%link%%
)

echo.
echo Selecciona formato de salida:
echo 1. CSV
echo 2. XLSX
set /p format="Formato (1 o 2): "

if "%format%"=="1" set output_format=csv
if "%format%"=="2" set output_format=xlsx

echo.
echo =======================================
echo Iniciando scraping en Instagram...
echo =======================================
echo.

REM Llamar al script Python correspondiente
python src\scraper_%platform%.py --links %links% --format %output_format%

pause