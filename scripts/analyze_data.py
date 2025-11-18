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

print("📊 Laatste 10 datapunten (Originele data):")
print(df.tail(10))

# --- 1. Statistieken berekenen (OP ORIGINELE DATA) ---
# We berekenen dit EERST, zodat de 'jitter' de cijfers niet beïnvloedt.
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

weekday_csv = report_dir / "weekday_stats.csv"
weekday_stats.to_csv(weekday_csv)
print(f"\n📁 Weekdag-statistieken opgeslagen in: {weekday_csv}")

# --- 2. Lineaire Regressie ---
X = df["temperature"].values.reshape(-1, 1)
y = df["total_free_bikes"].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

# --- 3. Visualisatie (MET JITTER) ---
# Hier maken we een TIJDELIJKE variabele met ruis, enkel voor de grafiek.
# Dit voorkomt 'overplotting' zonder de data te vervuilen.
np.random.seed(42)
jittered_temp = df["temperature"] + np.random.uniform(-0.2, 0.2, size=len(df))

plt.figure(figsize=(8,5))
# alpha=0.5 zorgt voor transparantie, zodat je ziet waar veel punten op elkaar liggen
plt.scatter(jittered_temp, df["total_free_bikes"], label="Datapunten (met jitter)", alpha=0.5)
plt.plot(df["temperature"], y_pred, color="red", linewidth=2, label="Trendlijn")

plt.title("Relatie tussen temperatuur en aantal vrije fietsen (Gent)")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Vrije fietsen")
plt.grid(True)
plt.legend()

plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path)
plt.close()
print(f"\n📁 Grafiek opgeslagen in: {plot_path}")