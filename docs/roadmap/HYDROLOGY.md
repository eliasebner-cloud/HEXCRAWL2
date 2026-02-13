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

## Aktueller Stand (WG-5)

- **Flow-Graph aktiv:** `flow_to` pro Hex ist deterministisch berechnet (inkl. Wrap-X-sicherer Nachbarschaft).
- **Accumulation aktiv:** auf dem Flow-Graph aufbauend werden Einzugsgebiete/Akkumulationen berechnet und für River-Masks genutzt.
- **Rivers/Lakes aktiv:** Flussnetz und Seen sind im HydrologyModel integriert.
- **River-Overlay in World:** Toggle über `R`; Threshold-Tuning über `[` und `]` (DEV-default-fokussiert).

## Bekannte Grenzen / Notes

- **TARGET Global Build:** derzeit noch nicht vollständig chunk-basiert; Build-Guard verhindert ungewollte Vollberechnung im TARGET-Profil.
- **Thresholds:** River-Sichtbarkeit hängt aktuell primär am DEV-Threshold; für TARGET ist weitere Kalibrierung im Zuge von WG-6/WG-6+ geplant.
- **Wrap-Rendering:** Overlay-Rendering ist wrap-aware (inkl. Multi-Wrap), damit keine Naht-Artefakte am X-Seam entstehen.
