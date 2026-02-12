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

## Controls

- `ESC`: Spiel beenden
- `TAB`: Wechsel zwischen World- und Local-Ansicht
- `WASD` (Local): Cursor im Local-Grid bewegen
- `RMB` (World): Kamera pannen
- `Wheel` (World): Zoom
- `LMB` (World): Hex auswählen
- `ENTER` / `G` (World): Zur ausgewählten Hex reisen
- `T` (World): World-Step (Tick) auslösen
