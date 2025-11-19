#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
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

# --- Data inlezen ---
df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# --- Statistieken berekenen ---
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60
mean_temp = df["temperature"].mean()
mean_bikes = round(df["total_free_bikes"].mean())
day_data = df[(df['timestamp'].dt.hour >= 7) & (df['timestamp'].dt.hour < 19)]
day_avg_bikes = round(day_data['total_free_bikes'].mean()) if not day_data.empty else 0
night_data = df[(df['timestamp'].dt.hour < 7) | (df['timestamp'].dt.hour >= 19)]
night_avg_bikes = round(night_data['total_free_bikes'].mean()) if not night_data.empty else 0

# Correlaties
corr_temp_bikes = df["temperature"].corr(df["total_free_bikes"])
corr_temp_bikes = corr_temp_bikes if not pd.isna(corr_temp_bikes) else 0
corr_hour_bikes = df["hour"].corr(df["total_free_bikes"])
corr_hour_bikes = corr_hour_bikes if not pd.isna(corr_hour_bikes) else 0

print("\n📈 Statistieken (Gebaseerd op werkelijke metingen):")
print(f"Gemiddelde temperatuur: {mean_temp:.2f} °C")
print(f"Correlatie Temp ↔ Fietsen: {corr_temp_bikes:.2f}")

# Weekdag tabel
df["weekday"] = df["timestamp"].dt.day_name()
weekday_stats = df.groupby("weekday").agg(
    Min=("total_free_bikes", "min"),
    Max=("total_free_bikes", "max"),
    Gemiddelde_fietsen=("total_free_bikes", lambda x: round(x.mean()) if len(x) > 0 else 0),
    Gemiddelde_temp=("temperature", lambda x: round(x.mean(),2) if len(x) > 0 else 0)
).reindex([
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
])

bike_cols = ["Min", "Max", "Gemiddelde_fietsen"]
for col in bike_cols:
    weekday_stats[col] = weekday_stats[col].round(0).astype('Int64')
weekday_csv = report_dir / "weekday_stats.csv"
weekday_stats.to_csv(weekday_csv)

# --- Data Aggregatie ---
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()

# --- Lineaire regressie ---
X = df["temperature"].values.reshape(-1, 1)
y = df["total_free_bikes"].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

# --- GRAFIEK MAKEN (MODERN DESIGN) ---
plt.style.use('seaborn-v0_8-darkgrid')

fig, ax = plt.subplots(figsize=(12, 7))

# Punten: Donkerder blauw
ax.scatter(df_hourly["temperature"], df_hourly["total_free_bikes"], 
           label="Uurgemiddelden", 
           color=DARK_BLUE, 
           alpha=0.85, 
           s=70, 
           edgecolors='white', 
           linewidth=0.8)

# Trendlijn
ax.plot(df["temperature"], y_pred, 
        color=ACCENT_RED, 
        linewidth=3, 
        label=f"Trendlijn (Correlatie: {corr_temp_bikes:.2f})")

# Labels & Titel
ax.set_title("Temperatuur vs Aantal Vrije Fietsen (Gent)", fontsize=18, fontweight='bold', color=TEXT_COLOR, pad=20)
ax.set_xlabel("Temperatuur (°C)", fontsize=13, color=TEXT_COLOR)
ax.set_ylabel("Aantal Vrije Fietsen", fontsize=13, color=TEXT_COLOR)

# Grid & Legend
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(fontsize=11, frameon=True, facecolor='white', framealpha=0.9, loc='upper left')

# Layout
plt.tight_layout()

plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"📁 Prachtige temperatuur-grafiek opgeslagen in: {plot_path}")