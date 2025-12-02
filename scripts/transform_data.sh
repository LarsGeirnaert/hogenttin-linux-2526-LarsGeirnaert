#!/bin/bash
# transform_data.sh — Alleen datapunten met zowel weer als fietsdata
set -euo pipefail
trap 'echo "Fout bij transform_data.sh op regel $LINENO"; exit 1' ERR

WEATHER_DIR="$HOME/projects/data-workflow/raw_data/weather"
BIKES_DIR="$HOME/projects/data-workflow/raw_data/bikes"
OUT_DIR="$HOME/projects/data-workflow/transformed_data"
mkdir -p "$OUT_DIR"

OUTFILE="$OUT_DIR/combined.csv"
TMPFILE="${OUTFILE}.tmp"

# Header
echo "timestamp,temperature,total_free_bikes" > "$TMPFILE"

# Build sorted list robustly
mapfile -t weather_files < <(printf '%s\n' "$WEATHER_DIR"/weather_*.json 2>/dev/null | sort)

total_files=0
processed=0
skipped=0

for weather_file in "${weather_files[@]}"; do
    [[ -f "$weather_file" ]] || continue
    total_files=$((total_files + 1))

    base=$(basename "$weather_file")
    stamp=${base#weather_}
    stamp=${stamp%.json}

    # maak ISO-achtige timestamp
    if [[ ${#stamp} -ge 15 && "${stamp:8:1}" == "-" ]]; then
        yyyy=${stamp:0:4}; mm=${stamp:4:2}; dd=${stamp:6:2}
        hh=${stamp:9:2}; min=${stamp:11:2}; ss=${stamp:13:2}
        timestamp="${yyyy}-${mm}-${dd}T${hh}:${min}:${ss}"
    else
        timestamp="$stamp"
    fi

    # lees temperatuur
    temp=$(jq -r '(.current_weather.temperature // .current.temperature_2m) // empty' "$weather_file" 2>/dev/null || echo "")
    if [[ -z "$temp" ]]; then
        echo "⚠️ Ongeldige of ontbrekende temperatuur in $weather_file — overslaan" >&2
        skipped=$((skipped + 1))
        continue
    fi

    # bijhorend bikes bestand
    bikes_file="$BIKES_DIR/bikes_${stamp}.json"
    if [[ -f "$bikes_file" ]]; then
        total_free=$(jq -r '([.network.stations[].free_bikes] | add) // 0' "$bikes_file" 2>/dev/null || echo "0")
        [[ -z "$total_free" || "$total_free" == "null" ]] && total_free=0
    else
        total_free=0
    fi

    # ✅ Alleen toevoegen als total_free > 0
    if [[ "$total_free" -eq 0 ]]; then
        echo "Geen fietsdata voor $stamp — overslaan" >&2
        skipped=$((skipped + 1))
        continue
    fi

    echo "${timestamp},${temp},${total_free}" >> "$TMPFILE"
    processed=$((processed + 1))
done

# Atomisch vervangen
mv "$TMPFILE" "$OUTFILE"

echo "✅ CSV volledig herbouwd: $OUTFILE"
echo "🔢 Samenvatting: totale weather-bestanden gevonden: $total_files; verwerkt: $processed; overgeslagen: $skipped"
