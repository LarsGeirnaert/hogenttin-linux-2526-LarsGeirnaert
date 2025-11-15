#!/bin/bash
# transform_data.sh — Transformeer JSON naar CSV (veilig voor ontbrekende data)

set -e
set -o pipefail
trap 'echo "❌ Fout bij transform_data.sh"; exit 1' ERR

WEATHER_DIR="$HOME/projects/data-workflow/raw_data/weather"
BIKES_DIR="$HOME/projects/data-workflow/raw_data/bikes"
OUT_DIR="$HOME/projects/data-workflow/transformed_data"
mkdir -p "$OUT_DIR"

OUTFILE="$OUT_DIR/combined.csv"

# CSV volledig herbouwen
echo "timestamp,temperature,total_free_bikes" > "$OUTFILE"

for weather_file in "$WEATHER_DIR"/weather_*.json; do
    base=$(basename "$weather_file" | sed 's/weather_//' | sed 's/.json//')
    bikes_file="$BIKES_DIR/bikes_$base.json"

    timestamp=$(date -d "${base:0:8} ${base:9:2}:${base:11:2}:${base:13:2}" --iso-8601=seconds 2>/dev/null || echo "$base")

    # Weerdata
    temp=$(jq -r '.current_weather.temperature' "$weather_file" 2>/dev/null)
    if [[ -z "$temp" || "$temp" == "null" ]]; then
        echo "⚠️ Weerdata ontbreekt of ongeldig in $weather_file, overslaan"
        continue
    fi

    # Fietsdata, default 0 als bestand ontbreekt
    if [[ -f "$bikes_file" ]]; then
        total_free=$(jq '[.network.stations[].free_bikes] | add' "$bikes_file" 2>/dev/null)
        total_free=${total_free:-0}
    else
        echo "⚠️ Bikes file ontbreekt: $bikes_file → gebruik 0"
        total_free=0
    fi

    echo "$timestamp,$temp,$total_free" >> "$OUTFILE"
done

echo "✅ CSV volledig herbouwd: $OUTFILE"
