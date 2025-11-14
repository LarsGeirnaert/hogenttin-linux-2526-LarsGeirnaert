#!/usr/bin/env python3
# analyze_data.py — analyseert data en maakt grafieken + weekday tabel

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

print("\n📈 Statistieken:")
print(f"Gemiddelde temperatuur: {mean_temp:.2f} °C")
print(f"Gemiddeld aantal vrije fietsen: {mean_bikes}")
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

# Grafiek opslaan
plt.figure(figsize=(8,5))
plt.scatter(df["temperature"], df["total_free_bikes"], label="Datapunten")
plt.plot(df["temperature"], y_pred, color="red", linewidth=2, label="Trendlijn")
plt.title("Relatie tussen temperatuur en aantal vrije fietsen (Gent)")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Vrije fietsen")
plt.grid(True)
plt.legend()

plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path)

print(f"\n📁 Grafiek opgeslagen in: {plot_path}")
