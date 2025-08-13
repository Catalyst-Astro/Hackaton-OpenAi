import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate findings report")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    data = {"findings": [f"Results from {args.input}"]}
    with open(args.output, "w", encoding="utf-8") as f_out:
        json.dump(data, f_out)

=======
import logging
import os
import random
from typing import Any, Dict, List

REQUIRED_FIELDS = [
    "id",
    "prompt",
    "mutated",
    "response",
    "category",
]

SELF_SCORE_FIELDS = [
    "severity",
    "breadth",
    "novelty",
    "reproducibility",
    "methodological_insight",
]

def validate_exploit(exploit: Dict[str, Any]) -> None:
    """Validate exploit schema."""
    missing = [f for f in REQUIRED_FIELDS if f not in exploit]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    if not isinstance(exploit.get("mutated"), bool):
        raise ValueError("'mutated' must be boolean")
    score = exploit.get("self_score", {})
    missing_score = [f for f in SELF_SCORE_FIELDS if f not in score]
    if missing_score:
        raise ValueError(f"Missing self_score fields: {missing_score}")
    for field in SELF_SCORE_FIELDS:
        value = score[field]
        if not isinstance(value, int) or not (1 <= value <= 5):
            raise ValueError(f"self_score.{field} must be int 1-5")

def apply_scores(exploit: Dict[str, Any]) -> Dict[str, Any]:
    score = {
        field: random.randint(1, 5) for field in SELF_SCORE_FIELDS
    }
    exploit["self_score"] = score
    return exploit

def load_findings(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "findings" in data:
        data = data["findings"]
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list or have a 'findings' key")
    return data

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Kaggle findings file")
    parser.add_argument(
        "--input",
        default="data/findings/law_findings.json",
        help="Input findings JSON file",
    )
    parser.add_argument(
        "--output",
        default="findings.auto.1.json",
        help="Output filename (placed under data/kaggle/)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of findings to export",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    findings = load_findings(args.input)
    if len(findings) > args.limit:
        random.shuffle(findings)
    selected = findings[: args.limit]

    output: List[Dict[str, Any]] = []
    for exploit in selected:
        exploit = apply_scores(exploit)
        validate_exploit(exploit)
        logging.info("Exporting exploit %s", exploit["id"])
        output.append(exploit)

    out_dir = os.path.join("data", "kaggle")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logging.info("Wrote %d findings to %s", len(output), out_path)


if __name__ == "__main__":
    main()
