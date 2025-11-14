import pandas as pd
from datetime import datetime
import os

# Paden
csv_file = 'transformed_data/combined.csv'
report_file = 'reports/report.md'
grafiek_file = 'reports/fiets_vs_temp.png'

# Lees CSV
df = pd.read_csv(csv_file)
avg_temp = df['temperature'].mean()
avg_bikes = df["total_free_bikes"].mean()
correlatie = df['temperature'].corr(df['total_free_bikes'])

# Ronde waarde van gemiddeld aantal fietsen
avg_bikes = round(df["total_free_bikes"].mean())

# Markdown genereren
with open(report_file, 'w') as f:
    f.write(f"# Data workflow rapport\n\n")
    f.write(f"Datum gegenereerd: {datetime.now()}\n\n")
    f.write(f"## Grafiek: Vrije fietsen vs Temperatuur\n\n")
    f.write(f"![Fietsen vs Temp]({grafiek_file})\n\n")
    f.write("## Basisstatistieken\n")
    f.write(f"- Gemiddelde temperatuur: {avg_temp:.2f} °C\n")
    f.write(f"- Gemiddeld aantal vrije fietsen: {avg_bikes}\n")  # nu afgerond
    f.write(f"- Correlatie: {correlatie:.2f}\n")
