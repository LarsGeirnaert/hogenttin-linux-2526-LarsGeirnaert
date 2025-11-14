#!/bin/bash
# run_workflow.sh

LOGFILE="/home/larsg/projects/data-workflow/logs/cron.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Run start" >> "$LOGFILE"

# activeer virtuele omgeving
source /home/larsg/projects/data-workflow/venv/bin/activate

# ga naar projectmap
cd /home/larsg/projects/data-workflow || exit 1

# Check parameter: als "--no-fetch" meegegeven, sla fetch over
if [[ "$1" != "--no-fetch" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Data ophalen..." >> "$LOGFILE"
    bash /home/larsg/projects/data-workflow/scripts/fetch_data.sh >> "$LOGFILE" 2>&1
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Fetch overgeslagen" >> "$LOGFILE"
fi

# transformeren, analyseren en rapport genereren
bash /home/larsg/projects/data-workflow/scripts/transform_data.sh >> "$LOGFILE" 2>&1
python /home/larsg/projects/data-workflow/scripts/analyze_data.py >> "$LOGFILE" 2>&1
python /home/larsg/projects/data-workflow/scripts/plot_bikes_vs_time.py >> "$LOGFILE" 2>&1
python /home/larsg/projects/data-workflow/scripts/generate_report.py >> "$LOGFILE" 2>&1
python /home/larsg/projects/data-workflow/scripts/generate_pdf_report.py >> "$LOGFILE" 2>&1

# automatisch commit & push
git add -A >> "$LOGFILE" 2>&1
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>> "$LOGFILE" || true
git push origin main >> "$LOGFILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Run eind" >> "$LOGFILE"
