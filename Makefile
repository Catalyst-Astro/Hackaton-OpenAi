.PHONY: sanitize validate-jsonl clean pipeline

sanitize:
	python scripts/sanitize_jsonl.py data/prompts

validate-jsonl:
	python scripts/validate_jsonl.py

clean:
	rm -f data/outputs/*.json data/analyzed/*.json data/analyzed/*.csv data/findings/*.json

pipeline:
	python scripts/pipeline_stub.py
