# Erosion Sub-Roadmap

## Ziel

Minimaler Erosionsschritt zur visuellen/spielerischen Verbesserung der Höhenkarte, ohne teure wissenschaftliche Prozesssimulation.

## Ansatz (lightweight)

### 1) Thermal Erosion (leicht)
- Steile Gradientenspitzen begrenzen.
- Material lokal von steilen Hexen zu tieferen Nachbarn verteilen.
- Wenige Iterationen für stabile Laufzeit.

### 2) Hydraulic-inspired Smoothing (leicht)
- Entlang bestehender Flusskorridore Täler leicht vertiefen/breiten.
- Ufernahe Kanten glätten, um harte Artefakte zu reduzieren.
- Keine vollständige Fluidsimulation.

## Constraints

- Rechenbudget geeignet für große Karten (Target 4000×2000).
- Deterministisch bei gleichem Seed und gleicher Ausgangshöhe.
- Modulare Schritte: kann bei Bedarf teilweise deaktiviert werden.

## „Realistisch genug“

- Gebirge wirken weniger pixelig/rauschig.
- Flusstäler/Küstenformen sind besser lesbar.
- Terrain bleibt gameplay-klar (kein übermäßiges Verwaschen).
