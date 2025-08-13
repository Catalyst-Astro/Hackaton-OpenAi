"""Batch executor utilities for robust JSONL ingestion."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Iterator, List

logger = logging.getLogger(__name__)


def _parse_fragments(line: str) -> List[Dict[str, Any]]:
    """Extract JSON objects from a possibly corrupted line.

    The function attempts several heuristics to recover JSON objects from a
    string that may contain concatenated objects or literal ``\n`` sequences.
    Returns a list of successfully parsed objects. The list will be empty when
    nothing could be recovered.
    """

    fragments: List[Dict[str, Any]] = []

    # Handle literal ``\n`` separators
    if "\\n" in line:
        for part in line.split("\\n"):
            part = part.strip()
            if not part:
                continue
            try:
                fragments.append(json.loads(part))
            except json.JSONDecodeError:
                pass

    # Handle concatenated objects ``}{``
    if not fragments and "}{" in line:
        for part in line.replace("}{", "}\n{").splitlines():
            part = part.strip()
            if not part:
                continue
            try:
                fragments.append(json.loads(part))
            except json.JSONDecodeError:
                pass

    # Fallback: regex to pull out ``{...}`` fragments
    if not fragments:
        for match in re.findall(r"\{.*?\}(?=(?:\s*\{)|$)", line, flags=re.S):
            try:
                fragments.append(json.loads(match))
            except json.JSONDecodeError:
                continue

    return fragments


def iter_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    """Yield objects from a JSONL file, attempting to recover corrupt lines.

    Lines containing multiple concatenated objects or literal ``\n`` sequences
    are split and parsed individually. Lines that cannot be parsed are skipped
    with a warning.
    """

    produced = recovered = ignored = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip().lstrip("\ufeff")
            if not line:
                continue

            try:
                obj = json.loads(line)
                produced += 1
                yield obj
                continue
            except json.JSONDecodeError:
                pass

            objs = _parse_fragments(line)
            if not objs:
                ignored += 1
                logger.warning("Skipping unparsable line: %s", line[:80])
                continue

            recovered += 1
            for obj in objs:
                produced += 1
                yield obj

    logger.info(
        "iter_jsonl produced=%s recovered_lines=%s ignored_lines=%s",
        produced,
        recovered,
        ignored,
    )

