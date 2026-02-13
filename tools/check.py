"""Run repo quality checks (compile + unittest) with one command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> int:
    print(f"[check] running: {' '.join(cmd)}")
    completed = subprocess.run(cmd, cwd=cwd)
    if completed.returncode != 0:
        print(f"[check] failed ({completed.returncode}): {' '.join(cmd)}")
    return completed.returncode


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    python_files = sorted(str(path.relative_to(repo_root)) for path in repo_root.rglob("*.py"))

    if not python_files:
        print("[check] no python files found")
        return 1

    rc = _run([sys.executable, "-m", "py_compile", *python_files], repo_root)
    if rc != 0:
        return rc

    rc = _run([sys.executable, "-m", "unittest", "-v"], repo_root)
    if rc != 0:
        return rc

    print("[check] all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
