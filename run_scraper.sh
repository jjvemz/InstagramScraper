#!/bin/bash

# Set terminal title
echo -ne "\033]0;Social Media Scraper\007"

# Clear screen and set colors
clear
echo -e "\033[92m"  # Green color

echo "======================================="
echo "      INSTAGRAM SCRAPER"
echo "======================================="
echo ""
echo "1. Instagram"
echo "0. Salir"
echo ""

read -p "Selecciona una opcion (0-1): " choice

if [ "$choice" = "0" ]; then
    exit 0
fi

if [ "$choice" = "1" ]; then
    platform="instagram"
fi

echo ""
read -p "Cuantos videos deseas scrapear? (max 10): " count

# Validate input is a number and within range
if ! [[ "$count" =~ ^[0-9]+$ ]] || [ "$count" -gt 10 ] || [ "$count" -lt 1 ]; then
    echo "Error: Solo puedes ingresar hasta 10 videos por ejecucion."
    exit 1
fi

echo ""
echo "Ingresa los $count links de Instagram:"
links=""

for ((i=1; i<=count; i++)); do
    read -p "Link $i: " link
    links="$links $link"
done

echo ""
echo "Selecciona formato de salida:"
echo "1. CSV"
echo "2. XLSX"
read -p "Formato (1 o 2): " format

if [ "$format" = "1" ]; then
    output_format="csv"
elif [ "$format" = "2" ]; then
    output_format="xlsx"
else
    echo "Formato invalido. Usando CSV por defecto."
    output_format="csv"
fi

echo ""
echo "======================================="
echo "Iniciando scraping en Instagram..."
echo "======================================="
echo ""

# Call the Python script
python3 "src/scraper_${platform}.py" --links $links --format "$output_format"

# Wait for user input before closing (equivalent to pause)
read -p "Presiona Enter para continuar..."