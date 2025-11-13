#!/usr/bin/env python3
# analyze_data.py — leest combined.csv in en maakt analyse & grafiek

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Paden
base_dir = Path.home() / "projects" / "data-workflow"
data_file = base_dir / "transformed_data" / "combined.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)

# Data inlezen
df = pd.read_csv(data_file)
print("📊 Gegevens ingelezen:")
print(df.head())

# Statistieken
mean_temp = df["temperature"].mean()
mean_bikes = df["avg_free_bikes"].mean()
corr = df["temperature"].corr(df["avg_free_bikes"])

print("\n📈 Statistieken:")
print(f"Gemiddelde temperatuur: {mean_temp:.2f} °C")
print(f"Gemiddeld aantal vrije fietsen: {mean_bikes:.2f}")
print(f"Correlatie tussen temperatuur en vrije fietsen: {corr:.2f}")

# Grafiek maken (y-as als percentage)
plt.figure(figsize=(8,5))
plt.scatter(df["temperature"], df["avg_free_bikes"] * 100, color="blue")  # *100 voor %
plt.title("Relatie tussen temperatuur en beschikbaarheid van deelfietsen (Gent)")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Gemiddeld aantal vrije fietsen (%)")
plt.grid(True)

# Opslaan
plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path)
print(f"\n📁 Grafiek opgeslagen in: {plot_path}")
