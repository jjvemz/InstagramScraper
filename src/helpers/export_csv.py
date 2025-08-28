import csv
import os

def export_to_csv(metadata, comments, platform, filename):
    os.makedirs(f"scrape/{platform}", exist_ok=True)
    filepath = os.path.join(f"scrape/{platform}", filename + ".csv")

    with open(filepath, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        # Escribir metadatos
        metadata_headers = list(metadata.keys())
        writer.writerow(metadata_headers)
        writer.writerow([metadata.get(k, "") for k in metadata_headers])

        # Separador
        writer.writerow([])

        # Escribir comentarios
        if comments:
            comment_headers = list(comments[0].keys())
            writer.writerow(comment_headers)
            for c in comments:
                writer.writerow([c.get(k, "") for k in comment_headers])

    print(f"[OK] CSV exportado: {filepath}")
    return filepath