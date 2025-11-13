#!/bin/bash
cd /home/larsg/projects/data-workflow

# Fetch data
./scripts/fetch_data.sh

# Transform data
./scripts/transform_data.sh

# Analyse data (grafiek)
python3 scripts/analyze_data.py

# Genereer rapport
python3 scripts/generate_report.py

# Voeg nieuwe bestanden toe en push naar GitHub
git add raw_data/ transformed_data/ reports/
git commit -m "Automatische update $(date +'%Y-%m-%d %H:%M:%S')"
git push origin main
