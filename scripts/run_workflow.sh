#!/bin/bash
set -e
set -o pipefail
trap 'echo "❌ Fout in run_workflow.sh"; exit 1' ERR

source /home/larsg/projects/data-workflow/venv/bin/activate
cd /home/larsg/projects/data-workflow

if [[ "$1" != "--no-fetch" ]]; then
    echo "📥 Data ophalen..."
    bash scripts/fetch_data.sh
else
    echo "⚠️ Fetch overgeslagen, gebruik bestaande data"
fi

# Transformeren, analyseren, rapport
bash scripts/transform_data.sh
python scripts/analyze_data.py
python scripts/plot_bikes_vs_time.py
python scripts/generate_report.py
python scripts/generate_pdf_report.py

# Git push met check
cd /home/larsg/projects/data-workflow || exit 1
git add -A
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
git push origin main || { echo "❌ Git push mislukt"; exit 1; }
