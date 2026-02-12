# Tectonics Sub-Roadmap

## Ziel

Ein deterministisches, hex-geeignetes Plattenmodell, das großräumige Reliefstrukturen erzeugt: Gebirgsgürtel, Rifts und Tiefseegräben.

## Modell

### 1) Voronoi-Platten
- Erzeuge `N` Platten-Seeds deterministisch aus World-Seed.
- Weise jede Hex der nächstgelegenen Seed-Zelle zu (Voronoi-Partition).
- Optional: Lloyd-Relaxation für gleichmäßigere Plattengrößen.

### 2) Plattentypen
- **Oceanic Plate**: dichter, dünner, tendenziell niedrigere Ausgangshöhe.
- **Continental Plate**: leichter, dicker, höhere Ausgangshöhe.
- Typzuweisung deterministisch aus Seed + Lageheuristik.

### 3) Bewegungsvektoren
- Jede Platte erhält einen 2D-Bewegungsvektor (Richtung + Magnitude).
- Vektoren werden seed-basiert erzeugt und bleiben über den Weltlauf stabil (für statische Worldgen).

## Grenztypen und Ableitungen

An jeder Plattengrenze wird die relative Bewegung bewertet:

- **Convergent** (aufeinander zu):
  - continental + continental → Gebirgsgürtel/Ridges
  - oceanic + continental → Subduktionsrand, Küstengebirge + Trench offshore
  - oceanic + oceanic → Inselbögen + Trench
- **Divergent** (auseinander):
  - Rift-Zonen, Rücken, abgesenkte Becken
- **Transform** (seitliches Vorbeigleiten):
  - lineare Störungszonen, moderate Relief-Offsets

## Hex-geeignete Umsetzung

- Nachbarschaft über Hex-Adjazenz statt square-grid-Annahmen.
- Grenzband als Hex-Korridor mit Distanzabfall (z. B. 0..k Hex zur Grenze).
- Height-Modifier über gewichtete Funktion:
  - konvergent: positiver Ridge-Bias
  - divergent: negativer Rift-Bias
  - transform: lokaler Rauheits-/Offset-Bias

## Deterministik

- Alle Schritte leiten Zufallswerte aus `world_seed` + konstanten Layer-Keys ab.
- Kein frame- oder thread-abhängiger Zufall.
- Bei gleichem Seed sind Plate-IDs, Grenzen und Height-Modifier identisch.
