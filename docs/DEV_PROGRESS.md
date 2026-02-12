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

## Aktueller Stand

- Spiel läuft mit zwei Modi: **World** und **Local** (`TAB` zum Wechseln).
- **World** unterstützt Pan, Zoom, Hover/Select und Travel (`ENTER`/`G`).
- **Local** unterstützt Grid-Navigation über `WASD`.
- Zeitmodell ist aktiv: Local läuft in Realtime, World wird per Ticks fortgeschrieben (`T` + Travel-Distanz).
- Worldgen liefert deterministische Terrain/Height-Werte inklusive Debug-Anzeige.

## Nächste 3 PRs

1. **Climate/Biomes Stub: heat/moisture → biome mapping + Debug-Anzeige**
   - Datenstruktur für Klima/Biome anlegen.
   - Erste Visualisierung + Debug-Overlay für Heat/Moisture/Biome.

2. **Zoom/Input-Härtung + Test-Discovery Stabilisierung**
   - Zoom-Eingaben für unterschiedliche pygame-Eventpfade absichern.
   - `unittest`-Discovery auf Konsolen-Defaults robust halten.

3. **Travel UX: Validation + kleines Feedback im Debug-Panel**
   - Travel-Trigger und Auswahlzustände klarer sichtbar machen.
   - Fehlende/ungültige Travel-Aktionen besser rückmelden.
