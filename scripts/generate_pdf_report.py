#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Paden
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
weekday_file = base_dir / "reports/weekday_stats.csv"
report_dir = base_dir / "reports"
pdf_file = report_dir / "report.pdf"

# Data
df = pd.read_csv(data_file)
weekday_stats = pd.read_csv(weekday_file)

mean_temp = df["temperature"].mean()
mean_bikes = round(df["total_free_bikes"].mean())

# Dag/nacht gemiddeld
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
daytime_avg = round(df[(df["hour"] >= 7) & (df["hour"] < 19)]["total_free_bikes"].mean())
nighttime_avg = round(pd.concat([df[df["hour"] >= 19]["total_free_bikes"], df[df["hour"] < 7]["total_free_bikes"]]).mean())

corr = df["temperature"].corr(df["total_free_bikes"])

# Engelse → Nederlandse dagen
day_map = {
    "Monday": "Maandag", "Tuesday": "Dinsdag", "Wednesday": "Woensdag",
    "Thursday": "Donderdag", "Friday": "Vrijdag", "Saturday": "Zaterdag", "Sunday": "Zondag"
}
weekday_stats["weekday"] = weekday_stats["weekday"].map(day_map)

# PDF setup
doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
styles = getSampleStyleSheet()
elements = []

# Titelpagina + statistieken
elements.append(Paragraph("Data Workflow Rapport: Temperatuur vs Aantal Vrije Fietsen in Gent", styles['Title']))
elements.append(Spacer(1, 20))
elements.append(Paragraph("<b>Statistische Samenvatting</b>", styles['Heading2']))
elements.append(Spacer(1, 8))
elements.append(Paragraph(f"Gemiddelde temperatuur: {mean_temp:.2f} °C", styles['Normal']))
elements.append(Paragraph(f"Gemiddeld aantal vrije fietsen: {mean_bikes}", styles['Normal']))
elements.append(Paragraph(f"Gemiddeld aantal fietsen overdag (7-19u): {daytime_avg}", styles['Normal']))
elements.append(Paragraph(f"Gemiddeld aantal fietsen ’s nachts (19-7u): {nighttime_avg}", styles['Normal']))
elements.append(Paragraph(f"Correlatie: {corr:.2f}", styles['Normal']))
elements.append(PageBreak())

# Grafiek 1
elements.append(Paragraph("<b>Grafiek 1: Temperatuur vs vrije fietsen</b>", styles['Heading2']))
elements.append(Spacer(1, 12))
elements.append(Image(str(report_dir / "fiets_vs_temp.png"), width=400, height=300))
elements.append(PageBreak())

# Grafiek 2
elements.append(Paragraph("<b>Grafiek 2: Aantal fietsen per uur</b>", styles['Heading2']))
elements.append(Spacer(1, 12))
elements.append(Image(str(report_dir / "fiets_vs_uur.png"), width=400, height=300))
elements.append(PageBreak())

# Weekdag tabel
elements.append(Paragraph("<b>Tabel: Vrije fietsen per weekdag</b>", styles['Heading2']))
elements.append(Spacer(1, 12))
table_data = [["Weekdag", "Min", "Max", "Gemiddelde"]]
for _, row in weekday_stats.iterrows():
    table_data.append([row["weekday"], row["Min"], row["Max"], row["Gemiddelde"]])

table = Table(table_data)
table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("ALIGN", (1,1), (-1,-1), "CENTER"),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
]))
elements.append(table)

# PDF bouwen
doc.build(elements)
print(f"📁 PDF gegenereerd: {pdf_file}")
