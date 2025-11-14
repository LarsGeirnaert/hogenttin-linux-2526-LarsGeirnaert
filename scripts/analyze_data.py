#!/usr/bin/env python3
# analyze_data.py — leest combined.csv in en maakt analyse & grafiek

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
print("📊 Gegevens ingelezen:")

print("📊 Laatste 10 datapunten:")
print(df.tail(10))
# Temperatuur afronden op 2 decimalen + kleine random jitter toevoegen
np.random.seed(42)  # vaste seed voor reproduceerbaarheid; verwijder voor echte random jitter
df['temperature'] = df['temperature'].round(2) + np.random.uniform(-0.05, 0.05, size=len(df))

# Statistieken
mean_temp = df["temperature"].mean()
mean_bikes = df["total_free_bikes"].mean()
corr = df["temperature"].corr(df["total_free_bikes"])

print("\n📈 Statistieken:")
print(f"Gemiddelde temperatuur: {mean_temp:.2f} °C")
print(f"Gemiddeld aantal vrije fietsen: {mean_bikes:.1f}")
print(f"Correlatie tussen temperatuur en vrije fietsen: {corr:.2f}")

# Lineaire regressie
X = df["temperature"].values.reshape(-1, 1)
y = df["total_free_bikes"].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

print(f"Mean Squared Error (MSE): {mse:.4f}")

# Grafiek maken
plt.figure(figsize=(8,5))
plt.scatter(df["temperature"], df["total_free_bikes"], color="blue", label="Data punten")
plt.plot(df["temperature"], y_pred, color="red", linewidth=2, label="Trendlijn (linear regression)")
plt.title("Relatie tussen temperatuur en beschikbaarheid van deelfietsen (Gent)")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Aantal vrije fietsen")
plt.grid(True)
plt.legend()
plt.text(min(df["temperature"]), max(df["total_free_bikes"])*0.9, f"MSE: {mse:.4f}", color="black")

# Opslaan
plot_path = report_dir / "fiets_vs_temp.png"
plt.savefig(plot_path)
print(f"\n📁 Grafiek opgeslagen in: {plot_path}")
