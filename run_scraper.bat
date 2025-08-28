@echo off
title Social Media Scraper
color 0a

echo =======================================
echo      INSTAGRAM SCRAPER
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