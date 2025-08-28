import sys
import os
import json
import requests
from datetime import datetime
from helpers.export_excel import export_to_excel
from helpers.export_csv import export_to_csv
from helpers.common import validate_links, format_date_for_filename, SCRAPFLY_KEY
from scrapfly import ScrapflyClient, ScrapeConfig

client = ScrapflyClient(key=SCRAPFLY_KEY)

SCRAPFLY_API = "https://api.scrapfly.io/scrape"

def scrape_instagram_video(url):
    """Scrapea datos de un post de Instagram con Scrapfly"""
    payload = {
        "key": SCRAPFLY_KEY,
        "url": url,
        "render_js": True, # Renderizado para cargar likes/comentarios
        "asp": True
    }
    resp = requests.post(SCRAPFLY_API, json=payload)
    data = resp.json()

    if "result" not in data:
        print(f"Error al scrapear {url}: {data}")
        return None

    html = data["result"]["content"]

    # ⚠️ Instagram cambia mucho el DOM → aquí se hace parsing básico
    # Puedes afinar selectores según el HTML real
    post_info = {
        "post_url": url,
        "publisher_nickname": "desconocido",
        "publisher_handle": "desconocido",
        "publisher_url": "",
        "publish_time": str(datetime.now()),
        "post_likes": 0,
        "post_shares": 0,
        "description": "",
        "num_comments_lvl1": 0,
        "num_comments_lvl2": 0,
        "total_comments_actual": 0,
        "total_comments_platform": 0,
        "difference": 0,
        "comments": []
    }

    # 👉 Aquí deberías usar BeautifulSoup o regex para extraer los datos
    # likes, comentarios, usuario, etc.
    # Ejemplo placeholder:
    post_info["post_likes"] = html.count("like")  # simplificado
    post_info["description"] = "Descripción simulada"

    # Simulación de comentarios
    comments = []
    for i in range(3):
        comments.append({
            "comment_number": i+1,
            "nickname": f"user{i}",
            "user_handle": f"@user{i}",
            "user_url": f"https://instagram.com/user{i}",
            "comment_text": f"Comentario {i}",
            "time": str(datetime.now()),
            "likes": i*2,
            "profile_pic_url": "",
            "followers": 100+i,
            "is_2nd_level": False,
            "user_replied_to": "",
            "num_replies": 0
        })
    post_info["comments"] = comments
    post_info["total_comments_actual"] = len(comments)

    return post_info


def main():
    print("=== Instagram Scraper ===")
    num_videos = int(input("¿Cuántos links quieres scrapear? (máx 10): "))
    links = [input(f"Link {i+1}: ") for i in range(num_videos)]
    validate_links(links, "instagram")

    export_format = input("Formato de salida (csv/xlsx): ").lower()

    all_data = []
    for link in links:
        print(f"Scrapeando {link} ...")
        data = scrape_instagram_video(link)
        if data:
            all_data.append(data)

    if not all_data:
        print("No se pudo scrapear nada.")
        return

    date_str = format_date_for_filename()
    outdir = os.path.join("scrape", "instagram")
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f"video_{date_str}.{export_format}")

    if export_format == "xlsx":
        export_to_excel(all_data, outfile)
    else:
        export_to_csv(all_data, outfile)

    print(f"✅ Datos exportados en {outfile}")


if __name__ == "__main__":
    main()