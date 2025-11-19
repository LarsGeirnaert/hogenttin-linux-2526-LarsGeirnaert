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
GRID_COLOR = "#999999" # Duidelijk grijs voor de lijnen

# --- Data inlezen ---
df = pd.read_csv(data_file)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- 1. Lineaire Regressie ---
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60 
X = df['hour'].values.reshape(-1, 1)
y = df['total_free_bikes'].values

model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

# --- 2. X-AS VERSCHUIVING ---
df['hour_shifted'] = df['hour'].apply(lambda h: h + 24 if h < 3 else h)

# --- 3. Data Aggregatie ---
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()
df_hourly['hour'] = df_hourly['timestamp'].dt.hour + df_hourly['timestamp'].dt.minute/60
df_hourly['hour_shifted'] = df_hourly['hour'].apply(lambda h: h + 24 if h < 3 else h)

# --- 4. Grafiek maken (HOOG CONTRAST GRID) ---
plt.style.use('seaborn-v0_8-whitegrid') # Witte achtergrond voor beter contrast

fig, ax = plt.subplots(figsize=(12, 7))

# Het Rooster (Grid) - Nu veel duidelijker
ax.grid(True, which='major', color=GRID_COLOR, linestyle='-', linewidth=0.8, alpha=0.5, zorder=0)

# Punten
ax.scatter(df_hourly['hour_shifted'], df_hourly['total_free_bikes'], 
           color=DARK_BLUE, 
           label='Uurgemiddelden', 
           alpha=0.9, 
           s=70, 
           edgecolors='white', 
           linewidth=0.8,
           zorder=3) # zorder=3 zorgt dat punten BOVEN op de lijnen liggen

# Trendlijn
X_shifted = df['hour_shifted'].values.reshape(-1, 1)
y_pred_shifted = model.predict(X_shifted)
ax.plot(df['hour_shifted'], y_pred_shifted, 
        color=ACCENT_RED, 
        linewidth=3, 
        label=f'Trendlijn (MSE: {mse:.2f})',
        zorder=4)

# Labels & Titel
ax.set_title('Aantal Vrije Fietsen per Uur (Gent)', fontsize=18, fontweight='bold', color=TEXT_COLOR, pad=20)
ax.set_xlabel('Uur van de dag (Start 03:00)', fontsize=13, color=TEXT_COLOR)
ax.set_ylabel('Aantal Vrije Fietsen', fontsize=13, color=TEXT_COLOR)

# X-As Ticks
tick_positions = np.arange(4, 28, 2) 
tick_labels = [f"{int(t % 24)}:00" for t in tick_positions] 
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, fontsize=11)
ax.set_xlim(3, 27)

# Legend (met kader)
ax.legend(fontsize=11, frameon=True, facecolor='white', edgecolor=GRID_COLOR, framealpha=1, loc='upper left')

plt.tight_layout()

plot_path = report_dir / "fiets_vs_uur.png"
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"📁 Grafiek met duidelijk raster opgeslagen in: {plot_path}")