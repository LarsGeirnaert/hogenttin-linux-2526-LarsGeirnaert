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
DARK_BLUE = "#004C99"  # Donkerder blauw voor duidelijkheid
ACCENT_RED = "#D62728" # Diep rood voor trendlijn
TEXT_COLOR = "#333333"

# --- Data inlezen ---
df = pd.read_csv(data_file)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- 1. Lineaire Regressie (op VOLLE 0-24u data) ---
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60 
X = df['hour'].values.reshape(-1, 1)
y = df['total_free_bikes'].values

model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

# --- 2. X-AS VERSCHUIVING (VOOR GRAFIEK) ---
# Uren 0, 1, 2 AM worden verschoven met +24, zodat de X-as van 3 tot 27 loopt
df['hour_shifted'] = df['hour'].apply(lambda h: h + 24 if h < 3 else h)

# --- 3. Data Aggregatie ---
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()
df_hourly['hour'] = df_hourly['timestamp'].dt.hour + df_hourly['timestamp'].dt.minute/60
df_hourly['hour_shifted'] = df_hourly['hour'].apply(lambda h: h + 24 if h < 3 else h)

# --- 4. Grafiek maken (MODERN DESIGN) ---
plt.style.use('seaborn-v0_8-darkgrid') # Moderne basis

fig, ax = plt.subplots(figsize=(12, 7))

# Punten: Donkerder blauw, iets groter, witte rand voor contrast
ax.scatter(df_hourly['hour_shifted'], df_hourly['total_free_bikes'], 
           color=DARK_BLUE, 
           label='Uurgemiddelden', 
           alpha=0.85,      # Minder transparant = donkerder
           s=70,            # Iets groter
           edgecolors='white', 
           linewidth=0.8)

# Trendlijn
X_shifted = df['hour_shifted'].values.reshape(-1, 1)
y_pred_shifted = model.predict(X_shifted)
ax.plot(df['hour_shifted'], y_pred_shifted, 
        color=ACCENT_RED, 
        linewidth=3, 
        label=f'Trendlijn (MSE: {mse:.2f})')

# Labels & Titel
ax.set_title('Aantal Vrije Fietsen per Uur (Gent)', fontsize=18, fontweight='bold', color=TEXT_COLOR, pad=20)
ax.set_xlabel('Uur van de dag (Start 03:00)', fontsize=13, color=TEXT_COLOR)
ax.set_ylabel('Aantal Vrije Fietsen', fontsize=13, color=TEXT_COLOR)

# X-As Ticks (Om de 2 uur, even uren)
tick_positions = np.arange(4, 28, 2) 
tick_labels = [f"{int(t % 24)}:00" for t in tick_positions] 
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, fontsize=11)
ax.set_xlim(3, 27)

# Grid & Legend
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(fontsize=11, frameon=True, facecolor='white', framealpha=0.9, loc='upper left')

# Layout
plt.tight_layout()

# Opslaan
plot_path = report_dir / "fiets_vs_uur.png"
plt.savefig(plot_path, dpi=300) # 300 DPI voor scherpe PDF
plt.close()
print(f"📁 Prachtige tijd-grafiek opgeslagen in: {plot_path}")