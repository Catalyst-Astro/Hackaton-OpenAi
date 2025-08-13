"""Validate JSONL files under data/prompts."""

from __future__ import annotations

import json
import pathlib
import sys


def main() -> None:
    bad = 0
    for p in pathlib.Path("data/prompts").glob("*.jsonl"):
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    json.loads(line)
                except Exception:
                    bad += 1
                    print(f"BAD {p}:{i} -> {line[:120]}", file=sys.stderr)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()

