#!/bin/bash
# transform_data.sh — Alle weerdata in CSV, fietsdata optioneel

set -e
set -o pipefail
trap 'echo "❌ Fout bij transform_data.sh"; exit 1' ERR

WEATHER_DIR="$HOME/projects/data-workflow/raw_data/weather"
BIKES_DIR="$HOME/projects/data-workflow/raw_data/bikes"
OUT_DIR="$HOME/projects/data-workflow/transformed_data"
mkdir -p "$OUT_DIR"

OUTFILE="$OUT_DIR/combined.csv"

# CSV header
echo "timestamp,temperature,total_free_bikes" > "$OUTFILE"

# Loop over alle weerbestanden, chronologisch
for weather_file in $(ls "$WEATHER_DIR"/weather_*.json | sort); do
    base=$(basename "$weather_file" | sed 's/weather_//' | sed 's/.json//')
    bikes_file="$BIKES_DIR/bikes_$base.json"

    # Timestamp
    timestamp=$(date -d "${base:0:8} ${base:9:2}:${base:11:2}:${base:13:2}" --iso-8601=seconds 2>/dev/null || echo "$base")

    # Temperatuur
    temp=$(jq -r '.current_weather.temperature' "$weather_file" 2>/dev/null)
    if [[ -z "$temp" || "$temp" == "null" ]]; then
        echo "⚠️ Ongeldige weerdata in $weather_file, overslaan"
        continue
    fi

    # Fietsdata (0 als ontbreekt)
    if [[ -f "$bikes_file" ]]; then
        total_free=$(jq '[.network.stations[].free_bikes] | add' "$bikes_file" 2>/dev/null)
        total_free=${total_free:-0}
    else
        total_free=0
    fi

    echo "$timestamp,$temp,$total_free" >> "$OUTFILE"
done

echo "✅ CSV volledig herbouwd: $OUTFILE"
