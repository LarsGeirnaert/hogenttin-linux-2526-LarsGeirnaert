#!/bin/bash
# run_workflow.sh — volledige workflow (robust update)
# Usage: ./run_workflow.sh [skip-fetch]

set -e
set -o pipefail
trap 'echo "❌ Fout bij run_workflow.sh op regel $LINENO"; exit 1' ERR

LOG="$HOME/projects/data-workflow/logs/cron.log"

# Functie om log + terminal output tegelijk te doen
log_and_echo() {
    echo "$1" | tee -a "$LOG"
}

log_and_echo "============================"
log_and_echo "Run start: $(date)"

export PATH="$HOME/projects/data-workflow/venv/bin:$PATH"
export HOME="/home/larsg"
source "$HOME/projects/data-workflow/venv/bin/activate"
cd "$HOME/projects/data-workflow" || { echo "❌ Kan projectmap niet vinden"; exit 1; }

# --- Stap 1: Data ophalen (optioneel) ---
if [ "$1" != "skip-fetch" ]; then
    log_and_echo "🔹 Data ophalen..."
    bash scripts/fetch_data.sh | tee -a "$LOG"
else
    log_and_echo "🔹 Data ophalen overgeslagen (handmatig run)"
fi

# --- Stap 2: CSV heropbouwen ---
log_and_echo "🔹 CSV heropbouwen..."
bash scripts/transform_data.sh | tee -a "$LOG"
log_and_echo "✔ CSV bijgewerkt"

# --- Stap 3: Analyses + grafieken ---
log_and_echo "🔹 Analyses en grafieken..."
python scripts/analyze_data.py | tee -a "$LOG"
python scripts/plot_bikes_vs_time.py | tee -a "$LOG"
log_and_echo "✔ Analyses en grafieken afgerond"

# --- Stap 4: Markdown rapport genereren ---
log_and_echo "🔹 Markdown rapport genereren..."
python scripts/generate_report.py | tee -a "$LOG"
log_and_echo "✔ Markdown rapport klaar"

# --- Stap 5: PDF rapport genereren ---
log_and_echo "🔹 PDF rapport genereren..."
python scripts/generate_pdf_report.py | tee -a "$LOG"
log_and_echo "✔ PDF rapport klaar"

# --- Stap 6: Automatische commit & push ---
log_and_echo "🔹 Git commit & push..."
git add -A
git commit -m "Automatische update $(date '+%Y-%m-%d %H:%M:%S')" 2>> "$LOG" || log_and_echo "⚠️ Geen wijzigingen om te committen"
git push origin main >> "$LOG" 2>&1 || log_and_echo "⚠️ Git push mislukt"

log_and_echo "Run eind: $(date)"
log_and_echo "============================"
