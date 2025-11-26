import sys
import os
import re
import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# === Scrapfly API Key ===
# La clave API se lee desde el archivo .env por seguridad
SCRAPFLY_KEY = os.getenv('SCRAPFLY_API_KEY')

if not SCRAPFLY_KEY:
    SCRAPFLY_KEY = None  # Permitir None para Instagram con instagrapi
    print("⚠️ WARNING: No SCRAPFLY_API_KEY found (OK if using Instagram with credentials)")

def validate_links(links, platform):
    if len(links) > 10:
        print("Error: El máximo de links permitidos por ejecución es 10.")
        sys.exit(1)

    for link in links:
        if platform not in link.lower():
            print(f"Error: El link {link} no pertenece a {platform}.")
            sys.exit(1)

def format_date_for_filename():
    return datetime.datetime.now().strftime("%d-%m-%Y")