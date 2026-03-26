#!/usr/bin/env python3
"""Fail if committed content looks like embedded API keys (heuristic, CI-friendly)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Google API keys often start with AIza; avoid short matches (placeholders).
_GOOGLE_API_KEYISH = re.compile(r"AIza[0-9A-Za-z_-]{30,}")
# OpenAI-style secret (common in mixed stacks)
_SK_SECRET = re.compile(r"\bsk-(?:proj-|live-|test-)?[a-zA-Z0-9]{20,}\b")
# GitHub PAT classic prefix (optional catch)
_GH_PAT = re.compile(r"\bghp_[a-zA-Z0-9]{20,}\b")

_SKIP_DIR_NAMES = frozenset({
    ".git",
    ".venv",
    "venv",
    ".eggs",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".adk",
})

_TEXT_SUFFIXES = frozenset({
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ipynb",
    ".env",
})

# Lines that are clearly documentation / examples (reduce false positives).
_ALLOW_SUBSTRINGS = (
    "your-key",
    "your_key",
    "YOUR_KEY",
    "<your",
    "placeholder",
    "export GOOGLE_API_KEY=",
    "GOOGLE_API_KEY=...",
)


def _iter_files(root: Path):
  for p in root.rglob("*"):
    if not p.is_file():
      continue
    if any(part in _SKIP_DIR_NAMES for part in p.parts):
      continue
    if p.name == ".env.example":
      continue
    suf = p.suffix.lower()
    if suf not in _TEXT_SUFFIXES and p.name != ".env":
      continue
    yield p


def _content_from_ipynb(path: Path) -> str:
  try:
    data = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError):
    return ""
  chunks: list[str] = []
  for cell in data.get("cells", []):
    src = cell.get("source", [])
    if isinstance(src, list):
      chunks.append("".join(src))
    elif isinstance(src, str):
      chunks.append(src)
  return "\n".join(chunks)


def _check_line(line: str, path: Path, line_no: int | None, hits: list[str]) -> None:
  stripped = line.strip()
  if any(s in stripped for s in _ALLOW_SUBSTRINGS):
    return
  for label, pat in (
      ("Google API key shape (AIza…)", _GOOGLE_API_KEYISH),
      ("sk-… secret shape", _SK_SECRET),
      ("GitHub PAT shape (ghp_…)", _GH_PAT),
  ):
    if pat.search(line):
      loc = f"{path}:{line_no}" if line_no else str(path)
      hits.append(f"{loc}: possible {label}")


def main() -> int:
  root = Path(__file__).resolve().parent.parent
  hits: list[str] = []
  for path in _iter_files(root):
    if path.suffix.lower() == ".ipynb":
      text = _content_from_ipynb(path)
      for i, line in enumerate(text.splitlines(), start=1):
        _check_line(line, path, i, hits)
      continue
    try:
      raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
      continue
    for i, line in enumerate(raw.splitlines(), start=1):
      _check_line(line, path, i, hits)

  if hits:
    print("Possible API key or token material detected:", file=sys.stderr)
    for h in hits:
      print(f"  {h}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
