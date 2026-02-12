# Architektur

## Module

- `core`
  - Basale Laufzeit-/Anwendungssteuerung (App-Loop, Input-Weitergabe, zentraler Zustand auf App-Ebene).
  - Gemeinsame Utilities für deterministisches Verhalten (z. B. Seeds/RNG, sofern genutzt).

- `ui`
  - Darstellung und Interaktion für World- und Local-Ansicht.
  - Enthält Views/Renderer und Controls (Pan/Zoom/Select, Cursor-Bewegung, Mode-Switch).

- `world`
  - Weltbezogene Datenstrukturen und (schrittweise) Worldgen-Pipeline.
  - Zielbild: Height → Klima → Hydro → Biomes als getrennte, testbare Schritte.

- `sim`
  - Laufende Simulationen (aktuell TimeModel, später NPC/Faktionen/Ökologie).
  - Verantwortlich für Fortschreibung über diskrete World-Ticks.

## Zeitmodell (aktueller Stand + nächste Evolutionsstufe)

### Aktueller Stand
- **Local-Ebene:** Realtime-orientierte Fortschreibung im laufenden Spielbetrieb.
- **World-Ebene:** diskrete Tick-Fortschreibung.
- **Brücke aktuell:** manueller World-Step über Taste `T`, um World-Zeit explizit weiterzuschalten.

### Nächste Evolutionsstufe
- Einführung einer zentralen **GameClock** als verbindliche Zeitquelle.
- Erweiterung um Kalender-/Datumslogik (z. B. Tag/Monat/Jahr als Simulationszeit).
- Koppelung von Travel-Cost an Weltbewegung: Distanz/Route erzeugt definierte Zeitkosten in World-Ticks.
- Klar definierte Synchronisationsregeln zwischen Local-Realtime und World-Ticks (z. B. Events, Übergänge, Reisebestätigung).
