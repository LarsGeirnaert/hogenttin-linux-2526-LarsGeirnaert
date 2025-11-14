#!/bin/bash
# fetch_data.sh — Ophalen van weerdata en fietsdata

set -e
set -o pipefail
trap 'echo "❌ Fout bij fetch_data.sh"; exit 1' ERR

# --- Directories ---
RAWDIR="$HOME/projects/data-workflow/raw_data"
WEATHER_DIR="$RAWDIR/weather"
BIKES_DIR="$RAWDIR/bikes"
LOGDIR="$HOME/projects/data-workflow/logs"

mkdir -p "$WEATHER_DIR" "$BIKES_DIR" "$LOGDIR"

# --- Logbestand ---
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
LOGFILE="$LOGDIR/fetch-$TIMESTAMP.log"

# --- Locatie Gent ---
LAT=51.0543
LON=3.7174

# --- Bestandsnamen ---
WEATHER_FILE="$WEATHER_DIR/weather_$TIMESTAMP.json"
BIKES_FILE="$BIKES_DIR/bikes_$TIMESTAMP.json"

{
    echo "[$(date)] Start data ophalen..."

    # --- Weerdata ---
    echo "Ophalen weerdata..."
    if ! curl -s "https://api.open-meteo.com/v1/forecast?latitude=$LAT&longitude=$LON&current_weather=true" \
        -o "$WEATHER_FILE"; then
        echo "❌ Fout bij ophalen weerdata" >&2
        exit 1
    fi
    echo "Weerdata opgeslagen in $WEATHER_FILE"

    # --- Fietsdata ---
    echo "Ophalen fietsdata..."
    if ! curl -s "https://api.citybik.es/v2/networks/donkey-gh" \
        -o "$BIKES_FILE"; then
        echo "❌ Fout bij ophalen fietsdata" >&2
        exit 1
    fi
    echo "Fietsdata opgeslagen in $BIKES_FILE"

    # --- Check bestanden ---
    [[ -f "$WEATHER_FILE" ]] || { echo "❌ Weather file ontbreekt!"; exit 1; }
    [[ -f "$BIKES_FILE" ]] || { echo "❌ Bikes file ontbreekt!"; exit 1; }

    echo "[$(date)] Klaar met ophalen data."
} >> "$LOGFILE" 2>&1
