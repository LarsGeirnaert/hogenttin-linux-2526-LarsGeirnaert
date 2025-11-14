#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# Paden
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
report_dir = base_dir / "reports"
pdf_file = report_dir / "report.pdf"

# Data inlezen
df = pd.read_csv(data_file)

# Statistieken
mean_temp = df["temperature"].mean()
mean_bikes = df["total_free_bikes"].mean()
corr = df["temperature"].corr(df["total_free_bikes"])

# PDF aanmaken
doc = SimpleDocTemplate(pdf_file, pagesize=A4)
styles = getSampleStyleSheet()
elements = []

# Titel
elements.append(Paragraph("Data Workflow: Temperatuur vs. Aantal Vrije Fietsen in Gent", styles['Title']))
elements.append(Spacer(1, 12))

# Statistieken
elements.append(Paragraph(f"Gemiddelde temperatuur: {mean_temp:.2f} °C", styles['Normal']))
elements.append(Paragraph(f"Gemiddeld aantal vrije fietsen: {mean_bikes:.1f}", styles['Normal']))
elements.append(Paragraph(f"Correlatie tussen temperatuur en vrije fietsen: {corr:.2f}", styles['Normal']))
elements.append(Spacer(1, 12))

# Grafiek toevoegen
graph_path = report_dir / "fiets_vs_temp.png"
elements.append(Image(str(graph_path), width=400, height=300))

# PDF genereren
doc.build(elements)
print(f"📁 PDF-rapport opgeslagen in: {pdf_file}")
