#!/usr/bin/env python3
import pandas as pd
from datetime import datetime
from pathlib import Path

# --- Paden ---
base_dir = Path.home() / "projects/data-workflow"
csv_file = base_dir / "transformed_data/combined.csv"
weekday_file = base_dir / "reports/weekday_stats.csv"
report_file = base_dir / "reports/report.md"

img_temp = "fiets_vs_temp.png"
img_time = "fiets_vs_uur.png"
img_week = "weekday_bars.png"

# --- Data inlezen ---
df = pd.read_csv(csv_file)
weekday_stats = pd.read_csv(weekday_file)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour + df["timestamp"].dt.minute/60

# SORTEREN (Data is al NL, alleen volgorde afdwingen)
dutch_order = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
weekday_stats['weekday'] = pd.Categorical(weekday_stats['weekday'], categories=dutch_order, ordered=True)
weekday_stats = weekday_stats.sort_values('weekday')

# --- Statistieken ---
mean_temp = df["temperature"].mean() if not df.empty else 0
mean_bikes = round(df["total_free_bikes"].mean()) if not df.empty else 0
day_data = df[(df['timestamp'].dt.hour >= 7) & (df['timestamp'].dt.hour < 19)]
day_avg_bikes = round(day_data['total_free_bikes'].mean()) if not day_data.empty else 0
night_data = df[(df['timestamp'].dt.hour < 7) | (df['timestamp'].dt.hour >= 19)]
night_avg_bikes = round(night_data['total_free_bikes'].mean()) if not night_data.empty else 0
corr_temp = df["temperature"].corr(df["total_free_bikes"])
corr_temp = corr_temp if not pd.isna(corr_temp) else 0
corr_hour = df["hour"].corr(df["total_free_bikes"])
corr_hour = corr_hour if not pd.isna(corr_hour) else 0

# --- Markdown Genereren ---
with open(report_file, "w") as f:
    f.write("# DATA WORKFLOW RAPPORT\n")
    f.write("### Temperatuur vs Aantal Vrije Fietsen in Gent\n\n")
    f.write(f"**Opgesteld door:** Lars Geirnaert (Klas: 2E2)  \n")
    f.write(f"**Gegenereerd op:** {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\n")
    f.write("---\n\n")

    f.write("## 📊 Statistische Samenvatting\n\n")
    f.write("| Statistiek | Waarde |\n")
    f.write("| :--- | ---: |\n")
    f.write(f"| Gemiddelde temperatuur | {mean_temp:.2f} °C |\n")
    f.write(f"| Gemiddeld aantal vrije fietsen | {int(mean_bikes)} |\n")
    f.write(f"| Gemiddeld aantal fietsen overdag (07-19u) | {int(day_avg_bikes)} |\n")
    f.write(f"| Gemiddeld aantal fietsen 's nachts (19-07u) | {int(night_avg_bikes)} |\n")
    f.write(f"| Correlatie temperatuur ↔ vrije fietsen | {corr_temp:.2f} |\n")
    f.write(f"| Correlatie uur ↔ vrije fietsen | {corr_hour:.2f} |\n\n")
    f.write("---\n\n")

    f.write("## 📈 Grafiek 1: Temperatuur vs Vrije Fietsen\n\n")
    f.write(f"![Temperatuur Grafiek]({img_temp})\n\n")
    f.write("---\n\n")

    f.write("## 📊 Grafiek 2: Aantal Fietsen per Uur\n\n")
    f.write(f"![Tijd Grafiek]({img_time})\n\n")
    f.write("---\n\n")

    f.write("## 📅 Analyse per Weekdag\n\n")
    f.write(f"![Weekdag Grafiek]({img_week})\n\n")
    f.write("| Weekdag | Min | Max | Gem. Fietsen | Gem. Temp (°C) |\n")
    f.write("| :--- | --: | --: | --: | --: |\n")

    for _, row in weekday_stats.iterrows():
        wd = row['weekday'] if pd.notna(row['weekday']) else ""
        mi = int(row['Min']) if pd.notna(row['Min']) else 0
        ma = int(row['Max']) if pd.notna(row['Max']) else 0
        avg_b = int(row['Gemiddelde_fietsen']) if pd.notna(row['Gemiddelde_fietsen']) else 0
        avg_t = f"{row['Gemiddelde_temp']:.2f}" if pd.notna(row['Gemiddelde_temp']) else "0.00"
        f.write(f"| {wd} | {mi} | {ma} | {avg_b} | {avg_t} |\n")

print(f"✅ Markdown rapport gegenereerd: {report_file}")