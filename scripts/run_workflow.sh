#!/bin/bash
# run_workflow.sh

# activeer virtuele omgeving
source /home/larsg/projects/data-workflow/venv/bin/activate

# ga naar projectmap
cd /home/larsg/projects/data-workflow

# Check parameter: als "--no-fetch" meegegeven, sla fetch over
if [[ "$1" != "--no-fetch" ]]; then
    echo "📥 Data ophalen..."
    bash scripts/fetch_data.sh
else
    echo "⚠️ Fetch overgeslagen, gebruik bestaande data"
fi

# transformeren, analyseren en rapport genereren
bash scripts/transform_data.sh
python scripts/analyze_data.py
python scripts/plot_bikes_vs_time.py
python scripts/generate_report.py

# automatisch commit & push
cd /home/larsg/projects/data-workflow || exit 1
git add -A
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
git push origin main
