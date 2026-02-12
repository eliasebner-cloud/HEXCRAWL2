# Roadmap (Vision v2)

Diese Roadmap priorisiert **Worldgen-First**: Die nächsten PRs fokussieren auf eine glaubwürdige, deterministische, finite Hex-Welt als Fundament für alle späteren Systeme.

## Priorität: Worldgen-First

Die Reihenfolge ist verbindlich:
1. **Worldgen Core**
   - Kontinente
   - Tektonik
   - Klima
   - Hydrologie
   - Erosion/Polish
2. **Ressourcen / Infrastruktur / POIs**
3. **Simulation (Fraktionen, NPC LOD, Living World)**
4. **Gameplay (Skyrim/EQ2-ähnliche Exploration + Crafting/Farming-Loops)**

> Hinweis für kommende PRs: Worldgen-first; POIs/Infrastruktur erst nach Kontinente+Tektonik+Klima+Flüsse.

## Große Roadmap (Phasen)

### Phase A — Worldgen Core
Ziel: reproduzierbare, spielbare Weltbasis mit realistisch wirkenden Makrostrukturen.

Reihenfolge innerhalb der Phase:
1. **Kontinente/Ozeanbecken** (korrelierte Höhenfelder, keine Noise-Flecken)
2. **Tektonik** (Platten + Gebirgsgürtel/Rifts/Trenches)
3. **Klima** (Latitude/Wind/Rainshadow/Altitude)
4. **Hydrologie** (Flüsse, Seen, Abfluss bis Meer)
5. **Erosion/Polish** (leichtgewichtig, gameplay-tauglich)

### Phase B — Ressourcen, Infrastruktur, POIs
Ziel: Welt mit nutzbaren Inhalten füllen, nachdem die physische Basis steht.

### Phase C — Simulation
Ziel: Fraktionen/NPCs/Living-World auf robustem Terrain-/Klima-/Hydro-Fundament.

### Phase D — Gameplay
Ziel: Kernspielschleifen (Exploration im Stil Skyrim/EQ2, Crafting, Farming, Risiko/Belohnung) auf stabiler Weltsimulation.

## Single Source of Truth

`docs/ROADMAP.md` ist die **Top-Level-Steuerung**. Detailplanung und DoD pro Worldgen-Baustein liegen in:

- `docs/roadmap/WORLDGEN.md`
- `docs/roadmap/TECTONICS.md`
- `docs/roadmap/CLIMATE.md`
- `docs/roadmap/HYDROLOGY.md`
- `docs/roadmap/EROSION.md`

Alle kommenden Worldgen-PRs referenzieren diese Sub-Roadmaps explizit.
