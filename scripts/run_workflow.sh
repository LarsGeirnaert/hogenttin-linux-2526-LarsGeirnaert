#!/bin/bash
# run_workflow.sh — volledige workflow (robust update)
# Usage: ./run_workflow.sh [skip-fetch]

set -e
set -o pipefail
trap 'echo "❌ Fout bij run_workflow.sh op regel $LINENO"; exit 1' ERR

LOG="$HOME/projects/data-workflow/logs/cron.log"
echo "============================" >> "$LOG"
echo "Run start: $(date)" >> "$LOG"

export PATH="$HOME/projects/data-workflow/venv/bin:$PATH"
export HOME="/home/larsg"
source "$HOME/projects/data-workflow/venv/bin/activate"
cd "$HOME/projects/data-workflow" || { echo "❌ Kan projectmap niet vinden"; exit 1; }

# --- Stap 1: Data ophalen (optioneel) ---
if [ "$1" != "skip-fetch" ]; then
    echo "🔹 Data ophalen..." >> "$LOG"
    bash scripts/fetch_data.sh >> "$LOG" 2>&1 || { echo "❌ fetch_data.sh mislukt"; exit 1; }
else
    echo "🔹 Data ophalen overgeslagen (handmatig run)" >> "$LOG"
fi

# --- Stap 2 t/m 6: rest van workflow ---
echo "🔹 CSV heropbouwen..." >> "$LOG"
bash scripts/transform_data.sh >> "$LOG" 2>&1 || { echo "❌ transform_data.sh mislukt"; exit 1; }

echo "🔹 Analyses en grafieken..." >> "$LOG"
python scripts/analyze_data.py >> "$LOG" 2>&1 || { echo "❌ analyze_data.py mislukt"; exit 1; }
python scripts/plot_bikes_vs_time.py >> "$LOG" 2>&1 || { echo "❌ plot_bikes_vs_time.py mislukt"; exit 1; }

echo "🔹 Markdown rapport..." >> "$LOG"
python scripts/generate_report.py >> "$LOG" 2>&1 || { echo "❌ generate_report.py mislukt"; exit 1; }

echo "🔹 PDF rapport..." >> "$LOG"
python scripts/generate_pdf_report.py >> "$LOG" 2>&1 || { echo "❌ generate_pdf_report.py mislukt"; exit 1; }

echo "🔹 Git commit & push..." >> "$LOG"
git add -A >> "$LOG" 2>&1
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>> "$LOG" || echo "⚠️ Geen wijzigingen om te committen"
git push origin main >> "$LOG" 2>&1 || echo "⚠️ Git push mislukt"

echo "Run eind: $(date)" >> "$LOG"
echo "============================" >> "$LOG"
