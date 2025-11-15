# Data Workflow: Temperatuur vs. Aantal Vrije Fietsen in Gent

## 0. Relevante links
- GitHub repository: https://github.com/hogenttin/linux-2526-LARS
- Panopto demo opname: [link hier]

---

## 1. Beschrijving van de workflow

Deze workflow verzamelt automatisch gegevens over het weer (temperatuur) en het aantal beschikbare deelfietsen in Gent. De data wordt verwerkt, geanalyseerd en gevisualiseerd, waarna de resultaten automatisch naar GitHub worden gepusht.

### Fasen van de workflow

1. **Data ophalen**  
   JSON-bestanden van de Gentse weer-API en CityBikes API worden opgehaald op regelmatige tijdstippen.

2. **Data transformeren**  
   Omzetten van JSON naar CSV (`combined.csv`) met relevante kolommen en timestamps.

3. **Data analyseren**  
   Berekenen van statistieken, correlaties en genereren van grafieken (temperatuur vs vrije fietsen, fietsen per uur).

4. **Rapport genereren**  
   Aanmaken van Markdown-rapport (`report.md`) en professioneel PDF-rapport (`report.pdf`) met grafieken en tabellen.

5. **Automatisering**  
   Alles kan automatisch draaien via een cron-job of GitHub Actions en wordt naar GitHub gepusht.

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

```text
data-workflow/
├─ scripts/              # Scripts voor alle fases
│  ├─ fetch_data.sh      # Haalt JSON-data op
│  ├─ transform_data.sh  # Zet raw JSON om naar CSV
│  ├─ analyze_data.py    # Maakt grafiek en berekent statistieken
│  ├─ generate_report.py # Genereert Markdown-rapport
│  └─ run_workflow.sh    # Overkoepelend script dat alles uitvoert en pusht
├─ raw_data/             # Ruwe JSON-bestanden (niet handmatig bewerken)
├─ transformed_data/     # CSV-bestanden (combined.csv)
├─ reports/              # Grafieken en Markdown-rapport
├─ logs/                 # Logbestanden van fetches
└─ README.md
```

## 4. Dependencies

- Python 3.11

- pandas

- matplotlib

- scikit-learn

- reportlab

- jq (voor JSON parsing in bash)

- curl (voor data ophalen via API)

## 5. Gebruiksaanwijzing
### 5.1 Automatisch uitvoeren (elk kwartier)

De workflow kan automatisch elk kwartier draaien via een cron-job. Hierbij wordt nieuwe data opgehaald, en worden alle documenten, grafieken en het CSV-bestand bijgewerkt. Voeg bijvoorbeeld deze regel toe aan je crontab:

``` */15 * * * * cd /home/larsg/projects/data-workflow && ./scripts/run_workflow.sh ```

### 5.2 Handmatig testen

Om de workflow handmatig uit te voeren zonder nieuwe data op te halen:

```
cd ~/projects/data-workflow
bash scripts/run_workflow.sh --no-fetch
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

- **Grafiek 2 (Fietsgebruik vs uur)**: [reports/fiets_vs_temp.png](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/fiets_vs_uur.png)

- **Markdown-rapport**: [reports/report.md](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/report.md)

- **PDF-rapport**: [reports/report.pdf](https://github.com/LarsGeirnaert/hogenttin-linux-2526-LarsGeirnaert/blob/main/reports/report.pdf)

Opmerking: de workflow pusht automatisch nieuwe gegevens en rapporten naar GitHub, zodat alles online up-to-date blijft.

## 7. Extra visualisaties en PDF-rapport

Naast de basisgrafiek (vrije fietsen vs. temperatuur) bevat de workflow een tweede grafiek die een ander aspect van de dataset verduidelijkt.

### 7.1 Extra grafiek: aantal vrije fietsen per uur

Een bijkomende visualisatie werd toegevoegd:
fietsen vs. uur van de dag → reports/fiets_vs_uur.png

Deze grafiek toont hoe het totaal aantal vrije fietsen in Gent varieert per uur van de dag.
Ze geeft inzichten zoals:

- op welke momenten er typisch meer of minder fietsen beschikbaar zijn

- piekmomenten rond ochtend- en avondspits

- eventuele trends in gebruiksdrukte tijdens weekends of koude dagen

- hoe de beschikbaarheid doorheen de dag evolueert

Deze grafiek is aanvullend op de temperatuur-analyse en helpt om te bepalen of variaties te wijten zijn aan dagelijks ritme in plaats van aan weersomstandigheden.

### 7.2 PDF-rapport met beide grafieken

Naast het Markdown-rapport wordt er automatisch ook een PDF-bestand gegenereerd:

📄 reports/report.pdf

Dit PDF-rapport bevat:

- een overzicht van de workflow
- de statistieken van de dataset
- de twee grafieken:
    - Temperatuur vs. aantal vrije fietsen
    - Aantal vrije fietsen per uur
- begeleidende uitleg bij elke visualisatie
- automatische titelpagina, consistente layout en uniforme opmaak


Het PDF-bestand wordt automatisch vernieuwd bij elk run van de workflow (behalve wanneer --no-fetch wordt gebruikt).
