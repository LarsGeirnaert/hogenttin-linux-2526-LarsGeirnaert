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

# --- 1. FILTEREN VOOR ACTIEVE UREN (3u00 tot 2u59) ---
# Filter de uren 0, 1 en 2 uit, want die zijn niet representatief voor het gebruik.
inactive_hours = [0, 1, 2]
df_active = df[~df['timestamp'].dt.hour.isin(inactive_hours)].copy()


# --- 2. Lineaire Regressie (op GEFILTERDE data) ---
df_active['hour'] = df_active['timestamp'].dt.hour + df_active['timestamp'].dt.minute/60 
X_active = df_active['hour'].values.reshape(-1, 1)
y_active = df_active['total_free_bikes'].values

model = LinearRegression()
model.fit(X_active, y_active)
y_pred_active = model.predict(X_active)
mse_active = mean_squared_error(y_active, y_pred_active)


# --- 3. Data Aggregatie (VOOR GRAFIEK) ---
# Aggregatie alleen op de actieve data
df_hourly_active = df_active.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()
df_hourly_active['hour'] = df_hourly_active['timestamp'].dt.hour + df_hourly_active['timestamp'].dt.minute/60


# --- 4. Grafiek maken (met GEAGGREGEERDE en GEFILTERDE punten) ---
plt.figure(figsize=(10,5))

# Plot de GEAGGREGEERDE punten (uurgemiddelden van de actieve uren)
plt.scatter(df_hourly_active['hour'], df_hourly_active['total_free_bikes'], color='blue', label='Uurgemiddelden (3u-2u)')

# Plot de trendlijn (gebruik de actieve data)
plt.plot(df_active['hour'], y_pred_active, color='red', linewidth=2, label='Trendlijn (linear regression)')

plt.xlabel('Uur van de dag (3:00 t/m 2:59)')
plt.ylabel('Aantal vrije fietsen')
plt.title('Aantal vrije fietsen tijdens actieve uren (Gent)')
plt.xticks(range(0,25, 3)) # Toon de uren 0, 3, 6, 9, etc.
plt.grid(True)
plt.legend()

# Toon de nieuwe, lagere MSE
plt.text(min(df_active['hour']), max(df_active['total_free_bikes'])*0.9, f"MSE (Actieve Uren): {mse_active:.2f}", color='black')

# Opslaan
plot_path = report_dir / "fiets_vs_uur.png"
plt.savefig(plot_path)
plt.close()
print(f"📁 Grafiek opgeslagen in: {plot_path}")