
install:
		uv sync --all-groups

run:
		uv run python -m src.main \
		--functions_definition data/input/functions_definition.json \
		--input data/input/function_calling_tests.json

debug:
		uv run python3 -m pdb -m src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	uv run flake8 --exclude=.venv,llm_sdk .
	uv run mypy . \
			--warn-return-any \
	        --warn-unused-ignores \
            --ignore-missing-imports \
            --disallow-untyped-defs \
            --check-untyped-defs \
            --exclude '^(venv|\.venv|env|llm_sdk)/'

lint-strict: clean
	uv run flake8 --exclude=.venv,llm_sdk .
	uv run mypy . \
		--strict \
		--exclude '^(venv|\.venv|env|llm_sdk)/'

.PHONY: install run debug clean lint lint-strict