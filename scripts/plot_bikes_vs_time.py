#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

# --- Paden ---
base_dir = Path.home() / "projects/data-workflow"
data_file = base_dir / "transformed_data/combined.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True) # Zorg dat de map bestaat

# --- Kleurdefinitie voor Modern Design ---
TEAL = "#008080"
DARK_GREY = "#333333"
LIGHT_GREY = "#CCCCCC"
SOFT_BLUE = "#66B2FF" # Nieuwe kleur voor scatter punten
RED_ACCENT = "#FF6347" # Nieuwe kleur voor trendlijn (iets zachter)

# --- Data inlezen ---
df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# --- Aggregatie naar Uurgemiddelden ---
# Zorg dat 'timestamp' de index is voor resample
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()

# --- X-as voorbereiding: Uur van de dag met verschuiving ---
# We willen de uren weergeven, maar de 'dag' laten starten om 3:00 uur 's nachts
# zodat de piek rond de spits niet wordt gesplitst.
# Creëer een 'time_of_day' kolom die de dag om 3:00 uur laat beginnen.
# Dit is de numerieke weergave van de uren, met 00:00 = 21.0, 03:00 = 0.0, etc.
df_hourly['shifted_hour'] = df_hourly['timestamp'].dt.hour + df_hourly['timestamp'].dt.minute / 60
df_hourly['shifted_hour'] = (df_hourly['shifted_hour'] - 3) % 24

# --- Lineaire regressie op shifted_hour ---
# Gebruik de geaggregeerde data voor de regressie (Uur vs Fietsen)
X_hourly = df_hourly["shifted_hour"].values.reshape(-1, 1)
y_hourly = df_hourly["total_free_bikes"].values

model_hourly = LinearRegression()
model_hourly.fit(X_hourly, y_hourly)
y_pred_hourly = model_hourly.predict(X_hourly)
mse_hourly = mean_squared_error(y_hourly, y_pred_hourly)

# --- Plotten: Aantal Fietsen per Uur (NU ECHT PRACHTIG!) ---
plt.style.use('seaborn-v0_8-darkgrid') # Basis voor een modern grid

fig, ax = plt.subplots(figsize=(12, 7)) # Grotere figuur voor impact

# Scatter plot van de uurgemiddelden
ax.scatter(df_hourly["shifted_hour"], df_hourly["total_free_bikes"], 
           label="Uurgemiddelden", 
           color=SOFT_BLUE, # Zachte blauwe punten
           alpha=0.7,      # Iets transparant voor overlap
           s=80,           # Grotere punten
           edgecolors='white', # Witte rand voor betere definitie
           linewidth=0.5)

# Trendlijn
# Sorteer de data op shifted_hour om een vloeiende lijn te garanderen
sorted_indices = np.argsort(X_hourly.flatten())
ax.plot(X_hourly[sorted_indices], y_pred_hourly[sorted_indices], 
        color=RED_ACCENT, # Opvallende rode lijn
        linewidth=2.5,   # Dikke lijn
        label=f"Trendlijn (MSE: {mse_hourly:.2f})") # MSE direct in de legend

# Titel en Labels
ax.set_title("Aantal Vrije Fietsen per Uur (Gent)", 
             fontsize=20, 
             color=DARK_GREY, 
             pad=20) # Ruimte boven de titel
ax.set_xlabel("Uur van de dag (Start 03:00)", 
              fontsize=14, 
              color=DARK_GREY, 
              labelpad=15)
ax.set_ylabel("Totaal aantal Vrije Fietsen", 
              fontsize=14, 
              color=DARK_GREY, 
              labelpad=15)

# X-as Ticks (met labels die duidelijk de verschuiving communiceren)
ax.set_xticks(np.arange(0, 24, 2)) # Elke 2 uur een tick
# Aangepaste labels om 0:00 en 2:00 te tonen, en de 3:00 start
x_tick_labels = [(f"{int((hour + 3) % 24):02d}:00") for hour in np.arange(0, 24, 2)]
ax.set_xticklabels(x_tick_labels, fontsize=12, color=DARK_GREY)

# Y-as Ticks
ax.tick_params(axis='y', labelsize=12, colors=DARK_GREY)

# Grid (lichter en subtieler)
ax.grid(True, linestyle='--', alpha=0.6, color=LIGHT_GREY) # Lichtere, gestippelde grid

# Legend
ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True, 
          edgecolor='lightgrey', facecolor='white', loc='upper left')

# Layout aanpassingen
plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Meer ruimte voor titel en onderkant
plt.gca().set_facecolor('white') # Achtergrond van het plotgebied wit maken
fig.patch.set_facecolor('white') # Achtergrond van de hele figuur wit maken

# Opslaan
plot_path = report_dir / "fiets_vs_uur.png"
plt.savefig(plot_path, dpi=300, bbox_inches='tight') # Hoge resolutie, trimt witruimte
plt.close()

print(f"📁 Prachtige grafiek opgeslagen in: {plot_path}")