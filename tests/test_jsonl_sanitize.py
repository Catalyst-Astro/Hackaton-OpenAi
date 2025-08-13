"""Tests for the JSONL sanitization utility."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scripts.sanitize_jsonl import sanitize_file


def _load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_concatenated_objects(tmp_path):
    p = tmp_path / "sample.jsonl"
    p.write_text('{"a":1}{"b":2}', encoding="utf-8")
    sanitize_file(p)
    assert _load_jsonl(p) == [{"a": 1}, {"b": 2}]


def test_literal_newline(tmp_path):
    p = tmp_path / "newline.jsonl"
    p.write_text('{"a":1}\\n{"b":2}', encoding="utf-8")
    sanitize_file(p)
    assert _load_jsonl(p) == [{"a": 1}, {"b": 2}]


def test_bom_and_spaces(tmp_path):
    p = tmp_path / "bom.jsonl"
    p.write_text("\ufeff {\"a\":1}  \n", encoding="utf-8")
    sanitize_file(p)
    assert _load_jsonl(p) == [{"a": 1}]


def test_idempotent(tmp_path):
    p = tmp_path / "idem.jsonl"
    p.write_text('{"a":1}{"b":2}', encoding="utf-8")
    sanitize_file(p)
    first = p.read_text(encoding="utf-8")
    sanitize_file(p)
    second = p.read_text(encoding="utf-8")
    assert first == second

