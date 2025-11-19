# Data Workflow: Temperatuur vs. Aantal Vrije Fietsen in Gent

## 0. Relevante links

- [GitHub repository](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert)
- Panopto demo opname: [link hier]

---

## 1. Beschrijving van de workflow

Deze workflow verzamelt automatisch gegevens over het weer (temperatuur) en het aantal beschikbare deelfietsen in Gent. De data wordt verwerkt, geanalyseerd en gevisualiseerd, waarna de resultaten automatisch naar GitHub worden gepusht.

### Fasen van de workflow

1. **Data ophalen**  
   JSON-bestanden van de Gentse weer-API en CityBikes API worden opgehaald op regelmatige tijdstippen.

2. **Data transformeren**  
   Omzetten van JSON naar CSV (combined.csv) met relevante kolommen en timestamps. Dit proces wordt volledig uitgevoerd met Linux-tools (Bash scripting en jq voor JSON-parsing), zonder Python. De data uit de verschillende bronnen wordt op tijdstempel gecombineerd tot één dataset.
3. **Data analyseren**  
   Berekenen van statistieken, correlaties en genereren van grafieken (temperatuur vs vrije fietsen, fietsen per uur).

4. **Rapport genereren**  
   Aanmaken van Markdown-rapport (`report.md`) en professioneel PDF-rapport (`report.pdf`) met grafieken en tabellen.

5. **Automatisering**  
   De gehele workflow wordt aangestuurd door run_workflow.sh en kan elk kwartier automatisch draaien via een cron-job. De resultaten worden automatisch vastgelegd in Git en naar GitHub gepusht.

---

## 2. Data

### Bronnen

- **Weer**: publieke weer-API voor Gent
- **Fietsen**: CityBikes API (Donkey Republic / Gent netwerk)

### Periode

Vanaf 13 november 2025, met een interval van 15 minuten (automatisch).

### Bestandsindeling

- **Ruwe data**: JSON-bestanden in `raw_data/`
- **Verwerkte data**: CSV-bestand `transformed_data/combined.csv`

### CSV-header

- `timestamp`: ISO 8601 datum/tijd van de meting
- `temperature`: temperatuur in graden Celsius
- `total_free_bikes`: totaal aantal vrije fietsen in Gent

---

## 3. Directorystructuur

```
data-workflow/
├── README.md
├── logs/ # Automatische logbestanden per fetch-run
│ ├── cron.log
│ ├── cron_reboot.log
│ ├── cron_test.log
│ └── fetch-*.log
├── raw_data/ # Ruwe JSON-data
│ ├── bikes
│ └── weather
├── reports/
│ ├── fiets_vs_temp.png
│ ├── fiets_vs_uur.png
│ ├── weekday_bars.png
│ ├── report.md
│ ├── report.pdf
│ └── weekday_stats.csv
├── scripts/
│ ├── analyze_data.py
│ ├── fetch_data.sh
│ ├── generate_pdf_report.py
│ ├── generate_report.py
│ ├── plot_bikes_vs_time.py
│ ├── plot_weekday_stats.py
│ ├── run_workflow.sh
│ └── transform_data.sh
├── transformed_data/ # Verwerkte CSV-bestanden
│ └── combined.csv
└── venv/ # Virtuele Python-omgeving
```

## 4. Dependencies

- Python 3.11

- jq (voor JSON parsing in bash)

- curl (voor data ophalen via API)

- pandas

- matplotlib

- scikit-learn

- reportlab

## 5. Gebruiksaanwijzing

### 5.1 Automatisch uitvoeren (elk kwartier)

De workflow kan automatisch elk kwartier draaien via een cron-job. Hierbij wordt nieuwe data opgehaald, en worden alle documenten, grafieken en het CSV-bestand bijgewerkt. Voeg bijvoorbeeld deze regel toe aan je crontab:

`*/15 * * * * cd /home/larsg/projects/data-workflow && ./scripts/run_workflow.sh`

### 5.2 Handmatig testen

Om de workflow handmatig uit te voeren zonder nieuwe data op te halen:

```
cd ~/projects/data-workflow
./scripts/run_workflow.sh skip-fetch

```

Om enkel de CSV bij te werken (transformatie van ruwe data):

```
bash scripts/transform_data.sh
```

Om alleen analyse en grafieken te genereren:

```
python scripts/analyze_data.py
python scripts/plot_bikes_vs_time.py
```

wordt geen nieuwe data opgehaald. Alleen de verwerkte bestanden, grafieken en rapporten worden bijgewerkt op basis van de reeds aanwezige ruwe data. Dit is handig om snel te testen of de analyse en visualisaties correct werken.

## 6. Resultaten bekijken

- **Verwerkte CSV**: [transformed_data/combined.csv](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/transformed_data/combined.csv)

- **Grafiek 1 (Fietsgebruik vs temperatuur)**: [reports/fiets_vs_temp.png](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/fiets_vs_temp.png)

- **Grafiek 2 (Fietsgebruik vs uur)**: [reports/fiets_vs_uur.png](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/fiets_vs_uur.png)

- **Grafiek 3 (Weekdag analyse)**: [reports/weekday_bars.png](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/weekday_bars.png)

- **Markdown-rapport**: [reports/report.md](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/report.md)

- **PDF-rapport**: [reports/report.pdf](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/report.pdf)

Opmerking: de workflow pusht automatisch nieuwe gegevens en rapporten naar GitHub, zodat alles online up-to-date blijft.

## 7. Extra visualisaties en PDF-rapport

### 7.1 Data Aggregatie voor Visualisatie

De ruwe data wordt elke 15 minuten verzameld. Om de grafieken helder en leesbaar te houden, past de analysefase een aggregatietechniek toe:

- Statistieken (correlatie, gemiddelden) worden berekend op de volledige 15-minuten dataset om maximale nauwkeurigheid te garanderen.

- Grafieken gebruiken uurgemiddelden (berekend via resample('H').mean()) om overplotting tegen te gaan en de trends per uur duidelijk zichtbaar te maken. Dit vereiste het gebruik van de parameter numeric_only=True in Pandas om een TypeError te voorkomen bij het aggregeren van niet-numerieke kolommen.

### 7.2 Extra grafiek: aantal vrije fietsen per uur

Een bijkomende visualisatie werd toegevoegd: fietsen vs. uur van de dag → [reports/fiets_vs_uur.png](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/fiets_vs_uur.png)

Deze grafiek toont hoe het totaal aantal vrije fietsen in Gent varieert per uur van de dag. Ze geeft inzichten zoals:

- op welke momenten er typisch meer of minder fietsen beschikbaar zijn

- piekmomenten rond ochtend- en avondspits

- eventuele trends in gebruiksdrukte tijdens weekends of koude dagen

- hoe de beschikbaarheid doorheen de dag evolueert

Deze grafiek is aanvullend op de temperatuur-analyse en helpt om te bepalen of variaties te wijten zijn aan dagelijks ritme in plaats van aan weersomstandigheden.

### 7.3 Extra grafiek: Weekdag-analyse met spreiding (Error Bars)

Een derde visualisatie werd toegevoegd via het script plot_weekday_stats.py: Vrije fietsen per weekdag → reports/weekday_bars.png

Deze staafgrafiek toont niet enkel het gemiddelde aantal fietsen per dag, maar visualiseert ook de spreiding van de data met behulp van 'Error Bars' (de rode lijnen):

De blauwe staaf: Het gemiddeld aantal vrije fietsen.

De rode lijn: Het bereik tussen het minimum en maximum aantal gemeten fietsen op die dag.

Meerwaarde: Dit maakt in één oogopslag duidelijk of een dag stabiel is (korte rode lijn) of dat er grote schommelingen zijn (lange rode lijn), wat waardevolle context biedt die een simpel gemiddelde verbergt.

### 7.4 PDF-rapport met beide grafieken

Naast het Markdown-rapport wordt er automatisch ook een PDF-bestand gegenereerd: [reports/report.pdf](reports/report.pdf)

Dit PDF-rapport bevat:

- een overzicht van de workflow
- de statistieken van de dataset
- de twee grafieken:
  - Temperatuur vs. aantal vrije fietsen
  - Aantal vrije fietsen per uur
  - Weekdag-analyse met min/max bereik
- begeleidende uitleg bij elke visualisatie
- automatische titelpagina, consistente layout en uniforme opmaak

Het PDF-bestand wordt automatisch vernieuwd bij elk run van de workflow.
