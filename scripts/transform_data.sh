#!/bin/bash
# transform_data.sh — Transformeer JSON naar CSV

set -e
set -o pipefail
trap 'echo "❌ Fout bij transform_data.sh"; exit 1' ERR

WEATHER_DIR="$HOME/projects/data-workflow/raw_data/weather"
BIKES_DIR="$HOME/projects/data-workflow/raw_data/bikes"
OUT_DIR="$HOME/projects/data-workflow/transformed_data"
mkdir -p "$OUT_DIR"

OUTFILE="$OUT_DIR/combined.csv"

# Maak CSV met header als die nog niet bestaat
if [[ ! -f "$OUTFILE" ]]; then
    echo "timestamp,temperature,total_free_bikes" > "$OUTFILE"
fi

# Bestaande timestamps
existing=$(tail -n +2 "$OUTFILE" | cut -d',' -f1)

for weather_file in "$WEATHER_DIR"/weather_*.json; do
    base=$(basename "$weather_file" | sed 's/weather_//' | sed 's/.json//')
    bikes_file="$BIKES_DIR/bikes_$base.json"

    [[ -f "$bikes_file" ]] || { echo "⚠️ Bikes file ontbreekt: $bikes_file"; continue; }

    timestamp=$(date -d "${base:0:8} ${base:9:2}:${base:11:2}:${base:13:2}" --iso-8601=seconds 2>/dev/null || echo "$base")

    # Voeg alleen toe als nog niet in CSV
    if echo "$existing" | grep -qx "$timestamp"; then
        continue
    fi

    temp=$(jq -r '.current_weather.temperature' "$weather_file") || { echo "⚠️ JSON fout $weather_file"; continue; }
    total_free=$(jq '[.network.stations[].free_bikes] | add' "$bikes_file") || { echo "⚠️ JSON fout $bikes_file"; continue; }

    echo "$timestamp,$temp,$total_free" >> "$OUTFILE"
done

echo "✅ CSV-bestand bijgewerkt: $OUTFILE"
