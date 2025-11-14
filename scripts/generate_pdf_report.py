#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# Paden
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
weekday_file = base_dir / "reports/weekday_stats.csv"
report_dir = base_dir / "reports"
pdf_file = report_dir / "report.pdf"

# Data
df = pd.read_csv(data_file)
weekday_stats = pd.read_csv(weekday_file)

# Algemene statistieken
mean_temp = df["temperature"].mean()
mean_bikes = round(df["total_free_bikes"].mean())

# Gemiddeld aantal fietsen overdag/nacht
day_avg_bikes = round(df[(pd.to_datetime(df['timestamp']).dt.hour >= 7) & 
                         (pd.to_datetime(df['timestamp']).dt.hour < 19)]['total_free_bikes'].mean())
night_avg_bikes = round(df[(pd.to_datetime(df['timestamp']).dt.hour < 7) | 
                           (pd.to_datetime(df['timestamp']).dt.hour >= 19)]['total_free_bikes'].mean())

corr = df["temperature"].corr(df["total_free_bikes"])

# Nederlandse weekdagen
day_map = {
    "Monday": "Maandag", "Tuesday": "Dinsdag", "Wednesday": "Woensdag",
    "Thursday": "Donderdag", "Friday": "Vrijdag", "Saturday": "Zaterdag", "Sunday": "Zondag"
}
weekday_stats["weekday"] = weekday_stats["weekday"].map(day_map)

# PDF setup
doc = SimpleDocTemplate(str(pdf_file), pagesize=A4,
                        rightMargin=2*cm, leftMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'TitleStyle', parent=styles['Title'], fontSize=24, alignment=1, spaceAfter=20)
header_style = ParagraphStyle(
    'HeaderStyle', parent=styles['Heading2'], fontSize=16, spaceAfter=12)
normal_style = ParagraphStyle(
    'NormalStyle', parent=styles['Normal'], fontSize=12, leading=16)

elements = []

# ---------- TITELPAGINA ----------
elements.append(Paragraph("Data Workflow Rapport", title_style))
elements.append(Paragraph("Temperatuur vs Aantal Vrije Fietsen in Gent", header_style))
elements.append(Spacer(1, 12))
elements.append(Paragraph(f"Gegenereerd op: {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')}", normal_style))
elements.append(PageBreak())

# ---------- STATISTIEKEN ----------
elements.append(Paragraph("Statistische Samenvatting", header_style))
elements.append(Spacer(1, 12))
elements.append(Paragraph(f"Gemiddelde temperatuur: {mean_temp:.2f} °C", normal_style))
elements.append(Paragraph(f"Gemiddeld aantal vrije fietsen: {mean_bikes}", normal_style))
elements.append(Paragraph(f"Gemiddeld aantal fietsen overdag (07-19u): {day_avg_bikes}", normal_style))
elements.append(Paragraph(f"Gemiddeld aantal fietsen ’s nachts (19-07u): {night_avg_bikes}", normal_style))
elements.append(Paragraph(f"Correlatie tussen temperatuur en aantal vrije fietsen: {corr:.2f}", normal_style))
elements.append(PageBreak())

# ---------- GRAFIEK 1 ----------
elements.append(Paragraph("Grafiek 1: Temperatuur vs Vrije Fietsen", header_style))
elements.append(Spacer(1, 12))
graph_path_1 = report_dir / "fiets_vs_temp.png"
elements.append(Image(str(graph_path_1), width=16*cm, height=10*cm))
elements.append(PageBreak())

# ---------- GRAFIEK 2 ----------
elements.append(Paragraph("Grafiek 2: Aantal Fietsen per Uur", header_style))
elements.append(Spacer(1, 12))
graph_path_2 = report_dir / "fiets_vs_uur.png"
elements.append(Image(str(graph_path_2), width=16*cm, height=10*cm))
elements.append(PageBreak())

# ---------- WEEKDAG TABEL ----------
elements.append(Paragraph("Tabel: Vrije Fietsen per Weekdag", header_style))
elements.append(Spacer(1, 12))
table_data = [["Weekdag", "Min", "Max", "Gemiddelde Fietsen", "Gemiddelde Temp (°C)"]]
for _, row in weekday_stats.iterrows():
    table_data.append([
        row["weekday"],
        int(row["Min"]) if not pd.isna(row["Min"]) else 0,
        int(row["Max"]) if not pd.isna(row["Max"]) else 0,
        int(row["Gemiddelde_fietsen"]) if not pd.isna(row["Gemiddelde_fietsen"]) else 0,
        round(row["Gemiddelde_temp"], 2) if not pd.isna(row["Gemiddelde_temp"]) else 0
    ])

table = Table(table_data, hAlign='CENTER')
table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d9d9d9")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.black),
    ("ALIGN", (1,1), (-1,-1), "CENTER"),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 11),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BOX", (0,0), (-1,-1), 1, colors.grey)
]))
elements.append(table)

# ---------- BUILD PDF ----------
doc.build(elements)
print(f"📁 Professioneel PDF-rapport opgeslagen in: {pdf_file}")


elements.append(Paragraph("Heatmap: Vrije Fietsen per Uur per Weekdag", header_style))
elements.append(Image(str(report_dir / "fiets_heatmap.png"), width=16*cm, height=10*cm))
elements.append(PageBreak())

elements.append(Paragraph("Rolling Average van Vrije Fietsen", header_style))
elements.append(Image(str(report_dir / "rolling_avg.png"), width=16*cm, height=10*cm))
elements.append(PageBreak())

elements.append(Paragraph("Boxplot Vrije Fietsen per Weekdag", header_style))
elements.append(Image(str(report_dir / "boxplot_weekday.png"), width=16*cm, height=10*cm))
elements.append(PageBreak())
