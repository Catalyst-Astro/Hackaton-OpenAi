"""Utility to sanitize JSONL files with minimal formatting issues."""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
import re
import shutil
from typing import Any, Dict, Iterable, List, Tuple

logger = logging.getLogger(__name__)


def _parse_fragments(line: str) -> List[Dict[str, Any]]:
    """Attempt to recover JSON objects from a line."""

    fragments: List[Dict[str, Any]] = []

    if "\\n" in line:
        for part in line.split("\\n"):
            part = part.strip()
            if not part:
                continue
            try:
                fragments.append(json.loads(part))
            except json.JSONDecodeError:
                pass

    if not fragments and "}{" in line:
        for part in line.replace("}{", "}\n{").splitlines():
            part = part.strip()
            if not part:
                continue
            try:
                fragments.append(json.loads(part))
            except json.JSONDecodeError:
                pass

    if not fragments:
        for match in re.findall(r"\{.*?\}(?=(?:\s*\{)|$)", line, flags=re.S):
            try:
                fragments.append(json.loads(match))
            except json.JSONDecodeError:
                continue

    return fragments


def sanitize_file(path: pathlib.Path) -> Tuple[int, int, int]:
    """Sanitize a JSONL file in-place.

    Returns a tuple ``(objects, recovered_lines, omitted_lines)``.
    """

    text = path.read_text(encoding="utf-8", errors="ignore")
    text = text.replace("}\n{", "}\n{")  # literal \n -> newline
    text = text.replace("}{", "}\n{")

    lines = text.splitlines()
    objects: List[Dict[str, Any]] = []
    recovered = omitted = 0

    for raw in lines:
        line = raw.strip().lstrip("\ufeff")
        if not line:
            continue
        try:
            objects.append(json.loads(line))
            continue
        except json.JSONDecodeError:
            pass

        frags = _parse_fragments(line)
        if not frags:
            omitted += 1
            logger.warning("Omitting unparsable line in %s: %s", path, line[:80])
            continue
        recovered += 1
        objects.extend(frags)

    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copyfile(path, backup)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for obj in objects:
            print(json.dumps(obj, ensure_ascii=False), file=f)

    return len(objects), recovered, omitted


def iter_paths(paths: Iterable[str]) -> List[pathlib.Path]:
    result: List[pathlib.Path] = []
    for p_str in paths:
        p = pathlib.Path(p_str)
        if p.is_dir():
            result.extend(sorted(p.rglob("*.jsonl")))
        elif p.suffix == ".jsonl" and p.exists():
            result.append(p)
    return result


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Sanitize JSONL files")
    parser.add_argument("paths", nargs="+", help="Files or directories")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    for file_path in iter_paths(args.paths):
        objs, rec, om = sanitize_file(file_path)
        logger.info("%s: objects=%s recovered_lines=%s omitted_lines=%s", file_path, objs, rec, om)


if __name__ == "__main__":
    main()

