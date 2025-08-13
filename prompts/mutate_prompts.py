"""Mutate prompts while safely handling malformed JSONL input."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


def _parse_fragments(line: str) -> List[Dict[str, Any]]:
    """Recover JSON objects from a corrupted line."""

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


def _safe_load(line: str) -> Tuple[List[Dict[str, Any]], bool]:
    """Return objects parsed from ``line`` and whether recovery was needed."""

    line = line.strip().lstrip("\ufeff")
    if not line:
        return [], False
    try:
        return [json.loads(line)], False
    except json.JSONDecodeError:
        objs = _parse_fragments(line)
        if objs:
            return objs, True
        logger.warning("Omitting unparsable line: %s", line[:80])
        return [], False


def mutate_prompts(in_path: str, out_path: str) -> None:
    """Copy prompts from ``in_path`` to ``out_path`` with robust loading."""

    total = valid = rescued = omitted = 0
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(in_path, "r", encoding="utf-8", errors="ignore") as f_in, \
        open(out_path, "w", encoding="utf-8", newline="\n") as f_out:
        for raw_line in f_in:
            total += 1
            objs, fixed = _safe_load(raw_line)
            if not objs:
                omitted += 1
                continue
            if fixed:
                rescued += 1
            else:
                valid += 1
            for obj in objs:
                print(json.dumps(obj, ensure_ascii=False), file=f_out)

    logger.info(
        "mutate_prompts lines=%s valid=%s rescued=%s omitted=%s",
        total,
        valid,
        rescued,
        omitted,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mutate prompts JSONL")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    mutate_prompts(args.input, args.output)


if __name__ == "__main__":
    main()

