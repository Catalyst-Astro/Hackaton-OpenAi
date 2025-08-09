import argparse
import logging
import subprocess
import sys

MODULE_MAP = {
    'generate_prompts': 'prompts/generator.py',
    'mutate_prompts': 'prompts/mutator.py',
    'run_model': 'engine/runner.py',
    'analyze_outputs': 'engine/analyzer.py',
    'classify_failures': 'engine/classifier.py',
    'generate_report': 'report/generator.py',
}

def run_module(script: str, input_path: str, output_path: str) -> None:
    """Execute a module as a subprocess.

    Args:
        script: Path to the script to execute.
        input_path: Path to input file.
        output_path: Path to output file.
    """
    cmd = [sys.executable, script]
    if input_path:
        cmd += ['--input', input_path]
    if output_path:
        cmd += ['--output', output_path]
    logging.info("Running: %s", ' '.join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        logging.error("Subprocess failed with exit code %s", exc.returncode)
        raise

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI controller for GPT OSS red-teaming"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for cmd, script in MODULE_MAP.items():
        sub = subparsers.add_parser(cmd, help=f"Invoke {script}")
        sub.add_argument("--input", required=True, help="Input file path")
        sub.add_argument("--output", required=True, help="Output file path")
    return parser

def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)
    script = MODULE_MAP[args.command]
    try:
        run_module(script, args.input, args.output)
    except Exception as exc:  # noqa: BLE001
        logging.error("Error executing %s: %s", args.command, exc)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
