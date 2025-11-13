#!/bin/bash
# fetch_data.sh — haalt weer- en fietsdata op en slaat ze op met timestamp

# === Instellingen ===
OUTDIR="$HOME/projects/data-workflow/raw_data"
LOGDIR="$HOME/projects/data-workflow/logs"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
LOGFILE="$LOGDIR/fetch-$TIMESTAMP.log"

# === Locatie Gent ===
LAT="51.05"
LON="3.72"

# === Outputbestanden ===
WEATHER_FILE="$OUTDIR/weather-$TIMESTAMP.json"
BIKES_FILE="$OUTDIR/bikes-$TIMESTAMP.json"

mkdir -p "$OUTDIR" "$LOGDIR"

{
  echo "[$(date)] Start data ophalen..."

  # 🌡️ Weerdata via Open-Meteo
  curl -s "https://api.open-meteo.com/v1/forecast?latitude=$LAT&longitude=$LON&current=temperature_2m" \
    -o "$WEATHER_FILE"
  echo "Weerdata opgeslagen in $WEATHER_FILE"

  # 🚲 Deelfietsdata via CityBikes API (Donkey Republic Gent)
  curl -s "https://api.citybik.es/v2/networks/donkey-gh" \
    -o "$BIKES_FILE"
  echo "Fietsdata opgeslagen in $BIKES_FILE"


  echo "[$(date)] Klaar!"
} >> "$LOGFILE" 2>&1
