#!/bin/bash
# activeer de virtuele omgeving
source /home/larsg/projects/data-workflow/venv/bin/activate

# ga naar projectmap
cd /home/larsg/projects/data-workflow

# voer workflow uit
# bash scripts/fetch_data.sh   # ✅ tijdelijk uitgeschakeld zodat geen nieuwe data wordt opgehaald
bash scripts/transform_data.sh
python scripts/analyze_data.py
python scripts/generate_report.py

# --- Automatisch committen en pushen naar GitHub ---
cd /home/larsg/projects/data-workflow || exit 1

# Voeg alle nieuwe/gewijzigde bestanden toe
git add -A

# Commit met timestamp (faalt niet als er niks te committen is)
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true

# Push naar de main branch
git push origin main
