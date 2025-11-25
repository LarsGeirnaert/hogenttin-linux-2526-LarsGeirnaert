#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
import numpy as np

# --- Paden ---
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)

# --- Kleuren & Stijl ---
DARK_BLUE = "#004C99"
ACCENT_RED = "#D62728"
TEXT_COLOR = "#333333"
GRID_COLOR = "#999999"

# --- Data inlezen ---
df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# --- Voorbereiding ---
# Correlatie berekenen voor in de titel/legende
corr_temp_bikes = df["temperature"].corr(df["total_free_bikes"])

# Aggregatie per uur (voor een schonere scatterplot)
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()

# --- Lineaire Regressie ---
X = df["temperature"].values.reshape(-1, 1)
y = df["total_free_bikes"].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

# --- GRAFIEK MAKEN ---
plt.style.use('seaborn-v0_8-whitegrid')

fig, ax = plt.subplots(figsize=(12, 7))

# Rooster
ax.grid(True, which='major', color=GRID_COLOR, linestyle='-', linewidth=0.8, alpha=0.5, zorder=0)

# Punten (Uurgemiddelden)
ax.scatter(df_hourly["temperature"], df_hourly["total_free_bikes"], 
           label="Uurgemiddelden", 
           color=DARK_BLUE, 
           alpha=0.9, 
           s=70, 
           edgecolors='white', 
           linewidth=0.8, 
           zorder=3)

# Trendlijn
ax.plot(df["temperature"], y_pred, 
        color=ACCENT_RED, 
        linewidth=3, 
        label=f"Trendlijn (Correlatie: {corr_temp_bikes:.2f})", 
        zorder=4)

# Labels & Titel
ax.set_title("Temperatuur vs Aantal Vrije Fietsen (Gent)", fontsize=18, fontweight='bold', color=TEXT_COLOR, pad=20)
ax.set_xlabel("Temperatuur (°C)", fontsize=13, color=TEXT_COLOR)
ax.set_ylabel("Aantal Vrije Fietsen", fontsize=13, color=TEXT_COLOR)

# Legende
ax.legend(fontsize=11, frameon=True, facecolor='white', edgecolor=GRID_COLOR, framealpha=1, loc='upper left')

plt.tight_layout()

# Opslaan
plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"📁 Grafiek opgeslagen: {plot_path}")
