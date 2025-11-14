#!/bin/bash
# activeer de virtuele omgeving
source /home/larsg/projects/data-workflow/venv/bin/activate

# ga naar projectmap
cd /home/larsg/projects/data-workflow

# --- Data ophalen ---
bash scripts/fetch_data.sh

# --- Data transformeren, analyseren en rapport genereren ---
bash scripts/transform_data.sh
python scripts/analyze_data.py
python scripts/generate_report.py

# --- Automatisch committen en pushen naar GitHub ---
git add -A
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
git push origin main
