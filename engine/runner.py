import argparse



def main() -> None:
    parser = argparse.ArgumentParser(description="Run local model")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    with open(args.output, "w", encoding="utf-8") as f_out:
        f_out.write(f"Model run on {args.input}\n")
=======
import json
import logging
import os
import time
from typing import Any, Dict, List, Tuple

import requests
from requests.exceptions import RequestException


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a batch of prompts against an LLM endpoint.")
    parser.add_argument(
        "--input",
        default="data/prompts/law_mutated.json",
        help="Path to JSON file containing prompts.",
    )
    parser.add_argument(
        "--output",
        default="data/outputs/law_results.json",
        help="Path to JSON file for saving results.",
    )
    parser.add_argument(
        "--model_url",
        default="http://localhost:8000",
        help="Base URL of the model service.",
    )
    parser.add_argument(
        "--log_every",
        type=int,
        default=10,
        help="Log progress every N prompts.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries when request fails.",
    )
    return parser.parse_args()


def ensure_output_dir(path: str) -> None:
    """Ensure the directory for the output path exists."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def parse_model_response(data: Dict[str, Any]) -> Tuple[str, Any]:
    """Extract text and token usage from the model response."""
    text = ""
    tokens = None

    if isinstance(data, dict):
        if "choices" in data and data["choices"]:
            choice = data["choices"][0]
            text = choice.get("text") or choice.get("message", {}).get("content", "")
        elif "text" in data:
            text = data.get("text", "")
        elif "output" in data:
            text = data.get("output", "")
        elif "generated_text" in data:
            text = data.get("generated_text", "")
        else:
            text = json.dumps(data)

        usage = data.get("usage") or {}
        tokens = usage.get("total_tokens") or usage.get("tokens")
    else:
        text = str(data)

    return text, tokens


def call_model(model_url: str, prompt: str, retries: int = 3, timeout: int = 60) -> Tuple[str, Any]:
    """Send prompt to the model endpoint with retry logic."""
    url = model_url.rstrip("/") + "/generate"
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json={"prompt": prompt}, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            return parse_model_response(data)
        except (RequestException, ValueError) as exc:
            logging.warning("Request failed (attempt %s/%s): %s", attempt, retries, exc)
            if attempt == retries:
                raise
            time.sleep(2 ** (attempt - 1))
    return "", None


def run_batch(prompts: List[Dict[str, Any]], model_url: str, log_every: int, retries: int) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    total = len(prompts)
    for idx, item in enumerate(prompts, start=1):
        prompt_id = item.get("id", f"{idx:04d}")
        prompt_text = item["prompt"]
        response_text, tokens = call_model(model_url, prompt_text, retries=retries)
        results.append(
            {
                "id": prompt_id,
                "prompt": prompt_text,
                "response": response_text,
                "tokens": tokens,
            }
        )
        if idx % log_every == 0 or idx == total:
            logging.info("Processed %s/%s prompts", idx, total)
    return results


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    with open(args.input, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    ensure_output_dir(args.output)
    results = run_batch(prompts, args.model_url, args.log_every, args.retries)

    with open(args.output, "w", encoding="utf-8") as f:



if __name__ == "__main__":
    main()
