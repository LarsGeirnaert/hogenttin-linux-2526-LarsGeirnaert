# Data Workflow: Temperatuur vs. Aantal Vrije Fietsen in Gent

## 1. Beschrijving van de workflow
Deze workflow verzamelt automatisch gegevens over het weer (temperatuur) en het aantal beschikbare deelfietsen in Gent, verwerkt deze data, genereert grafieken en een rapport, en pusht alles naar GitHub.

**Fasen van de workflow:**
1. **Data ophalen**: JSON-bestanden van Gentse weer-API en CityBikes API.  
2. **Data transformeren**: JSON → CSV (`combined.csv`) met relevante kolommen.  
3. **Data analyseren**: grafiek van vrije fietsen vs. temperatuur + basisstatistieken.  
4. **Rapport genereren**: Markdown-rapport (`report.md`) met grafieken en statistieken.  
5. **Automatisering**: alles draait automatisch via een cron-job en wordt (optioneel) gepusht naar GitHub.

---

## 2. Data
- **Bronnen:**
  - **Weer**: publieke weer-API voor Gent (bijv. Open-Meteo).  
  - **Fietsen**: CityBikes API (Donkey Republic / Gent netwerk).  
- **Periode**: vanaf **13 november 2025** (startdatum), interval: **elk 1 uur**.  
- **Bestandsindeling:**
  - Ruwe data: JSON-bestanden in `raw_data/`  
  - Verwerkte data: CSV in `transformed_data/combined.csv`  

---

## 3. Directorystructuur
Dit is de aanbevolen structuur van het project:

