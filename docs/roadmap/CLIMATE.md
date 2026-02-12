# Climate Sub-Roadmap

## Ziel

Ein plausibles, deterministisches Klimamodell, das aus wenigen robusten Inputs stabile Heat/Moisture/Biome-Felder erzeugt.

## Inputs

- **Latitude**: Grundtemperatur nach Breite.
- **Height**: Altitude-Cooling (höher = kälter).
- **Wind**: vorherrschende Windbänder als Feuchtetransport.
- **Ocean Proximity**: Distanz/Exposition zu maritimer Feuchtequelle.
- **Rainshadow**: Leeeffekte hinter Gebirgszügen.

## Outputs

- **Heat Field** (normiert, z. B. 0..1)
- **Moisture Field** (normiert, z. B. 0..1)
- **Biome Mapping** aus Heat × Moisture, modifiziert durch Höhe

## Pipeline (v3)

1. Latitude-Heat-Basis berechnen.
2. Heat durch Höhe korrigieren (Lapse-Rate-Approximation).
3. Feuchtequellen über Ozeannähe + Windadvektion einspeisen.
4. Rainshadow entlang Windrichtung hinter Höhenbarrieren anwenden.
5. Heat/Moisture in Biome-Klassen mappen.

## Debug & Visualisierung

- Einzel-Overlays für Heat, Moisture, Windrichtung, Rainshadow-Faktor.
- Kombi-Overlay für Biome.
- Seed/Layer-Parameter im Debugpanel anzeigen, um Reproduzierbarkeit zu prüfen.

## „Realistisch genug“

- Breitenabhängige Temperaturzonen klar erkennbar.
- Luv/Lee-Unterschiede an großen Gebirgsgürteln sichtbar.
- Küstennähe tendenziell feuchter als tiefes Binnenland.
- Keine wissenschaftliche Klimasimulation, sondern gameplay-taugliche Plausibilität.
