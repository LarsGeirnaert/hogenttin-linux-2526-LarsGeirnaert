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
GRID_COLOR = "#999999"

# --- Data inlezen ---
df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# --- Statistieken ---
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60
mean_temp = df["temperature"].mean()
corr_temp_bikes = df["temperature"].corr(df["total_free_bikes"])

# --- Weekdag tabel ---
# 1. We gebruiken eerst Engels om correct te kunnen sorteren (Pandas default)
df["weekday"] = df["timestamp"].dt.day_name()

weekday_stats = df.groupby("weekday").agg(
    Min=("total_free_bikes", "min"),
    Max=("total_free_bikes", "max"),
    Gemiddelde_fietsen=("total_free_bikes", lambda x: round(x.mean()) if len(x) > 0 else 0),
    Gemiddelde_temp=("temperature", lambda x: round(x.mean(),2) if len(x) > 0 else 0)
).reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

# 2. VERTALING NAAR NEDERLANDS (Voordat we opslaan!)
day_map = {
    "Monday": "Maandag", "Tuesday": "Dinsdag", "Wednesday": "Woensdag",
    "Thursday": "Donderdag", "Friday": "Vrijdag", "Saturday": "Zaterdag", "Sunday": "Zondag"
}
# We hernoemen de index van de tabel naar het Nederlands
weekday_stats.index = weekday_stats.index.map(day_map)

# 3. Afronden en opslaan
bike_cols = ["Min", "Max", "Gemiddelde_fietsen"]
for col in bike_cols:
    weekday_stats[col] = weekday_stats[col].round(0).astype('Int64')

weekday_csv = report_dir / "weekday_stats.csv"
weekday_stats.to_csv(weekday_csv)
print(f"\n📁 Weekdag-statistieken (NL) opgeslagen in: {weekday_csv}")


# --- Data Aggregatie (Grafieken) ---
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()

# --- Lineaire regressie ---
X = df["temperature"].values.reshape(-1, 1)
y = df["total_free_bikes"].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

# --- GRAFIEK MAKEN: Temp vs Fietsen ---
plt.style.use('seaborn-v0_8-whitegrid')

fig, ax = plt.subplots(figsize=(12, 7))

ax.grid(True, which='major', color=GRID_COLOR, linestyle='-', linewidth=0.8, alpha=0.5, zorder=0)

ax.scatter(df_hourly["temperature"], df_hourly["total_free_bikes"], 
           label="Uurgemiddelden", color=DARK_BLUE, alpha=0.9, s=70, 
           edgecolors='white', linewidth=0.8, zorder=3)

ax.plot(df["temperature"], y_pred, color=ACCENT_RED, linewidth=3, 
        label=f"Trendlijn (Correlatie: {corr_temp_bikes:.2f})", zorder=4)

ax.set_title("Temperatuur vs Aantal Vrije Fietsen (Gent)", fontsize=18, fontweight='bold', color=TEXT_COLOR, pad=20)
ax.set_xlabel("Temperatuur (°C)", fontsize=13, color=TEXT_COLOR)
ax.set_ylabel("Aantal Vrije Fietsen", fontsize=13, color=TEXT_COLOR)

ax.legend(fontsize=11, frameon=True, facecolor='white', edgecolor=GRID_COLOR, framealpha=1, loc='upper left')
plt.tight_layout()

plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"📁 Grafiek fiets_vs_temp opgeslagen in: {plot_path}")