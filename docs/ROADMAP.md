# Roadmap

Kurzüberblick über die geplante Reihenfolge. Fokus: zuerst Navigierbarkeit und Zeitkonsistenz, danach Weltinhalte und schließlich lebendige Simulation.

## 1) Navigation
- World-/Local-Flow robust machen (Selektion, bestätigte Bewegung, Rücksprünge).
- Ziel: Spieler kann sich konsistent orientieren und bewegen, bevor Inhalte vertieft werden.

## 2) Time
- TimeModel zu einer zentralen GameClock ausbauen (Kalender + Travel-Cost).
- Ziel: Jede Bewegung/Simulation hat nachvollziehbare Zeitkosten.

## 3) Worldgen
- Deterministische Basiskarten (Height/Ocean/Coast) mit Seed.
- Ziel: reproduzierbare, strukturierte Welt als Fundament für alle weiteren Systeme.

## 4) Weather
- Klimadaten (heat/moisture) und einfache Wetterdynamik aufsetzen.
- Ziel: Umweltlogik, die später Biome, Ertrag und Reise beeinflusst.

## 5) Infrastruktur
- Siedlungen, Wege, einfache Netzwerke/Verbindungen.
- Ziel: Welt erhält funktionale Knotenpunkte für Handel, Reise und Konflikte.

## 6) Fraktionen / NPC LOD
- Fraktionsziele + NPC-Simulation in abgestuften Detailstufen (LOD).
- Ziel: große Welt performant simulieren, lokal aber detailreich darstellen.

## 7) Living World
- Ereignisse, Reaktionen und längerfristige Weltzustandsänderungen.
- Ziel: Welt entwickelt sich auch ohne direkten Spielerinput glaubwürdig weiter.

## 8) Gameplay
- Quests, Progression, Risiko/Belohnung und Kernspielschleifen ausbauen.
- Ziel: aus den Systemen entsteht ein spielbarer Hexcrawl mit klaren Entscheidungen.
