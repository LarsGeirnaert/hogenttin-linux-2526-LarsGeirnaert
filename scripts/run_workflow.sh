#!/bin/bash
# run_workflow.sh — volledige workflow

set -e
set -o pipefail
trap 'echo "❌ Fout bij run_workflow.sh"; exit 1' ERR

# Log bestand
LOG="$HOME/projects/data-workflow/logs/cron.log"
echo "Run start: $(date)" >> "$LOG"

# Environment paths
export PATH=$HOME/projects/data-workflow/venv/bin:$PATH
export HOME=/home/larsg

# Activeer virtuele omgeving
source "$HOME/projects/data-workflow/venv/bin/activate"

# Ga naar projectmap
cd "$HOME/projects/data-workflow" || exit 1

# Data ophalen
bash scripts/fetch_data.sh >> "$LOG" 2>&1

# Transformeren, analyseren en rapport genereren
bash scripts/transform_data.sh >> "$LOG" 2>&1
python scripts/analyze_data.py >> "$LOG" 2>&1
python scripts/plot_bikes_vs_time.py >> "$LOG" 2>&1
python scripts/generate_report.py >> "$LOG" 2>&1
python scripts/generate_pdf_report.py >> "$LOG" 2>&1

# Automatisch commit & push
git add -A >> "$LOG" 2>&1
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>> "$LOG" || true
git push origin main >> "$LOG" 2>&1

echo "Run eind: $(date)" >> "$LOG"
