#!/usr/bin/env python3
import pandas as pd
from datetime import datetime
from pathlib import Path

# --- Paden ---
base_dir = Path.home() / "projects/data-workflow"
csv_file = base_dir / "transformed_data/combined.csv"
weekday_file = base_dir / "reports/weekday_stats.csv"
report_file = base_dir / "reports/report.md"
grafiek_file_1 = base_dir / "reports/fiets_vs_temp.png"
grafiek_file_2 = base_dir / "reports/fiets_vs_uur.png"

# --- Data inlezen ---
df = pd.read_csv(csv_file)
weekday_stats = pd.read_csv(weekday_file)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour

# Engelse → Nederlandse dagen
day_map = {
    "Monday": "Maandag", "Tuesday": "Dinsdag", "Wednesday": "Woensdag",
    "Thursday": "Donderdag", "Friday": "Vrijdag", "Saturday": "Zaterdag", "Sunday": "Zondag"
}
weekday_stats["weekday"] = weekday_stats["weekday"].map(day_map)

# --- Statistieken ---
avg_temp = df["temperature"].mean() if not df.empty else 0
avg_bikes = round(df["total_free_bikes"].mean()) if not df.empty else 0

daytime_data = df[(df["hour"] >= 7) & (df["hour"] < 19)]
daytime_avg = round(daytime_data["total_free_bikes"].mean()) if not daytime_data.empty else 0

nighttime_data = pd.concat([df[df["hour"] >= 19]["total_free_bikes"], df[df["hour"] < 7]["total_free_bikes"]])
nighttime_avg = round(nighttime_data.mean()) if not nighttime_data.empty else 0

correlatie = df["temperature"].corr(df["total_free_bikes"])
correlatie = correlatie if not pd.isna(correlatie) else 0

# --- Markdown genereren ---
with open(report_file, "w") as f:
    f.write(f"# Data Workflow Rapport\n\n")
    f.write(f"**Gegenereerd op:** {datetime.now()}\n\n")

    f.write("## Grafiek: Vrije fietsen vs Temperatuur\n")
    if grafiek_file_1.exists():
        f.write(f"![Fietsen vs Temp]({grafiek_file_1})\n\n")
    else:
        f.write("_Grafiek niet beschikbaar_\n\n")

    f.write("## Basisstatistieken\n")
    f.write(f"- Gemiddelde temperatuur: {avg_temp:.2f} °C\n")
    f.write(f"- Gemiddeld aantal vrije fietsen: {avg_bikes}\n")
    f.write(f"- Gemiddeld aantal fietsen overdag (07-19u): {daytime_avg}\n")
    f.write(f"- Gemiddeld aantal fietsen ’s nachts (19-07u): {nighttime_avg}\n")
    f.write(f"- Correlatie: {correlatie:.2f}\n\n")

    f.write("## Vrije fietsen per weekdag\n\n")
    f.write("| Weekdag | Min | Max | Gemiddelde |\n")
    f.write("|---------|-----|-----|------------|\n")
    for _, row in weekday_stats.iterrows():
        f.write(
            f"| {row['weekday'] if pd.notna(row['weekday']) else ''} "
            f"| {int(row['Min']) if not pd.isna(row['Min']) else 0} "
            f"| {int(row['Max']) if not pd.isna(row['Max']) else 0} "
            f"| {int(row['Gemiddelde_fietsen']) if not pd.isna(row['Gemiddelde_fietsen']) else 0} |\n"
        )

    f.write("\n---\n")

    f.write("## Grafiek: Vrije fietsen per uur\n")
    if grafiek_file_2.exists():
        f.write(f"![Fiets vs Uur]({grafiek_file_2})\n")
    else:
        f.write("_Grafiek niet beschikbaar_\n")
