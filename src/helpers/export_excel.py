import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

def export_to_excel(metadata, comments, platform, filename):
    os.makedirs(f"scrape/{platform}", exist_ok=True)
    filepath = os.path.join(f"scrape/{platform}", filename + ".xlsx")

    wb = Workbook()
    ws = wb.active

    # Headers de metadatos
    metadata_headers = list(metadata.keys())
    for col, header in enumerate(metadata_headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")

    # Valores de metadatos
    for col, header in enumerate(metadata_headers, 1):
        ws.cell(row=2, column=col, value=metadata.get(header, ""))

    # Dejar columnas 15 y 16 vacías
    start_col = 17

    # Headers de comentarios
    if comments:
        comment_headers = list(comments[0].keys())
        for col, header in enumerate(comment_headers, start_col):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        # Datos de comentarios
        for row_idx, comment in enumerate(comments, start=3):
            for col, header in enumerate(comment_headers, start_col):
                ws.cell(row=row_idx, column=col, value=comment.get(header, ""))

    wb.save(filepath)
    print(f"[OK] XLSX exportado: {filepath}")
    return filepath