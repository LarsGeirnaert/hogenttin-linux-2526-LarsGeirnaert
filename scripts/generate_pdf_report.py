#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER

# --- Kleurdefinitie voor Modern Design ---
TEAL = colors.HexColor("#008080")
DARK_GREY = colors.HexColor("#333333")
LIGHT_GREY = colors.HexColor("#EEEEEE")


# --- Paden ---
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
weekday_file = base_dir / "reports/weekday_stats.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)
pdf_file = report_dir / "report.pdf"

# --- Data ---
df = pd.read_csv(data_file)
weekday_stats = pd.read_csv(weekday_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Bereken de numerieke uurwaarde (0.0 tot 24.0)
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60

# Algemene statistieken
mean_temp = df["temperature"].mean() if not df.empty else 0
mean_bikes = round(df["total_free_bikes"].mean()) if not df.empty else 0
day_data = df[(df["hour"] >= 7) & (df["hour"] < 19)]
day_avg_bikes = round(day_data["total_free_bikes"].mean()) if not day_data.empty else 0
night_data = df[(df["hour"] < 7) | (df["hour"] >= 19)]
night_avg_bikes = round(night_data["total_free_bikes"].mean()) if not night_data.empty else 0

# Correlaties
corr_temp_bikes = df["temperature"].corr(df["total_free_bikes"])
corr_temp_bikes = corr_temp_bikes if not pd.isna(corr_temp_bikes) else 0

corr_hour_bikes = df["hour"].corr(df["total_free_bikes"])
corr_hour_bikes = corr_hour_bikes if not pd.isna(corr_hour_bikes) else 0

# Nederlandse weekdagen
day_map = {
    "Monday": "Maandag", "Tuesday": "Dinsdag", "Wednesday": "Woensdag",
    "Thursday": "Donderdag", "Friday": "Vrijdag", "Saturday": "Zaterdag", "Sunday": "Zondag"
}
weekday_stats["weekday"] = weekday_stats["weekday"].map(day_map)

# --- PDF setup ---
doc = SimpleDocTemplate(str(pdf_file), pagesize=A4,
                        rightMargin=2*cm, leftMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=32, alignment=TA_CENTER, textColor=TEAL, spaceAfter=40)
header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontSize=20, textColor=DARK_GREY, spaceAfter=15)
normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=12, leading=16, textColor=DARK_GREY)

elements = []

# ---------- PAGINANUMMER FUNCTIE ----------
def add_page_number(canvas_obj, doc_obj):
    # Voorkom paginanummer op de titelpagina (pagina 1)
    if doc_obj.page == 1:
        return
        
    # Aftrekken van 1 zodat de inhoud begint bij Pagina 1 van de inhoud
    page_num_text = f"Pagina {doc_obj.page - 1}" 
    canvas_obj.setFont('Helvetica', 10)
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.drawRightString(A4[0]-2*cm, 1.5*cm, page_num_text)

# ---------- TITELPAGINA INHOUD (OPGESCHOOND) ----------
# Style voor gecentreerde tekst op de titelpagina
centered_style = ParagraphStyle(
    'CenteredTitle',
    parent=styles['Normal'],
    alignment=TA_CENTER,
    fontSize=20,
    textColor=DARK_GREY
)
    
# Grote titel in het midden van de pagina
elements.append(Spacer(1, 6*cm)) # Meer witruimte bovenaan
elements.append(Paragraph("DATA WORKFLOW RAPPORT", title_style))
elements.append(Paragraph("Temperatuur vs Aantal Vrije Fietsen in Gent", centered_style))
elements.append(Spacer(1, 8*cm)) # Grote centrale ruimte
    
# Naam en klas
elements.append(Paragraph(f"Opgesteld door:", centered_style))
elements.append(Spacer(1, 0.5*cm))
elements.append(Paragraph(f"**Lars Geirnaert**", ParagraphStyle('NameStyle', parent=centered_style, fontSize=24, textColor=TEAL)))
elements.append(Paragraph(f"Klas: 2E2", centered_style))
elements.append(Spacer(1, 4*cm))

# Datum is verwijderd voor een cleanere look
elements.append(PageBreak())

# ---------- STATISTIEKEN (START INHOUD) ----------
elements.append(Paragraph("📊 Statistische Samenvatting", header_style))
elements.append(Spacer(1, 12))
stats_table_data = [
    ["Statistiek", "Waarde"],
    ["Gemiddelde temperatuur (°C)", f"{mean_temp:.2f}"],
    ["Gemiddeld aantal vrije fietsen", f"{mean_bikes}"],
    ["Gemiddeld aantal fietsen overdag (07-19u)", f"{day_avg_bikes}"],
    ["Gemiddeld aantal fietsen ’s nachts (19-07u)", f"{night_avg_bikes}"],
    ["Correlatie temperatuur ↔ vrije fietsen", f"{corr_temp_bikes:.2f}"],
    ["Correlatie uur ↔ vrije fietsen", f"{corr_hour_bikes:.2f}"],
]
stats_table = Table(stats_table_data, colWidths=[10*cm, 6*cm])
stats_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), TEAL),
    ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
    ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ("ALIGN", (0,0), (0,-1), "LEFT"),
    ("ALIGN", (0,0), (-1,0), "CENTER"),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 11),
    ("INNERGRID", (0,0), (-1,-1), 0.25, DARK_GREY),
    ("BOX", (0,0), (-1,-1), 1, DARK_GREY)
]))
elements.append(stats_table)
elements.append(PageBreak())

# ---------- GRAFIEK 1 ----------
elements.append(Paragraph("📈 Grafiek 1: Temperatuur vs Vrije Fietsen", header_style))
elements.append(Spacer(1, 12))
graph_path_1 = report_dir / "fiets_vs_temp.png"
elements.append(Image(str(graph_path_1), width=16*cm, height=10*cm))
elements.append(PageBreak())

# ---------- GRAFIEK 2 ----------
elements.append(Paragraph("📊 Grafiek 2: Aantal Fietsen per Uur", header_style))
elements.append(Spacer(1, 12))
graph_path_2 = report_dir / "fiets_vs_uur.png"
elements.append(Image(str(graph_path_2), width=16*cm, height=10*cm))
elements.append(PageBreak())

# ---------- WEEKDAG TABEL ----------
elements.append(Paragraph("📅 Tabel: Vrije Fietsen per Weekdag", header_style))
elements.append(Spacer(1, 12))
table_data = [
    ["Weekdag", "Min", "Max", "Gem. Fietsen", "Gem. Temp (°C)"]
]
for _, row in weekday_stats.iterrows():
    table_data.append([
        row["weekday"] if pd.notna(row["weekday"]) else "",
        int(row["Min"]) if pd.notna(row["Min"]) else 0,
        int(row["Max"]) if pd.notna(row["Max"]) else 0,
        int(row["Gemiddelde_fietsen"]) if pd.notna(row["Gemiddelde_fietsen"]) else 0,
        round(row["Gemiddelde_temp"],2) if pd.notna(row["Gemiddelde_temp"]) else 0
    ])
weekday_table = Table(table_data, hAlign='CENTER', 
                      colWidths=[3.2*cm, 2.5*cm, 2.5*cm, 3.8*cm, 3.8*cm])
weekday_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), TEAL),
    ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
    ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ("ALIGN", (0,0), (-1,0), "CENTER"),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 10),
    ("INNERGRID", (0,0), (-1,-1), 0.25, DARK_GREY),
    ("BOX", (0,0), (-1,-1), 1, DARK_GREY)
]))
elements.append(weekday_table)

# ---------- BUILD PDF MET PAGINANUMMERS ----------
doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"✅ Professioneel PDF-rapport aangemaakt: {pdf_file}")