#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

# Paden
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)

# Data inlezen
df = pd.read_csv(data_file)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- 1. Lineaire Regressie (op RUWE data) ---
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60 
X = df['hour'].values.reshape(-1, 1)
y = df['total_free_bikes'].values

model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

# --- 2. Data Aggregatie (VOOR GRAFIEK) ---
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()
df_hourly['hour'] = df_hourly['timestamp'].dt.hour + df_hourly['timestamp'].dt.minute/60


# --- 3. Grafiek maken (met GEAGGREGEERDE punten en verbeterde stijl) ---
plt.style.use('seaborn-v0_8-darkgrid') # Consistentie in stijl
fig, ax = plt.subplots(figsize=(12, 6)) # Breder figuur voor uren-as

# Plot de GEAGGREGEERDE punten (elk punt is nu het uurgemiddelde)
ax.scatter(df_hourly['hour'], df_hourly['total_free_bikes'], 
           color='#2ca02c', label='Uurgemiddelden', alpha=0.7, s=50) # Mooie groene kleur, grotere punten

# Plot de trendlijn (gebruik de originele 'hour' kolom voor de X-range van de lijn)
ax.plot(df['hour'], y_pred, color='#ff7f0e', linewidth=2.5, label='Trendlijn (lineaire regressie)') # Oranje lijn

ax.set_xlabel('Uur van de dag', fontsize=12)
ax.set_ylabel('Aantal vrije fietsen', fontsize=12)
ax.set_title('Aantal vrije fietsen door de dag (Gent) - Uurgemiddelden', fontsize=16, fontweight='bold')
ax.set_xticks(range(0,25, 2)) # uren 0-24, elke 2 uur een label
ax.grid(True, linestyle='--', alpha=0.7)
ax.legend(fontsize=10, loc='upper left')

# Verwijder top en rechter spine
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Voeg tekst toe voor de MSE
ax.text(0.05, 0.95, f'MSE: {mse:.2f}', transform=ax.transAxes, 
        fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.7))


plot_path = report_dir / "fiets_vs_uur.png"
plt.savefig(plot_path, dpi=300, bbox_inches='tight') # Hogere resolutie, geen witruimte
plt.close()
print(f"📁 Grafiek opgeslagen in: {plot_path}")