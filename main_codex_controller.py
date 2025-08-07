import argparse
import logging
import os
import subprocess
import sys


def run_script(script_path: str, input_path: str, output_path: str) -> None:
    """Run a Python script with input/output arguments."""
    command = [sys.executable, script_path, "--input", input_path, "--output", output_path]
    logging.debug("Executing command: %s", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    parser = argparse.ArgumentParser(
        description="Main controller for gpt-oss-redteaming pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_io_arguments(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--input", required=True, help="Input file path")
        subparser.add_argument("--output", required=True, help="Output file path")

    add_io_arguments(
        subparsers.add_parser("generate_prompts", help="Generate initial prompts")
    )
    add_io_arguments(
        subparsers.add_parser("mutate_prompts", help="Mutate prompts for diversity")
    )
    add_io_arguments(
        subparsers.add_parser("run_model", help="Run the local model on prompts")
    )
    add_io_arguments(
        subparsers.add_parser("analyze_outputs", help="Analyze model outputs")
    )
    add_io_arguments(
        subparsers.add_parser("classify_failures", help="Classify potential failures")
    )
    add_io_arguments(
        subparsers.add_parser(
            "generate_report", help="Generate Kaggle findings.json report"
        )
    )

    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.abspath(__file__))
    script_map = {
        "generate_prompts": os.path.join(repo_root, "prompts", "generator.py"),
        "mutate_prompts": os.path.join(repo_root, "prompts", "mutator.py"),
        "run_model": os.path.join(repo_root, "engine", "runner.py"),
        "analyze_outputs": os.path.join(repo_root, "engine", "analyzer.py"),
        "classify_failures": os.path.join(repo_root, "engine", "classifier.py"),
        "generate_report": os.path.join(repo_root, "report", "generator.py"),
    }

    script_path = script_map.get(args.command)

    if script_path is None:
        logging.error("Unknown command: %s", args.command)
        sys.exit(1)

    try:
        run_script(script_path, args.input, args.output)
    except subprocess.CalledProcessError as exc:
        logging.error("Subprocess failed with exit code %s", exc.returncode)
        sys.exit(exc.returncode)
    except FileNotFoundError as exc:
        logging.error("Required script not found: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
