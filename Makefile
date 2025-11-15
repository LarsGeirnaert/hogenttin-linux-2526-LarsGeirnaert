# Makefile - gebruikt pattern rules voor automatische update

RAW_WEATHER = raw_data/weather
RAW_BIKES = raw_data/bikes
TRANSFORMED = transformed_data
REPORTS = reports

# Pattern rule: nieuwe weather_*.json → herbouw combined.csv
$(TRANSFORMED)/combined.csv: $(wildcard $(RAW_WEATHER)/weather_*.json)
	@echo "Herbouw combined.csv..."
	@mkdir -p $(TRANSFORMED)
	@echo "timestamp,temperature,total_free_bikes" > $@
	@for weather in $^; do \
		base=$$(basename $$weather .json | cut -c8-); \
		bike_file="$(RAW_BIKES)/bikes_$$base.json"; \
		ts=$$(date -d "$${base:0:8} $${base:9:2}:${base:11:2}:${base:13:2}" --iso-8601=seconds); \
		temp=$$(jq -r '.current_weather.temperature // empty' $$weather); \
		if [[ -z "$$temp" || "$$temp" == "null" ]]; then temp="0"; fi; \
		if [[ -f "$$bike_file" ]]; then \
			bikes=$$(jq '[.network.stations[].free_bikes] | add // 0' "$$bike_file"); \
		else \
			bikes=0; \
		fi; \
		echo "$$ts,$$temp,$$bikes" >> $@; \
	done
	@echo "CSV bijgewerkt: $@"

# Rapporten afhankelijk van CSV
$(REPORTS)/report.md $(REPORTS)/report.pdf $(REPORTS)/%.png: $(TRANSFORMED)/combined.csv
	@echo "Genereer rapporten..."
	@mkdir -p $(REPORTS)
	@python scripts/analyze_data.py
	@python scripts/plot_bikes_vs_time.py
	@python scripts/generate_report.py
	@python scripts/generate_pdf_report.py

# Hoofd target
all: $(TRANSFORMED)/combined.csv $(REPORTS)/report.md $(REPORTS)/report.pdf

.PHONY: all clean
clean:
	@rm -f $(TRANSFORMED)/combined.csv
	@rm -rf $(REPORTS)/*
