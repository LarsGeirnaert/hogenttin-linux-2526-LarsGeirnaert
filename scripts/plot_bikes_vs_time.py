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
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60

# Lineaire regressie
X = df['hour'].values.reshape(-1, 1)
y = df['total_free_bikes'].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

# Grafiek maken (punten, geen lijnen)
plt.figure(figsize=(10,5))
plt.scatter(df['hour'], df['total_free_bikes'], color='blue', label='Aantal vrije fietsen')
plt.plot(df['hour'], y_pred, color='red', linewidth=2, label='Trendlijn (linear regression)')
plt.xlabel('Uur van de dag')
plt.ylabel('Aantal vrije fietsen')
plt.title('Aantal vrije fietsen door de dag (Gent)')
plt.xticks(range(0,25))  # uren 0-24
plt.grid(True)
plt.legend()
plt.text(min(df['hour']), max(df['total_free_bikes'])*0.9, f"MSE: {mse:.2f}", color='black')

# Opslaan
plot_path = report_dir / "fiets_vs_uur.png"
plt.savefig(plot_path)
print(f"📁 Grafiek opgeslagen in: {plot_path}")
