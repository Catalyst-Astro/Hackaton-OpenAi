import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local model")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    with open(args.output, "w", encoding="utf-8") as f_out:
        f_out.write(f"Model run on {args.input}\n")


if __name__ == "__main__":
    main()
