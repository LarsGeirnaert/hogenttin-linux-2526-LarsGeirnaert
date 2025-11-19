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

# --- 1. Lineaire Regressie (op VOLLE 0-24u data) ---
# De uren voor de regressie (0.0 t/m 24.0)
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60 
X = df['hour'].values.reshape(-1, 1)
y = df['total_free_bikes'].values

# Model getraind op ALLE data
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred) # MSE is berekend over de VOLLE 24u cyclus


# --- 2. X-AS VERSCHUIVING (VOOR GRAFIEK) ---
# Uren 0, 1, 2 AM worden verschoven met +24, zodat de X-as van 3 tot 27 loopt
df['hour_shifted'] = df['hour'].apply(lambda h: h + 24 if h < 3 else h)

# --- 3. Data Aggregatie (Gebruikt de verschoven tijd) ---
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()
# De uurkolom opnieuw berekenen en de shift toepassen op de geaggregeerde data
df_hourly['hour'] = df_hourly['timestamp'].dt.hour + df_hourly['timestamp'].dt.minute/60
df_hourly['hour_shifted'] = df_hourly['hour'].apply(lambda h: h + 24 if h < 3 else h)


# --- 4. Grafiek maken (met verschoven as) ---
plt.figure(figsize=(12,6)) # Grotere breedte om labels te vermijden

# Plot de GEAGGREGEERDE punten tegen de verschoven X-as
plt.scatter(df_hourly['hour_shifted'], df_hourly['total_free_bikes'], color='blue', label='Uurgemiddelden')

# Plot de trendlijn: we moeten de trendlijn predicties opnieuw berekenen voor de verschoven X-waarden
X_shifted = df['hour_shifted'].values.reshape(-1, 1)
y_pred_shifted = model.predict(X_shifted)
plt.plot(df['hour_shifted'], y_pred_shifted, color='red', linewidth=2, label='Trendlijn (linear regression)')


plt.xlabel('Uur van de dag (Start 3:00)', fontsize=12)
plt.ylabel('Aantal vrije fietsen', fontsize=12)
plt.title('Aantal vrije fietsen per uur (Volledige Dataset, X-as verschoven)', fontsize=14)


# --- AANGEPASTE CODE VOOR 24 TICK LABELS ---
# Vanaf 3u tot 26u (27 is de grens van de plot, 26 is 2u 's nachts)
tick_positions = np.arange(3, 27, 1) 
# De labels moeten de modulaire tijd weergeven (zorgt dat 24 = 0, 25 = 1, etc.)
tick_labels = [f"{t % 24:.0f}u" for t in tick_positions] 
plt.xticks(tick_positions, tick_labels, rotation=45, ha='right') # Roteer labels voor leesbaarheid
plt.xlim(3, 27) # Zet de grenzen van de X-as
# ------------------------------------------

plt.grid(True)
plt.legend()

# Toon de MSE van de volledige dataset
plt.text(0.05, 0.95, f"MSE (Volle Dataset): {mse:.2f}", transform=plt.gca().transAxes, color='black')

# Opslaan
plot_path = report_dir / "fiets_vs_uur.png"
plt.savefig(plot_path, bbox_inches='tight') # Gebruik bbox_inches om labels niet af te snijden
plt.close()
print(f"📁 Grafiek opgeslagen in: {plot_path}")