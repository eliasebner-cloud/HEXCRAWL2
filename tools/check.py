"""Run repo quality checks (compile + unittest) with one command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "build",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "node_modules",
}


def _run(cmd: list[str], cwd: Path) -> int:
    print(f"[check] running: {' '.join(cmd)}")
    completed = subprocess.run(cmd, cwd=cwd)
    if completed.returncode != 0:
        print(f"[check] failed ({completed.returncode}): {' '.join(cmd)}")
    return completed.returncode


def _tracked_python_files(repo_root: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--", "*.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    return sorted(line.strip() for line in completed.stdout.splitlines() if line.strip())


def _fallback_python_files(repo_root: Path) -> list[str]:
    python_files: list[str] = []
    for path in repo_root.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.relative_to(repo_root).parts):
            continue
        python_files.append(str(path.relative_to(repo_root)))
    return sorted(python_files)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    python_files = _tracked_python_files(repo_root)
    if not python_files:
        print("[check] git unavailable or repo metadata missing, using filesystem fallback")
        python_files = _fallback_python_files(repo_root)

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
