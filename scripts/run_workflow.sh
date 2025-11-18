#!/bin/bash
# run_workflow.sh — volledige workflow (professioneel, log en feedback)

set -e
set -o pipefail
trap 'echo "❌ Fout op regel $LINENO"; exit 1' ERR

# Dynamisch pad bepalen (maakt het script portable voor docenten)
PROJECT_DIR="$HOME/projects/data-workflow"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

LOG="$LOG_DIR/cron.log"

echo "============================" >> "$LOG"
echo "Run start: $(date)" >> "$LOG"
echo "Project Data Workflow v1.0" >> "$LOG"

# --- Environment setup ---
# We voegen de venv bin toe aan PATH
export PATH="$PROJECT_DIR/venv/bin:$PATH"

# Activeer virtuele omgeving
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo "❌ Virtual environment niet gevonden op $PROJECT_DIR/venv" | tee -a "$LOG"
    exit 1
fi

cd "$PROJECT_DIR" || { echo "❌ Kan projectmap niet vinden"; exit 1; }

# --- Data ophalen (optioneel) ---
if [ "$1" != "skip-fetch" ]; then
    echo "🔹 Data ophalen..." | tee -a "$LOG"
    bash scripts/fetch_data.sh >> "$LOG" 2>&1 || { echo "❌ fetch_data.sh mislukt"; exit 1; }
else
    echo "⚡ Data ophalen overgeslagen (skip-fetch)" | tee -a "$LOG"
fi

# --- CSV heropbouwen ---
echo "🔹 CSV heropbouwen..." | tee -a "$LOG"
bash scripts/transform_data.sh >> "$LOG" 2>&1 || { echo "❌ transform_data.sh mislukt"; exit 1; }

# --- Analyses en grafieken ---
echo "🔹 Analyses en grafieken genereren..." | tee -a "$LOG"
python scripts/analyze_data.py >> "$LOG" 2>&1 || { echo "❌ analyze_data.py mislukt"; exit 1; }
python scripts/plot_bikes_vs_time.py >> "$LOG" 2>&1 || { echo "❌ plot_bikes_vs_time.py mislukt"; exit 1; }

# --- Markdown rapport ---
echo "🔹 Markdown rapport genereren..." | tee -a "$LOG"
python scripts/generate_report.py >> "$LOG" 2>&1 || { echo "❌ generate_report.py mislukt"; exit 1; }

# --- Professioneel PDF rapport ---
echo "🔹 PDF rapport genereren..." | tee -a "$LOG"
python scripts/generate_pdf_report.py >> "$LOG" 2>&1 || { echo "❌ generate_pdf_report.py mislukt"; exit 1; }

# --- Git commit & push ---
# Alleen uitvoeren als git geconfigureerd is
if [ -d ".git" ]; then
    echo "🔹 Git commit & push..." | tee -a "$LOG"
    git add -A >> "$LOG" 2>&1
    git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>> "$LOG" || echo "⚠️ Geen wijzigingen om te committen" >> "$LOG"
    git push origin main >> "$LOG" 2>&1 || echo "⚠️ Git push mislukt (check netwerk/credentials)" >> "$LOG"
else
    echo "⚠️ Geen git repository gevonden, slaat commit over." >> "$LOG"
fi

echo "Run eind: $(date)" >> "$LOG"
echo "============================" >> "$LOG"