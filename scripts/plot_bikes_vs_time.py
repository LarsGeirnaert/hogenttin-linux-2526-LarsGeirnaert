#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Paden
base_dir = Path.home() / "projects" / "data-workflow"
data_file = base_dir / "transformed_data" / "combined.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)

# Data inlezen
df = pd.read_csv(data_file)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60

# Grafiek maken
plt.figure(figsize=(10,5))
plt.scatter(df['hour'], df['total_free_bikes'], color='blue', label='Aantal vrije fietsen')
plt.plot(df['hour'], df['total_free_bikes'], color='lightblue', linewidth=1)
plt.xlabel('Uur van de dag')
plt.ylabel('Aantal vrije fietsen')
plt.title('Aantal vrije fietsen door de dag (Gent)')
plt.xticks(range(0,25))  # uren 0-24
plt.grid(True)
plt.legend()

# Opslaan
plot_path = report_dir / "fiets_vs_uur.png"
plt.savefig(plot_path)
print(f"📁 Grafiek opgeslagen in: {plot_path}")
