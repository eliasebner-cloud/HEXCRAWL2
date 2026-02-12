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

### PR6 – Player + Travel
- Player-State in der World-Ansicht sichtbar gemacht.
- Travel über `ENTER`/`G` zur ausgewählten Hex aktiviert.
- World-Ticks steigen beim Travel entsprechend der Distanz.

### PR7 – Worldgen Terrain-Fill
- Deterministische Terrain-Generierung per Seed ergänzt.
- Terrain/Height-Debugwerte in der World-Ansicht verfügbar.

### PR8 – Climate/Biomes
- Climate- und Biome-Layer ergänzt.
- Heat/Moisture/Biome-Informationen in Debug/Visualisierung nutzbar.

### PR9 – Fullscreen/F11 + Input-Härtung
- Fullscreen-Toggle über `F11` ergänzt.
- Input-/Eventpfade weiter stabilisiert.

## Aktueller Stand

- Spiel läuft mit zwei Modi: **World** und **Local** (`TAB` zum Wechseln).
- **World** unterstützt Pan, Zoom, Hover/Select und Travel (`ENTER`/`G`).
- **Local** unterstützt Grid-Navigation über `WASD`.
- Zeitmodell ist aktiv: Local läuft in Realtime, World wird per Ticks fortgeschrieben (`T` + Travel-Distanz).
- Worldgen liefert deterministische Terrain/Height/Klima/Biome-Werte inklusive Debug-Anzeige.
- Fullscreen ist über `F11` verfügbar.

## Nächste 3 PRs (Worldgen-First)

1. **WorldConfig & finite map scaffolding**
   - `target/dev/macro/chunk` als zentrale Konfiguration einführen.
   - Finite Welt mit Wrap-X und ohne Wrap-Y verbindlich machen.

2. **Continents / Ocean basins (correlated height)**
   - Zusammenhängende Landmassen und Ozeanbecken erzeugen.
   - Fleckige Noise-Verteilung durch korrelierte Makrostrukturen ersetzen.

3. **Tectonics plates + mountain belts**
   - Voronoi-Plattenmodell integrieren.
   - Grenztypen ableiten und Gebirgsgürtel/Rifts/Trenches prägen.
