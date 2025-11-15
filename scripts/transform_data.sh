
#!/bin/bash
# transform_data.sh — Alle weerdata in CSV, fietsdata optioneel (robust)
set -euo pipefail
trap 'echo "❌ Fout bij transform_data.sh op regel $LINENO"; exit 1' ERR

WEATHER_DIR="$HOME/projects/data-workflow/raw_data/weather"
BIKES_DIR="$HOME/projects/data-workflow/raw_data/bikes"
OUT_DIR="$HOME/projects/data-workflow/transformed_data"
mkdir -p "$OUT_DIR"

OUTFILE="$OUT_DIR/combined.csv"
TMPFILE="${OUTFILE}.tmp"

# Header
echo "timestamp,temperature,total_free_bikes" > "$TMPFILE"

# Build sorted list robustly (also werkt als veel bestanden of spaties in namen)
mapfile -t weather_files < <(printf '%s\n' "$WEATHER_DIR"/weather_*.json 2>/dev/null | sort)

total_files=0
processed=0
skipped=0

for weather_file in "${weather_files[@]}"; do
    # Als glob geen match geeft, staat het pad letterlijk in array; controleer file-existence
    if [[ ! -f "$weather_file" ]]; then
        continue
    fi

    total_files=$((total_files + 1))
    base=$(basename "$weather_file")
    # base expected format: weather_YYYYMMDD-HHMMSS.json
    # extract timestamp part after "weather_" and before ".json"
    stamp=${base#weather_}
    stamp=${stamp%.json}

    # maak een eenvoudige ISO-achtige timestamp zonder afhankelijkheid van date -d
    # stamp = YYYYMMDD-HHMMSS -> YYYY-MM-DDTHH:MM:SS
    if [[ ${#stamp} -ge 15 && "${stamp:8:1}" == "-" ]]; then
        yyyy=${stamp:0:4}
        mm=${stamp:4:2}
        dd=${stamp:6:2}
        hh=${stamp:9:2}
        min=${stamp:11:2}
        ss=${stamp:13:2}
        timestamp="${yyyy}-${mm}-${dd}T${hh}:${min}:${ss}"
    else
        # fallback: gebruik raw stamp
        timestamp="$stamp"
    fi

    # lees temperatuur (gebruik jq defaulting naar empty)
    temp=$(jq -r '.current_weather.temperature // empty' "$weather_file" 2>/dev/null || echo "")
    if [[ -z "$temp" ]]; then
        echo "⚠️ Ongeldige of ontbrekende temperatuur in $weather_file — overslaan" >&2
        skipped=$((skipped + 1))
        continue
    fi

    # zoek bijhorend bikes bestand
    bikes_file="$BIKES_DIR/bikes_${stamp}.json"
    if [[ -f "$bikes_file" ]]; then
        # gebruik jq met fallback naar 0 als add niets teruggeeft
        total_free=$(jq -r '([.network.stations[].free_bikes] | add) // 0' "$bikes_file" 2>/dev/null || echo "0")
        # zorg dat het een integer of 0 is
        if [[ -z "$total_free" || "$total_free" == "null" ]]; then
            total_free=0
        fi
    else
        # geen bike-file voor deze timestamp — gebruik 0 maar verwerk de weather-row
        total_free=0
    fi

    # append lijn — escape/quote niet nodig voor eenvoudige numerieke velden en timestamp zonder komma's
    echo "${timestamp},${temp},${total_free}" >> "$TMPFILE"
    processed=$((processed + 1))
done

# Atomisch vervangen
mv "$TMPFILE" "$OUTFILE"

echo "✅ CSV volledig herbouwd: $OUTFILE"
echo "🔢 Samenvatting: totale weather-bestanden gevonden: $total_files; verwerkt: $processed; overgeslagen (ongeldige temp): $skipped"
