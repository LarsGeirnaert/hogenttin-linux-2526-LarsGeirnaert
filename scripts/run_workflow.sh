#!/bin/bash
# run_workflow.sh — volledige workflow (professioneel, log en feedback)

set -e
set -o pipefail
trap 'echo "❌ Fout op regel $LINENO"; exit 1' ERR

LOG="$HOME/projects/data-workflow/logs/cron.log"
echo "============================" >> "$LOG"
echo "Run start: $(date)" >> "$LOG"
echo "Project Data Workflow v1.0" >> "$LOG"

# --- Environment paths ---
export PATH="$HOME/projects/data-workflow/venv/bin:$PATH"
export HOME="/home/larsg"

# Activeer virtuele omgeving
source "$HOME/projects/data-workflow/venv/bin/activate"

cd "$HOME/projects/data-workflow" || { echo "❌ Kan projectmap niet vinden"; exit 1; }

# --- Data ophalen (optioneel) ---
if [ "$1" != "skip-fetch" ]; then
    echo "🔹 Data ophalen..." | tee -a "$LOG"
    bash scripts/fetch_data.sh >> "$LOG" 2>&1 || { echo "❌ fetch_data.sh mislukt"; exit 1; }
else
    echo "⚡ Data ophalen overgeslagen (skip-fetch)" | tee -a "$LOG"
fi

# --- CSV heropbouwen ---
echo "🔹 CSV heropbouwen..." | tee -a "$LOG"
bash scripts/transform_data.sh >> "$LOG" 2>&1 || { echo "❌ transform_data.sh mislukt"; exit 1; }

# --- Analyses en grafieken ---
echo "🔹 Analyses en grafieken genereren..." | tee -a "$LOG"
python scripts/analyze_data.py >> "$LOG" 2>&1 || { echo "❌ analyze_data.py mislukt"; exit 1; }
python scripts/plot_bikes_vs_time.py >> "$LOG" 2>&1 || { echo "❌ plot_bikes_vs_time.py mislukt"; exit 1; }

# --- Markdown rapport ---
echo "🔹 Markdown rapport genereren..." | tee -a "$LOG"
python scripts/generate_report.py >> "$LOG" 2>&1 || { echo "❌ generate_report.py mislukt"; exit 1; }

# --- Professioneel PDF rapport ---
echo "🔹 PDF rapport genereren..." | tee -a "$LOG"
python scripts/generate_pdf_report.py >> "$LOG" 2>&1 || { echo "❌ generate_pdf_report.py mislukt"; exit 1; }

# --- Git commit & push ---
echo "🔹 Git commit & push..." | tee -a "$LOG"
git add -A >> "$LOG" 2>&1
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>> "$LOG" || echo "⚠️ Geen wijzigingen om te committen"
git push origin main >> "$LOG" 2>&1 || echo "⚠️ Git push mislukt"

echo "Run eind: $(date)" >> "$LOG"
echo "============================" >> "$LOG"
