#!/bin/bash
set -e
set -o pipefail
trap 'echo "❌ Fout bij transform_data.sh"; exit 1' ERR

WEATHER_DIR="$HOME/projects/data-workflow/raw_data/weather"
BIKES_DIR="$HOME/projects/data-workflow/raw_data/bikes"
OUT_DIR="$HOME/projects/data-workflow/transformed_data"
mkdir -p "$OUT_DIR"

OUTFILE="$OUT_DIR/combined.csv"
echo "timestamp,temperature,total_free_bikes" > "$OUTFILE"

for weather_file in "$WEATHER_DIR"/weather-*.json; do
    base=$(basename "$weather_file" | sed 's/weather-//' | sed 's/.json//')
    bikes_file="$BIKES_DIR/bikes-$base.json"

    [[ -f "$bikes_file" ]] || { echo "⚠️ Bikes file ontbreekt: $bikes_file"; continue; }

    temp=$(jq -r '.current.temperature_2m' "$weather_file" 2>/dev/null) || { echo "⚠️ JSON fout $weather_file"; continue; }
    total_free=$(jq '[.network.stations[].free_bikes] | add' "$bikes_file" 2>/dev/null) || { echo "⚠️ JSON fout $bikes_file"; continue; }

    timestamp=$(date -d "${base:0:8} ${base:9:2}:${base:11:2}:${base:13:2}" --iso-8601=seconds 2>/dev/null || echo "$base")

    echo "$timestamp,$temp,$total_free" >> "$OUTFILE"
done

[[ -f "$OUTFILE" ]] || { echo "❌ CSV niet aangemaakt!"; exit 1; }
echo "✅ CSV-bestand gegenereerd: $OUTFILE"
