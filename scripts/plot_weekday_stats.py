#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# --- Paden ---
base_dir = Path.home() / "projects/data-workflow"
weekday_file = base_dir / "reports/weekday_stats.csv"
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)

# --- Kleuren & Stijl (Consistent met de rest) ---
DARK_BLUE = "#004C99"
ACCENT_RED = "#D62728"
TEXT_COLOR = "#333333"
GRID_COLOR = "#999999"

# --- Data inlezen ---
df = pd.read_csv(weekday_file)

# --- VERTALING & SORTEREN (HIER ZAT DE FOUT) ---
# 1. Definieer de vertaling van Engels (uit CSV) naar Nederlands (voor Grafiek)
day_map = {
    "Monday": "Maandag", "Tuesday": "Dinsdag", "Wednesday": "Woensdag",
    "Thursday": "Donderdag", "Friday": "Vrijdag", "Saturday": "Zaterdag", "Sunday": "Zondag"
}

# 2. Pas de vertaling toe. Als de CSV al Nederlands is, doet dit niets (veilig).
df['weekday'] = df['weekday'].map(day_map).fillna(df['weekday'])

# 3. Definieer de Nederlandse volgorde
dutch_order = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]

# 4. Zet om naar Categorical type voor juiste sortering
df['weekday'] = pd.Categorical(df['weekday'], categories=dutch_order, ordered=True)
df = df.sort_values('weekday')

# --- Bereken Error Bars (Verschil tussen Gemiddelde en Min/Max) ---
# Matplotlib errorbars verwachten de afstand vanaf het gemiddelde
# y_err = [afstand_naar_onder, afstand_naar_boven]
y_err_min = df['Gemiddelde_fietsen'] - df['Min']
y_err_max = df['Max'] - df['Gemiddelde_fietsen']
y_err = [y_err_min, y_err_max]

# --- GRAFIEK MAKEN ---
plt.style.use('seaborn-v0_8-whitegrid') # Witte achtergrond

fig, ax = plt.subplots(figsize=(12, 7))

# Het Rooster (Grid)
ax.grid(True, which='major', axis='y', color=GRID_COLOR, linestyle='-', linewidth=0.8, alpha=0.5, zorder=0)

# Staven (Gemiddelde)
bars = ax.bar(df['weekday'], df['Gemiddelde_fietsen'], 
              color=DARK_BLUE, 
              alpha=0.85, 
              width=0.6,
              edgecolor='white',
              linewidth=1,
              zorder=3,
              label='Gemiddeld aantal')

# Error Bars (Min/Max bereik)
ax.errorbar(df['weekday'], df['Gemiddelde_fietsen'], yerr=y_err, 
            fmt='none', # Geen punten verbinden
            ecolor=ACCENT_RED, # Rode kleur voor het bereik
            elinewidth=2, 
            capsize=5, # Breedte van de streepjes boven/onder
            capthick=2,
            zorder=4,
            label='Bereik (Min-Max)')

# Waarde labels bovenop de staven
for bar in bars:
    height = bar.get_height()
    # Check op NaN om errors te voorkomen als data leeg is
    if not np.isnan(height):
        ax.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold', color=TEXT_COLOR)

# Labels & Titel
ax.set_title("Vrije Fietsen per Weekdag (Gemiddelde & Bereik)", fontsize=18, fontweight='bold', color=TEXT_COLOR, pad=20)
ax.set_xlabel("Weekdag", fontsize=13, color=TEXT_COLOR)
ax.set_ylabel("Aantal Vrije Fietsen", fontsize=13, color=TEXT_COLOR)

# Y-as limieten iets ruimer zetten zodat labels passen
# Veiligheidscheck voor lege data
if not df.empty:
    y_min_limit = df['Min'].min() - 20
    y_max_limit = df['Max'].max() + 20
    ax.set_ylim(bottom=y_min_limit, top=y_max_limit)

# Legend
ax.legend(fontsize=11, frameon=True, facecolor='white', edgecolor=GRID_COLOR, framealpha=1, loc='upper right')

plt.tight_layout()

# Opslaan
plot_path = report_dir / "weekday_bars.png"
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"📁 Prachtige weekdag-grafiek opgeslagen in: {plot_path}")