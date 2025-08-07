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


if __name__ == "__main__":
    main()
