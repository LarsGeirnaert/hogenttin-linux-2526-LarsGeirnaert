#!/bin/bash
# activeer de virtuele omgeving
source /home/larsg/projects/data-workflow/venv/bin/activate

# ga naar projectmap
cd /home/larsg/projects/data-workflow

# voer workflow uit
bash scripts/fetch_data.sh
bash scripts/transform_data.sh
python scripts/analyze_data.py
python scripts/generate_report.py

