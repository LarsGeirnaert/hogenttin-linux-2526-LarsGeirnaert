#!/bin/bash
set -e
set -o pipefail
trap 'echo "❌ Fout bij fetch_data.sh"; exit 1' ERR

RAWDIR="$HOME/projects/data-workflow/raw_data"
WEATHER_DIR="$RAWDIR/weather"
BIKES_DIR="$RAWDIR/bikes"
LOGDIR="$HOME/projects/data-workflow/logs"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
LOGFILE="$LOGDIR/fetch-$TIMESTAMP.log"

mkdir -p "$WEATHER_DIR" "$BIKES_DIR" "$LOGDIR"

{
    echo "[$(date)] Start data ophalen..."

    # Weerdata
    if ! curl -s "https://api.open-meteo.com/v1/forecast?latitude=$LAT&longitude=$LON&current=temperature_2m" \
        -o "$WEATHER_FILE"; then
        echo "❌ Fout bij ophalen weerdata" >&2
        exit 1
    fi

    # Fietsdata
    if ! curl -s "https://api.citybik.es/v2/networks/donkey-gh" \
        -o "$BIKES_FILE"; then
        echo "❌ Fout bij ophalen fietsdata" >&2
        exit 1
    fi

    # Check of bestanden bestaan
    [[ -f "$WEATHER_FILE" ]] || { echo "❌ Weather file ontbreekt!"; exit 1; }
    [[ -f "$BIKES_FILE" ]] || { echo "❌ Bikes file ontbreekt!"; exit 1; }

    echo "[$(date)] Klaar!"
} >> "$LOGFILE" 2>&1
