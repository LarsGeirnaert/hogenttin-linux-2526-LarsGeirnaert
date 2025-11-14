#!/bin/bash
# run_workflow.sh

# log bestand
LOG="/home/larsg/projects/data-workflow/logs/cron.log"
echo "Run start: $(date)" >> "$LOG"

# activeer virtuele omgeving
source /home/larsg/projects/data-workflow/venv/bin/activate

# ga naar projectmap
cd /home/larsg/projects/data-workflow || exit 1

# fetch data
bash scripts/fetch_data.sh >> "$LOG" 2>&1

# transformeren, analyseren en rapport genereren
bash scripts/transform_data.sh >> "$LOG" 2>&1
python scripts/analyze_data.py >> "$LOG" 2>&1
python scripts/plot_bikes_vs_time.py >> "$LOG" 2>&1
python scripts/generate_report.py >> "$LOG" 2>&1
python scripts/generate_pdf_report.py >> "$LOG" 2>&1

# commit & push
git add -A >> "$LOG" 2>&1
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>> "$LOG" || true
git push origin main >> "$LOG" 2>&1

echo "Run eind: $(date)" >> "$LOG"
