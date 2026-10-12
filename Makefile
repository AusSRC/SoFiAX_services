include python-templates/Makefile

# Override the template's lint/format targets: this repo's code lives under
# app/survey (not src/tests), and ruff is managed via uv rather than installed
# on PATH.
lint:
	uv run --only-group dev ruff check .

format:
	uv run --only-group dev ruff format .

# Web application tests against a throwaway database (see app/tests/run.sh)
test:
	app/tests/run.sh
