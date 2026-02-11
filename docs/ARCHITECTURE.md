# Architektur (Startgerüst)

## Module

- `core`
  - Clock / Timing-Basis
  - RNG / deterministische Seeds
  - Event-Bus
  - Globaler State-Container

- `ui`
  - World-View (Overworld)
  - Local-View (nahes Umfeld)

- `world`
  - Generation: Height
  - Generation: Climate
  - Generation: Hydro
  - Generation: Biomes

- `sim`
  - NPC-Simulation
  - Fraktionen
  - Ökologie / Ressourcenkreisläufe

## Zeitmodell (TODO)

- World-Ebene: diskrete Schritte (Tick-basiert).
- Local-Ebene: Realtime-Loop (frame-/delta-time-basiert).
- TODO: Synchronisierung zwischen World-Ticks und Local-Realtime definieren.
