import pandas as pd
from datetime import datetime

# Paden
csv_file = 'transformed_data/combined.csv'
weekday_file = 'reports/weekday_stats.csv'
report_file = 'reports/report.md'
grafiek_file_1 = 'reports/fiets_vs_temp.png'
grafiek_file_2 = 'reports/fiets_vs_uur.png'

# Data
df = pd.read_csv(csv_file)
weekday_stats = pd.read_csv(weekday_file)

# Engelse → Nederlandse dagen
day_map = {
    "Monday": "Maandag",
    "Tuesday": "Dinsdag",
    "Wednesday": "Woensdag",
    "Thursday": "Donderdag",
    "Friday": "Vrijdag",
    "Saturday": "Zaterdag",
    "Sunday": "Zondag"
}
weekday_stats["weekday"] = weekday_stats["weekday"].map(day_map)

avg_temp = df['temperature'].mean()
avg_bikes = round(df["total_free_bikes"].mean())
correlatie = df['temperature'].corr(df['total_free_bikes'])

# Markdown genereren
with open(report_file, 'w') as f:
    f.write(f"# Data Workflow Rapport\n\n")
    f.write(f"**Gegenereerd op:** {datetime.now()}\n\n")

    # Grafiek 1
    f.write("## Grafiek: Vrije fietsen vs Temperatuur\n")
    f.write(f"![Fietsen vs Temp]({grafiek_file_1})\n\n")

    # Statistieken
    f.write("## Basisstatistieken\n")
    f.write(f"- Gemiddelde temperatuur: {avg_temp:.2f} °C\n")
    f.write(f"- Gemiddeld aantal vrije fietsen: {avg_bikes}\n")
    f.write(f"- Correlatie: {correlatie:.2f}\n\n")

    # Weekdag tabel
    f.write("## Vrije fietsen per weekdag\n\n")
    f.write("| Weekdag | Min | Max | Gemiddelde |\n")
    f.write("|---------|-----|-----|------------|\n")
    for _, row in weekday_stats.iterrows():
        f.write(f"| {row['weekday']} | {row['Min']} | {row['Max']} | {row['Gemiddelde']} |\n")

    f.write("\n---\n")

    # Grafiek 2
    f.write("## Grafiek: Vrije fietsen per uur\n")
    f.write(f"![Fiets vs Uur]({grafiek_file_2})\n")
