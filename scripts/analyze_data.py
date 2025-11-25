#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import numpy as np

# --- Paden ---
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)

# --- Data inlezen ---
df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# --- Statistieken Berekenen ---
# Uur toevoegen voor correlatie
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60

# Gemiddelden
mean_temp = df["temperature"].mean()
mean_bikes = round(df["total_free_bikes"].mean())

# Correlaties
corr_temp_bikes = df["temperature"].corr(df["total_free_bikes"])
corr_hour_bikes = df["hour"].corr(df["total_free_bikes"])

# Printen naar de log (zodat je kan zien dat het werkt)
print("------------------------------------------------")
print("📊 ANALYSE RESULTATEN")
print(f"Gemiddelde temperatuur: {mean_temp:.2f} °C")
print(f"Gemiddeld aantal vrije fietsen: {mean_bikes}")
print(f"Correlatie Temp ↔ Fietsen: {corr_temp_bikes:.2f}")
print(f"Correlatie Uur ↔ Fietsen: {corr_hour_bikes:.2f}")
print("------------------------------------------------")

# --- Weekdag Tabel Genereren ---
# 1. Engels voor sortering
df["weekday"] = df["timestamp"].dt.day_name()

weekday_stats = df.groupby("weekday").agg(
    Min=("total_free_bikes", "min"),
    Max=("total_free_bikes", "max"),
    Gemiddelde_fietsen=("total_free_bikes", lambda x: round(x.mean()) if len(x) > 0 else 0),
    Gemiddelde_temp=("temperature", lambda x: round(x.mean(),2) if len(x) > 0 else 0)
).reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

# 2. Vertalen naar Nederlands
day_map = {
    "Monday": "Maandag", "Tuesday": "Dinsdag", "Wednesday": "Woensdag",
    "Thursday": "Donderdag", "Friday": "Vrijdag", "Saturday": "Zaterdag", "Sunday": "Zondag"
}
weekday_stats.index = weekday_stats.index.map(day_map)

# 3. Opslaan
bike_cols = ["Min", "Max", "Gemiddelde_fietsen"]
for col in bike_cols:
    weekday_stats[col] = weekday_stats[col].round(0).astype('Int64')

weekday_csv = report_dir / "weekday_stats.csv"
weekday_stats.to_csv(weekday_csv)
print(f"✅ Weekdag-statistieken opgeslagen: {weekday_csv}")