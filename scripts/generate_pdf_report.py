#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER

# --- Kleurdefinitie voor Modern Design ---
TEAL = colors.HexColor("#008080")
DARK_GREY = colors.HexColor("#333333")
LIGHT_GREY = colors.HexColor("#F2F2F2")

# --- Paden ---
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
weekday_file = base_dir / "reports/weekday_stats.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)
pdf_file = report_dir / "report.pdf"

# --- Data Inlezen & Verwerken ---
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

# --- PDF Setup ---
doc = SimpleDocTemplate(str(pdf_file), pagesize=A4,
                        rightMargin=2*cm, leftMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

styles = getSampleStyleSheet()

# --- Custom Styles ---
# Titelblad styles
title_main_style = ParagraphStyle('MainTitle', parent=styles['Title'], fontSize=34, leading=42, alignment=TA_CENTER, textColor=TEAL, spaceAfter=20)
title_sub_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=18, leading=24, alignment=TA_CENTER, textColor=DARK_GREY)

# Auteur blok styles
label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=12, leading=14, alignment=TA_CENTER, textColor=colors.grey)
# HIER OPGELOST: fontName='Helvetica-Bold' zorgt voor vetgedrukt zonder sterretjes **
name_style = ParagraphStyle('Name', parent=styles['Normal'], fontSize=26, leading=32, alignment=TA_CENTER, textColor=DARK_GREY, fontName='Helvetica-Bold')
class_style = ParagraphStyle('Class', parent=styles['Normal'], fontSize=16, leading=20, alignment=TA_CENTER, textColor=TEAL)
date_style = ParagraphStyle('Date', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=colors.grey)

# Content styles
header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontSize=20, textColor=DARK_GREY, spaceAfter=15, spaceBefore=20)

elements = []

# ---------- PAGINANUMMER FUNCTIE ----------
def add_page_number(canvas_obj, doc_obj):
    if doc_obj.page == 1:
        return
    page_num_text = f"Pagina {doc_obj.page - 1}" 
    canvas_obj.setFont('Helvetica', 10)
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.drawRightString(A4[0]-2*cm, 1.5*cm, page_num_text)

# ---------- TITELPAGINA (FIXED) ----------
def create_title_page():
    # 1. Ruimte bovenaan
    elements.append(Spacer(1, 6*cm))
    
    # 2. Hoofdtitel & Subtitel
    elements.append(Paragraph("DATA WORKFLOW RAPPORT", title_main_style))
    elements.append(Paragraph("Temperatuur vs Aantal Vrije Fietsen in Gent", title_sub_style))
    
    # 3. Visuele scheiding
    elements.append(Spacer(1, 5*cm))
    
    # 4. Auteur Blok in een TABEL
    # Tabelstructuur voorkomt overlap. Elke tekst zit in zijn eigen 'cel'.
    author_data = [
        [Paragraph("Opgesteld door:", label_style)],
        [Paragraph("Lars Geirnaert", name_style)],  # Geen sterretjes, stijl doet het werk
        [Paragraph("Klas: 2E2", class_style)]
    ]
    
    author_table = Table(author_data, colWidths=[14*cm])
    
    # HIER OPGELOST: BOTTOMPADDING zorgt voor witruimte tussen de regels
    author_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12), # 12pt ruimte onder "Opgesteld door"
        ('BOTTOMPADDING', (0,1), (-1,1), 12), # 12pt ruimte onder Naam
    ]))
    elements.append(author_table)
    
    # 5. Datum onderaan (via Spacer naar beneden duwen)
    elements.append(Spacer(1, 3*cm))
    elements.append(Paragraph(f"Gegenereerd op: {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')}", date_style))
    
    elements.append(PageBreak())

# Voeg titelpagina toe
create_title_page()

# ---------- START INHOUD (Pagina 2) ----------

# Statistieken
elements.append(Paragraph("📊 Statistische Samenvatting", header_style))
elements.append(Spacer(1, 10))

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
    ("BOX", (0,0), (-1,-1), 1, DARK_GREY),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, LIGHT_GREY])
]))
elements.append(stats_table)
elements.append(PageBreak())

# Grafiek 1
elements.append(Paragraph("📈 Grafiek 1: Temperatuur vs Vrije Fietsen", header_style))
elements.append(Spacer(1, 10))
graph_path_1 = report_dir / "fiets_vs_temp.png"
if graph_path_1.exists():
    elements.append(Image(str(graph_path_1), width=16*cm, height=9*cm))
elements.append(PageBreak())

# Grafiek 2
elements.append(Paragraph("📊 Grafiek 2: Aantal Fietsen per Uur", header_style))
elements.append(Spacer(1, 10))
graph_path_2 = report_dir / "fiets_vs_uur.png"
if graph_path_2.exists():
    elements.append(Image(str(graph_path_2), width=16*cm, height=9*cm))
elements.append(PageBreak())

# Weekdag Tabel
elements.append(Paragraph("📅 Tabel: Vrije Fietsen per Weekdag", header_style))
elements.append(Spacer(1, 10))

table_data = [["Weekdag", "Min", "Max", "Gem. Fietsen", "Gem. Temp (°C)"]]
for _, row in weekday_stats.iterrows():
    table_data.append([
        row["weekday"] if pd.notna(row["weekday"]) else "",
        int(row["Min"]) if pd.notna(row["Min"]) else 0,
        int(row["Max"]) if pd.notna(row["Max"]) else 0,
        int(row["Gemiddelde_fietsen"]) if pd.notna(row["Gemiddelde_fietsen"]) else 0,
        round(row["Gemiddelde_temp"],2) if pd.notna(row["Gemiddelde_temp"]) else 0
    ])

weekday_table = Table(table_data, hAlign='CENTER', colWidths=[3.2*cm, 2.5*cm, 2.5*cm, 3.8*cm, 3.8*cm])
weekday_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), TEAL),
    ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
    ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ("ALIGN", (0,0), (-1,0), "CENTER"),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 10),
    ("INNERGRID", (0,0), (-1,-1), 0.25, DARK_GREY),
    ("BOX", (0,0), (-1,-1), 1, DARK_GREY),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, LIGHT_GREY])
]))
elements.append(weekday_table)

# Bouw PDF
doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"✅ Professioneel PDF-rapport aangemaakt: {pdf_file}")