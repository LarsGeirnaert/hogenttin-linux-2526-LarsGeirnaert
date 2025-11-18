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

# --- Data inlezen ---
df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

print("📊 Laatste 10 datapunten (Originele 15-min data):")
print(df.tail(10))

# --- 1. Statistieken berekenen (OP ALLE RUWE DATA) ---
mean_temp = df["temperature"].mean()
mean_bikes = round(df["total_free_bikes"].mean())

# Gemiddeld aantal fietsen overdag/nacht (veilig met NaN)
day_data = df[(df['timestamp'].dt.hour >= 7) & (df['timestamp'].dt.hour < 19)]
day_avg_bikes = round(day_data['total_free_bikes'].mean()) if not day_data.empty else 0

night_data = df[(df['timestamp'].dt.hour < 7) | (df['timestamp'].dt.hour >= 19)]
night_avg_bikes = round(night_data['total_free_bikes'].mean()) if not night_data.empty else 0

# Correlatie (veilig)
corr = df["temperature"].corr(df["total_free_bikes"])
corr = corr if not pd.isna(corr) else 0

print("\n📈 Statistieken (Gebaseerd op werkelijke metingen):")
print(f"Gemiddelde temperatuur: {mean_temp:.2f} °C")
print(f"Gemiddeld aantal vrije fietsen: {mean_bikes}")
print(f"Gemiddeld aantal fietsen overdag (7-19u): {day_avg_bikes}")
print(f"Gemiddeld aantal fietsen ’s nachts (19-7u): {night_avg_bikes}")
print(f"Correlatie: {corr:.2f}")

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

# NIEUWE CODE: Zet de fiets-kolommen om naar nullable integers (Int64)
# Dit verwijdert de .0 en handelt NaN/lege groepen correct af.
bike_cols = ["Min", "Max", "Gemiddelde_fietsen"]
for col in bike_cols:
    # Round is nodig omdat 'min' en 'max' floats teruggeven, daarna converteren naar integer
    weekday_stats[col] = weekday_stats[col].round(0).astype('Int64')

weekday_csv = report_dir / "weekday_stats.csv"
weekday_stats.to_csv(weekday_csv)
print(f"\n📁 Weekdag-statistieken opgeslagen in: {weekday_csv}")

# --- 2. Data Aggregatie (VOOR GRAFIEK) ---
df_hourly = df.set_index('timestamp').resample('H').mean(numeric_only=True).dropna().reset_index()


# --- 3. Lineaire regressie (past model op RUWE data) ---
X = df["temperature"].values.reshape(-1, 1)
y = df["total_free_bikes"].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)


# --- 4. Grafiek 1: Temperatuur vs. Vrije Fietsen (Uurgemiddelden) ---
plt.style.use('seaborn-v0_8-darkgrid') # Betere stijl
fig, ax = plt.subplots(figsize=(10, 6)) # Grotere figuur

# Plot de GEAGGREGEERDE punten
ax.scatter(df_hourly["temperature"], df_hourly["total_free_bikes"], 
           label="Uurgemiddelden", alpha=0.6, s=50, color='#1f77b4') # Grotere punten, mooie kleur

# Plot de trendlijn (die is getraind op de ruwe data)
ax.plot(df["temperature"], y_pred, color='#d62728', linewidth=2.5, label="Trendlijn (ruwe data)") # Rode lijn

ax.set_title("Relatie tussen temperatuur en aantal vrije fietsen (Gent)", fontsize=16, fontweight='bold')
ax.set_xlabel("Temperatuur (°C)", fontsize=12)
ax.set_ylabel("Vrije fietsen", fontsize=12)
ax.grid(True, linestyle='--', alpha=0.7) # Duidelijker grid
ax.legend(fontsize=10, loc='upper left') # Legend op logische plek

# Verwijder top en rechter spine voor een cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Voeg tekst toe voor de correlatiecoëfficiënt
ax.text(0.05, 0.95, f'Correlatie: {corr:.2f}', transform=ax.transAxes, 
        fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.7))


plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path, dpi=300, bbox_inches='tight') # Hogere resolutie, geen witruimte
plt.close()
print(f"📁 Grafiek opgeslagen in: {plot_path}")