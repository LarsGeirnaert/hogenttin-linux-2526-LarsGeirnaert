#!/bin/bash
# transform_data.sh — combineert ruwe JSON-bestanden in één CSV-bestand

RAW_DIR="$HOME/projects/data-workflow/raw_data"
OUT_DIR="$HOME/projects/data-workflow/transformed_data"
mkdir -p "$OUT_DIR"

OUTFILE="$OUT_DIR/combined.csv"

# CSV-header
echo "timestamp,temperature,avg_free_bikes" > "$OUTFILE"

# Doorloop alle tijdstempels waarvoor zowel weather als bikes bestaan
for weather_file in "$RAW_DIR"/weather-*.json; do
    # Extracteer timestamp uit bestandsnaam
    base=$(basename "$weather_file" | sed 's/weather-//' | sed 's/.json//')
    bikes_file="$RAW_DIR/bikes-$base.json"

    # Controleer of bijhorende bikes-file bestaat
    if [[ -f "$bikes_file" ]]; then
        # 1️⃣ temperatuur ophalen uit JSON
        temp=$(jq -r '.current.temperature_2m' "$weather_file")

        # 2️⃣ gemiddelde vrije fietsen berekenen (fractie 0–1)
        avg_bikes=$(jq '[.network.stations[].free_bikes] | add / length' "$bikes_file")

        # 3️⃣ timestamp uit filename
        timestamp=$(date -d "${base:0:8} ${base:9:2}:${base:11:2}:${base:13:2}" --iso-8601=seconds 2>/dev/null || echo "$base")

        # 4️⃣ naar CSV schrijven
        echo "$timestamp,$temp,$avg_bikes" >> "$OUTFILE"
    fi
done

echo "✅ CSV-bestand gegenereerd: $OUTFILE"
