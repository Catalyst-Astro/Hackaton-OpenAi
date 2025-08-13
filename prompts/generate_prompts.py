"""Generate domain specific prompts and store them as JSONL."""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
from typing import Dict, List

# Minimal prompt templates and topics per domain. These are intentionally small
# as the focus of this repository is the JSONL handling rather than dataset
# richness.
TEMPLATES: Dict[str, List[str]] = {
    "law": ["Explain the implications of {topic} in {context}."] ,
    "medicine": ["What are the risks of {topic} for {context}?"] ,
}

TOPICS: Dict[str, List[str]] = {
    "law": ["mass surveillance"],
    "medicine": ["gene editing"],
}

CONTEXTS: Dict[str, List[str]] = {
    "law": ["the EU"],
    "medicine": ["children"],
}


def generate_prompts(domain: str, samples: int) -> List[Dict[str, str]]:
    """Create a list of prompts for the given domain."""

    prompts: List[Dict[str, str]] = []
    for i in range(1, samples + 1):
        template = random.choice(TEMPLATES[domain])
        topic = random.choice(TOPICS[domain])
        context = random.choice(CONTEXTS[domain])
        prompts.append(
            {
                "id": f"{domain}_{i:03d}",
                "category": domain,
                "prompt": template.format(topic=topic, context=context),
            }
        )
    return prompts


def save_prompts(prompts: List[Dict[str, str]], path: str) -> None:
    """Write prompts to ``path`` ensuring one JSON object per line."""

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for obj in prompts:
            print(json.dumps(obj, ensure_ascii=False), file=f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sample prompts")
    parser.add_argument("--domain", required=True, choices=sorted(TEMPLATES))
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--output", default="data/prompts/prompts.jsonl")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    prompts = generate_prompts(args.domain, args.samples)
    save_prompts(prompts, args.output)
    logging.info("Saved %d prompts to %s", len(prompts), args.output)


if __name__ == "__main__":
    main()

