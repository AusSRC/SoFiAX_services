include python-templates/Makefile

# Override the template's lint/format targets: this repo's code lives under
# web/survey (not src/tests), and ruff is managed via uv rather than installed
# on PATH.
lint:
	uv run ruff check .

format:
	uv run ruff format .

# Web application tests against a throwaway database (see web/tests/run.sh)
test:
	web/tests/run.sh
