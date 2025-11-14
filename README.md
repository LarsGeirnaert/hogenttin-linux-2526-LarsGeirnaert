Data Workflow: Temperatuur vs. Aantal Vrije Fietsen in Gent
1. Beschrijving van de workflow

Deze workflow verzamelt automatisch gegevens over het weer (temperatuur) en het aantal beschikbare deelfietsen in Gent. De data wordt verwerkt, geanalyseerd en gevisualiseerd, waarna de resultaten automatisch naar GitHub worden gepusht.

Fasen van de workflow:

Data ophalen: JSON-bestanden van de Gentse weer-API en CityBikes API.

Data transformeren: JSON → CSV (combined.csv) met relevante kolommen.

Data analyseren: grafiek van vrije fietsen vs. temperatuur.

Rapport genereren: Markdown-rapport (report.md) met grafieken en statistieken.

Automatisering: alles kan automatisch draaien via een cron-job en wordt gepusht naar GitHub.

2. Data

Bronnen:

Weer: publieke weer-API voor Gent

Fietsen: CityBikes API (Donkey Republic / Gent netwerk)

Periode: vanaf 13 november 2025, interval: elk 15 minuten (automatisch)

Bestandsindeling:

Ruwe data: JSON-bestanden in raw_data/

Verwerkte data: CSV in transformed_data/combined.csv

3. Directorystructuur
```data-workflow/
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
4. Gebruiksaanwijzing
4.1 Automatisch uitvoeren (elk kwartier)

De workflow kan automatisch elk kwartier draaien via een cron-job. Hierbij wordt nieuwe data opgehaald, en worden alle documenten, grafieken en het CSV-bestand bijgewerkt. Voeg bijvoorbeeld deze regel toe aan je crontab:

``` */15 * * * * cd /home/larsg/projects/data-workflow && ./scripts/run_workflow.sh ```

4.2 Handmatig testen

Wanneer je de workflow handmatig start met:
```
cd ~/projects/data-workflow 
bash /home/larsg/projects/data-workflow/scripts/run_workflow.sh --no-fetch
```


wordt geen nieuwe data opgehaald. Alleen de verwerkte bestanden, grafieken en rapporten worden bijgewerkt op basis van de reeds aanwezige ruwe data. Dit is handig om snel te testen of de analyse en visualisaties correct werken.

5. Resultaten bekijken

Ruwe data: raw_data/

Verwerkte CSV: transformed_data/combined.csv

Grafiek: reports/fiets_vs_temp.png

Markdown-rapport: reports/report.md

Opmerking: de workflow pusht automatisch nieuwe gegevens en rapporten naar GitHub, zodat alles online up-to-date blijft.

6. Extra visualisaties en PDF-rapport

Naast de basisgrafiek (vrije fietsen vs. temperatuur) bevat de workflow een tweede grafiek die een ander aspect van de dataset verduidelijkt.

6.1 Extra grafiek: aantal vrije fietsen per uur

Een bijkomende visualisatie werd toegevoegd:
fietsen vs. uur van de dag → reports/fiets_vs_uur.png

Deze grafiek toont hoe het totaal aantal vrije fietsen in Gent varieert per uur van de dag.
Ze geeft inzichten zoals:

op welke momenten er typisch meer of minder fietsen beschikbaar zijn

piekmomenten rond ochtend- en avondspits

eventuele trends in gebruiksdrukte tijdens weekends of koude dagen

hoe de beschikbaarheid doorheen de dag evolueert

Deze grafiek is aanvullend op de temperatuur-analyse en helpt om te bepalen of variaties te wijten zijn aan dagelijks ritme in plaats van aan weersomstandigheden.

6.2 PDF-rapport met beide grafieken

Naast het Markdown-rapport wordt er automatisch ook een PDF-bestand gegenereerd:

📄 reports/report.pdf

Dit PDF-rapport bevat:

een overzicht van de workflow

de statistieken van de dataset

de twee grafieken:

Temperatuur vs. aantal vrije fietsen

Aantal vrije fietsen per uur

begeleidende uitleg bij elke visualisatie

automatische titelpagina, consistente layout en uniforme opmaak

Het PDF-bestand wordt automatisch vernieuwd bij elk run van de workflow (behalve wanneer --no-fetch wordt gebruikt).
