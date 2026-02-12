# Worldgen Sub-Roadmap

## Design-Ziele

- **Finite Hex-Welt** mit klaren Weltgrenzen in Y-Richtung und Wrap in X-Richtung.
- **Deterministisch per Seed**: identische Inputs erzeugen identische Welt.
- **Realistisch wirkende Großformen**: Kontinente, Ozeanbecken, Gebirgsgürtel, Flusssysteme.
- **Skalenmodell Macro → Micro** für schnelle Iteration und spätere Zielauflösung.
- **Performance-orientiert** über Chunking, ohne die Deterministik zu brechen.

## Fixe Parameter

- **Target World Size:** `4000 x 2000` (2:1)
- **Wrap:** X (Longitude) = ja, Y = nein
- **Seed:** globaler World-Seed, plus abgeleitete Layer-Seeds
- **Skalenmodell:**
  - **Target-Grid:** `4000 x 2000` (Shipping/Final)
  - **Dev-Grid:** `512 x 256` (schnelle Iteration)
  - **Macro-Grid:** `500 x 250` (grobe Strukturen, dann Sampling/Resampling)
- **Chunking:** `64 x 64` Hex pro Chunk; Chunk-ID z. B. `chunk_x = x // 64`, `chunk_y = y // 64`

## Pipeline-Logik (Macro → Micro)

1. Macro-Felder erzeugen (Kontinente/Basins/Tektonik-Rohform).
2. Auf Ziel- oder Dev-Auflösung samplen.
3. Layer deterministisch kombinieren (Height/Climate/Hydrology/Erosion).
4. Chunkweise cachen/streamen für Rendering und Simulation.

## PR-Reihenfolge (WG-0 bis WG-6)

### WG-0 — WorldConfig & Scales
**Inhalt:** zentrale WorldConfig für target/dev/macro/chunk, Wrap-X, Seed-Derivation.

**Definition of Done:**
- Konfiguration ist zentral, dokumentiert und testbar.
- Dev/Target-Modus umschaltbar ohne Logikduplikate.
- Chunk-Koordinaten und Wrap-X-Regeln klar definiert.

### WG-1 — Continents / Ocean Basins
**Inhalt:** korrelierte Höhenfelder für zusammenhängende Kontinente/Ozeanbecken.

**Definition of Done:**
- Keine „Fleckenwelt“ aus isolierten Noise-Inseln.
- Mehrere große Landmassen + Ozeanbecken erkennbar.
- Deterministisch reproduzierbar per Seed.

### WG-2 — Plates & Mountain Belts
**Inhalt:** Voronoi-Platten, Grenzklassifikation, Initialprägung von Gebirgs-/Rift-/Trench-Zonen.

**Definition of Done:**
- Jede Hex einer Platte zugeordnet.
- Grenztypen (konvergent/divergent/transform) ableitbar.
- Height-Modifier für Gebirge/Rifts/Trenches vorhanden.

### WG-3 — Height Polish
**Inhalt:** geglättete Übergänge, Ridge-Betonung, Artefaktreduktion.

**Definition of Done:**
- Höhenkarte wirkt zusammenhängend und navigierbar.
- Harte Kanten/Artefakte reduziert.
- Gebirgsgürtel bleiben visuell klar.

### WG-4 — Climate v3
**Inhalt:** Latitude + Wind + Rainshadow + Altitude-Cooling.

**Definition of Done:**
- Heat/Moisture-Felder konsistent und deterministisch.
- Leeseiten/Trockengebiete plausibel.
- Biome aus Heat/Moisture + Höhe ableitbar.

### WG-5 — Rivers / Lakes
**Inhalt:** Basin-Logik, Flussrichtung, Flow Accumulation, Seen und Meerabfluss.

**Definition of Done:**
- Flüsse folgen Gefälle und konvergieren plausibel.
- Endorheische Becken/Seen möglich.
- Mehrheit der Flüsse erreicht Meer oder stabile Binnenbecken.

### WG-6 — Erosion / Polish
**Inhalt:** leichte thermische/hydraulische Erosion für Spielbarkeit.

**Definition of Done:**
- Terrain wirkt weniger „synthetisch“.
- Küsten/Flusstäler/Gebirge lesbarer.
- Rechenkosten für Zielgröße praktikabel.

## Nicht-Ziele (vorerst)

- POIs
- Cities
- Factions
- Economy

Diese Themen starten erst nach Abschluss von Worldgen-Core.
