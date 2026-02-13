# HEXCRAWL

Minimal startbares Projektgerüst für ein 2D Hexcrawl RPG.

## Setup

```bash
python -m venv .venv
```

Virtuelle Umgebung aktivieren:

- macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```
- Windows (PowerShell):
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

> Hinweis: Es wird **pygame-ce** verwendet. Ein separates `pygame` ist nicht nötig.

## Development

```bash
python tools/check.py
```

## Controls

- `ESC`: Spiel beenden
- `TAB`: Wechsel zwischen World- und Local-Ansicht
- `F11`: Fullscreen/Windowed umschalten
- `F2`: Debug-Verbosity umschalten (`MIN` → `STD` → `ADV`)
- `WASD` (Local): Cursor im Local-Grid bewegen
- `RMB` (World): Kamera pannen
- `Wheel` (World): Zoom
- `LMB` (World): Hex auswählen
- `ENTER` / `G` (World): Zur ausgewählten Hex reisen
- `T` (World): World-Step (Tick) auslösen
- `R` (World): River-Overlay umschalten

## Contributing / PR workflow

- Bitte für jede PR das GitHub-PR-Template verwenden (`.github/pull_request_template.md`).
- PRs sollen den Repro-Info-Standard (Profile/Seeds/Steps/Test Commands) ausfüllen.
- Vor dem Erstellen einer PR mindestens die Standard-Tests ausführen, z. B.:

```bash
python tools/check.py
python -m unittest -v
```

