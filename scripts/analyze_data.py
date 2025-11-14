#!/usr/bin/env python3
# analyze_data.py — analyseert data en maakt grafieken + weekday tabel + dag/nacht statistieken

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

# Paden
base_dir = Path.home() / "projects" / "data-workflow"
data_file = base_dir / "transformed_data" / "combined.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)

# Data inlezen
df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

print("📊 Laatste 10 datapunten:")
print(df.tail(10))

# Temperatuur afronden + lichte jitter
np.random.seed(42)
df['temperature'] = df['temperature'].round(2) + np.random.uniform(-0.05, 0.05, size=len(df))

# Algemene statistieken
mean_temp = df["temperature"].mean()
mean_bikes = round(df["total_free_bikes"].mean())
corr = df["temperature"].corr(df["total_free_bikes"])

# Uurkolom voor dag/nacht
df["hour"] = df["timestamp"].dt.hour
# Overdag 7-19u
daytime_avg = round(df[(df["hour"] >= 7) & (df["hour"] < 19)]["total_free_bikes"].mean())
# Nacht 19-7u
nighttime_avg = round(pd.concat([df[df["hour"] >= 19]["total_free_bikes"], df[df["hour"] < 7]["total_free_bikes"]]).mean())

print("\n📈 Statistieken:")
print(f"Gemiddelde temperatuur: {mean_temp:.2f} °C")
print(f"Gemiddeld aantal vrije fietsen: {mean_bikes}")
print(f"Gemiddeld aantal fietsen overdag (7-19u): {daytime_avg}")
print(f"Gemiddeld aantal fietsen ’s nachts (19-7u): {nighttime_avg}")
print(f"Correlatie: {corr:.2f}")

# Weekdag tabel
df["weekday"] = df["timestamp"].dt.day_name()
weekday_stats = df.groupby("weekday")["total_free_bikes"].agg(
    Min="min",
    Max="max",
    Gemiddelde=lambda x: round(x.mean())
).reindex([
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
])

weekday_csv = report_dir / "weekday_stats.csv"
weekday_stats.to_csv(weekday_csv)
print(f"\n📁 Weekdag-statistieken opgeslagen in: {weekday_csv}")

# Lineaire regressie
X = df["temperature"].values.reshape(-1, 1)
y = df["total_free_bikes"].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

# Grafiek 1: Temp vs Fietsen
plt.figure(figsize=(8,5))
plt.scatter(df["temperature"], df["total_free_bikes"], color="blue", label="Datapunten")
plt.plot(df["temperature"], y_pred, color="red", linewidth=2, label="Trendlijn")
plt.title("Relatie tussen temperatuur en aantal vrije fietsen (Gent)")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Aantal vrije fietsen")
plt.grid(True)
plt.legend()
plt.text(min(df["temperature"]), max(df["total_free_bikes"])*0.9, f"MSE: {mse:.4f}", color="black")
plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path)
print(f"\n📁 Grafiek opgeslagen in: {plot_path}")
