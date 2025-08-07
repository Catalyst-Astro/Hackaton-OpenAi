import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify failures")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    with open(args.output, "w", encoding="utf-8") as f_out:
        f_out.write(f"Classification results for {args.input}\n")


if __name__ == "__main__":
    main()
