include python-templates/Makefile

# Override the template's lint/format targets: this repo's code lives under
# app (not src/tests), and ruff is managed via uv rather than installed
# on PATH.
lint:
	uv run --only-group dev ruff check .

format:
	uv run --only-group dev ruff format .

# Web application tests against a throwaway database (see app/tests/run.sh)
test:
	app/tests/run.sh

# ---------------------------------------------------------------------------------------
# Minimal local deployment: the web application run with Python and its database in
# Docker (see README.md). The configuration is read from ENV_FILE.

ENV_FILE ?= .env
# Name of the database container, its data is kept in the volume $(DEV_DB)_data
DEV_DB ?= sofiax_dev_db
PORT ?= 8000
MANAGE = ENV_FILE=$(abspath $(ENV_FILE)) uv run --no-dev python app/manage.py

.PHONY: env install db migrate superuser run start stop

# Create the configuration from the example, if there is none
env:
	@test -f $(ENV_FILE) || (cp .env.example $(ENV_FILE) && echo "Created $(ENV_FILE) from .env.example")

# Install the Python dependencies
install:
	uv sync --no-dev

# Start the database. The tables of the modules in MODULES are created the first time.
db: env
	@docker build -q -t sofiax_db server/db > /dev/null
	@if [ -n "$$(docker ps -aq -f name='^$(DEV_DB)$$')" ]; then \
		docker start $(DEV_DB) > /dev/null; \
	else \
		port=$$(sed -n 's/^DATABASE_PORT=//p' $(ENV_FILE)); \
		docker run -d --name $(DEV_DB) --env-file $(ENV_FILE) \
			-p 127.0.0.1:$${port:-5432}:5432 \
			-v $(DEV_DB)_data:/var/lib/postgresql/data sofiax_db > /dev/null; \
	fi
	@echo "Waiting for the database"
	@for i in $$(seq 1 60); do \
		if docker exec $(DEV_DB) pg_isready -q -h 127.0.0.1 2> /dev/null; then exit 0; fi; \
		if [ "$$(docker inspect -f '{{.State.Running}}' $(DEV_DB))" != "true" ]; then break; fi; \
		sleep 1; \
	done; \
	docker logs --tail 20 $(DEV_DB); echo "The database failed to start"; exit 1

# Create the tables of the web application (users and sessions)
migrate:
	$(MANAGE) migrate

# Create a user to log in with
superuser:
	$(MANAGE) createsuperuser

# Run the web application at http://localhost:$(PORT)
run:
	$(MANAGE) runserver $(PORT)

# Everything needed to run the web application locally
start: env install db migrate run

# Stop the database, its data is kept
stop:
	docker stop $(DEV_DB)
