#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Paden
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data" / "combined.csv"
weekday_file = base_dir / "reports" / "weekday_stats.csv"
report_dir = base_dir / "reports"
pdf_file = report_dir / "report.pdf"

# Data
df = pd.read_csv(data_file)
weekday_stats = pd.read_csv(weekday_file)

mean_temp = df["temperature"].mean()
mean_bikes = round(df["total_free_bikes"].mean())
corr = df["temperature"].corr(df["total_free_bikes"])

# PDF setup
doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
styles = getSampleStyleSheet()
elements = []

# Titel
elements.append(Paragraph(
    "Data Workflow Rapport: Temperatuur vs Aantal Vrije Fietsen in Gent",
    styles['Title']
))
elements.append(Spacer(1, 16))

# Statistieken
elements.append(Paragraph("<b>Statistische Samenvatting</b>", styles['Heading2']))
elements.append(Paragraph(f"Gemiddelde temperatuur: {mean_temp:.2f} °C", styles['Normal']))
elements.append(Paragraph(f"Gemiddeld aantal vrije fietsen: {mean_bikes}", styles['Normal']))
elements.append(Paragraph(f"Correlatie: {corr:.2f}", styles['Normal']))
elements.append(Spacer(1, 16))

# Weekdag tabel
elements.append(Paragraph("<b>Vrije fietsen per weekdag</b>", styles['Heading2']))
elements.append(Spacer(1, 8))

table_data = [["Weekdag", "Min", "Max", "Gemiddelde"]]
for _, row in weekday_stats.iterrows():
    table_data.append([
        row["weekday"], row["Min"], row["Max"], row["Gemiddelde"]
    ])

table = Table(table_data)
table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("ALIGN", (1,1), (-1,-1), "CENTER")
]))
elements.append(table)
elements.append(Spacer(1, 16))

# Grafiek 1
elements.append(Paragraph("<b>Grafiek 1: Temperatuur vs vrije fietsen</b>", styles['Heading2']))
elements.append(Image(str(report_dir / "fiets_vs_temp.png"), width=400, height=300))
elements.append(PageBreak())

# Grafiek 2
elements.append(Paragraph("<b>Grafiek 2: Fietsen per uur</b>", styles['Heading2']))
elements.append(Image(str(report_dir / "fiets_vs_uur.png"), width=400, height=300))

# PDF bouwen
doc.build(elements)
print(f"📁 PDF gegenereerd: {pdf_file}")
