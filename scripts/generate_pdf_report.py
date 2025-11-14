#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

# Paden
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data" / "combined.csv"
report_dir = base_dir / "reports"
pdf_file = report_dir / "report.pdf"

# Data inlezen
df = pd.read_csv(data_file)

# Statistieken
mean_temp = df["temperature"].mean()
mean_bikes = df["total_free_bikes"].mean()
corr = df["temperature"].corr(df["total_free_bikes"])

# PDF instellen
doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
styles = getSampleStyleSheet()
elements = []

# ------------------------------------
# TITEL
# ------------------------------------
elements.append(Paragraph(
    "Data Workflow Rapport: Temperatuur vs. Aantal Vrije Fietsen in Gent",
    styles['Title']
))
elements.append(Spacer(1, 16))

# ------------------------------------
# STATISTIEKEN
# ------------------------------------
elements.append(Paragraph("<b>Statistische Samenvatting</b>", styles['Heading2']))
elements.append(Spacer(1, 8))

elements.append(Paragraph(
    f"Gemiddelde temperatuur: {mean_temp:.2f} °C", styles['Normal']
))
elements.append(Paragraph(
    f"Gemiddeld aantal vrije fietsen: {mean_bikes:.1f}", styles['Normal']
))
elements.append(Paragraph(
    f"Correlatie tussen temperatuur en aantal vrije fietsen: {corr:.2f}",
    styles['Normal']
))
elements.append(Spacer(1, 16))

# ------------------------------------
# GRAFIEK 1 – Temp vs Free Bikes
# ------------------------------------
elements.append(Paragraph("<b>Grafiek 1: Relatie tussen temperatuur en vrije fietsen</b>", styles['Heading2']))
elements.append(Spacer(1, 8))

elements.append(Paragraph("""
Deze grafiek toont het verband tussen de temperatuur in Gent en het aantal beschikbare 
deelfietsen. Elke punt vertegenwoordigt een meetmoment. Een lineaire regressielijn wordt 
toegevoegd om de trend visueel weer te geven. Een positieve correlatie betekent dat hogere 
temperaturen gemiddeld samengaan met meer beschikbare fietsen.
""", styles['Normal']))
elements.append(Spacer(1, 12))

graph_path_1 = report_dir / "fiets_vs_temp.png"
elements.append(Image(str(graph_path_1), width=400, height=300))
elements.append(Spacer(1, 24))

# --- NIEUWE PAGINA ---
elements.append(PageBreak())

# ------------------------------------
# GRAFIEK 2 – Bikes per Hour
# ------------------------------------
elements.append(Paragraph("<b>Grafiek 2: Aantal vrije fietsen per tijdstip van de dag</b>", styles['Heading2']))
elements.append(Spacer(1, 8))

elements.append(Paragraph("""
Deze grafiek toont hoe het aantal beschikbare fietsen varieert doorheen de dag. 
Hiermee krijg je een beter beeld op piekmomenten en rustige momenten. 
In tegenstelling tot de vorige grafiek wordt hier niet naar temperatuur gekeken, 
maar uitsluitend naar tijdstip versus beschikbaarheid.
""", styles['Normal']))
elements.append(Spacer(1, 12))

graph_path_2 = report_dir / "fiets_vs_uur.png"
elements.append(Image(str(graph_path_2), width=400, height=300))
elements.append(Spacer(1, 24))

# ------------------------------------
# PDF genereren
# ------------------------------------
doc.build(elements)
print(f"📁 PDF-rapport opgeslagen in: {pdf_file}")
