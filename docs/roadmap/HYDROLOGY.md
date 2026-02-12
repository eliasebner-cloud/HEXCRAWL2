# Hydrology Sub-Roadmap

## Ziel

Ein robustes Fluss-/Seen-System auf Hexfeldern, das aus der Höhenkarte natürliche Abflussmuster erzeugt und deterministisch reproduzierbar bleibt.

## Kernmodell

- **Flow Direction**: pro Hex Abflussrichtung zum niedrigsten gültigen Nachbarn.
- **Sink Filling / Depression Handling**: lokale Senken behandeln, damit Wasserpfade stabil sind.
- **Flow Accumulation**: aufsummierter Zufluss je Hex als Grundlage für Flussgröße.
- **Rivers to Sea**: priorisiert Abfluss zu Ozeanrändern.
- **Lakes**: Binnenbecken mit definiertem Überlaufverhalten.

## Pipeline

1. Height-Input normalisieren und hydrologisch „clean“ machen.
2. Flow-Direction-Feld berechnen (Hex-Nachbarn beachten).
3. Akkumulation topologisch aufbauen.
4. River-Mask aus Akkumulationsschwellen ableiten.
5. Seen/Endorheik modellieren und ggf. Spill-Points setzen.

## Deterministik

- Gleiches Height-Input + Seed ergibt identische Flussnetze.
- Tie-Breaker bei gleich hohen Nachbarn seed-stabil definieren.

## „Realistisch genug“

- Flüsse konvergieren zu Hauptläufen statt zufälligem Zickzack.
- Große Flüsse entstehen aus großen Einzugsgebieten.
- Seen treten in Senken plausibel auf.
- Mehrheit der Flüsse endet im Meer oder in stabilen Binnenbecken.
