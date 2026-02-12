# Entwicklungsfortschritt

## Erledigt (Milestones)

### PR1 – Projektstart
- Python-/Modul-Grundgerüst (`hexcrawl/*`) angelegt, Einstiegspunkt über `main.py`.
- Startbares pygame-ce-Fenster mit sauberem Quit (ESC/Fenster schließen).

### PR2 – WorldMapView
- Hexgrid in der World-Ansicht implementiert.
- Interaktion in World: RMB-Pan, Wheel-Zoom, LMB Hover/Select, Debug-Panel.

### PR3 – World/Local Umschaltung
- Umschalten zwischen World- und Local-View via TAB.
- Local-Grid + WASD-Cursor in der Local-Ansicht.

### PR4 – TimeModel
- TimeModel eingeführt: Local-Realtime + World-Ticks.
- Manueller World-Step über Taste `T`.

## Aktueller Stand

- Spiel läuft mit zwei Modi: **World** und **Local** (TAB zum Wechseln).
- **World** unterstützt Exploration per Kamera (Pan/Zoom) und Tile-Auswahl.
- **Local** unterstützt Grid-Navigation über WASD.
- Zeitmodell ist aktiv: Local läuft in Realtime, World wird über Ticks fortgeschrieben (aktuell per `T`).

## Nächste 3 PRs

1. **Player-State + World Click-to-Move + Travel-Time**
   - Player-Hex-Position sichtbar machen.
   - Movement über Enter/G bestätigen.
   - World-Ticks abhängig von der Hex-Distanz erhöhen.

2. **Worldgen Stub: Height/Ocean/Coast + einfache Farbcodierung pro Tile**
   - Deterministische Weltgenerierung per Seed.
   - Erste visuelle Klassifikation (Height/Ocean/Coast), noch ohne Rivers/Wetter.

3. **Climate/Biomes Stub: heat/moisture → biome mapping + Debug-Anzeige**
   - Datenstruktur für Klima/Biome anlegen.
   - Erste Visualisierung + Debug-Overlay für Heat/Moisture/Biome.
