# HI survey portal

A web platform for interactively selecting and managing detections for large HI surveys. Currently used for the WALLABY, DINGO and GASKAP-OH ASKAP surveys. Designed to handle source finding outputs from [SoFiA](https://gitlab.com/SoFiA-Admin/SoFiA-2) and [SoFiAX](https://github.com/AusSRC/SoFiAX).

This page describes the minimal deployment: the web application run locally with Python, and its database in Docker. To deploy all of the services on a server (database, web application, TAP service and reverse proxy in Docker) see [`server/README.md`](./server/README.md).

## Quick start

This project depends on git submodules.

```
git submodule update --init --recursive
```

You will need [uv](https://docs.astral.sh/uv/), Docker and `make`.

```
make start
```

This creates the configuration file `.env` from [`.env.example`](./.env.example), installs the Python dependencies, starts the database, and runs the web application at http://localhost:8000.

To log in you need a user. In another terminal create one with

```
make superuser
```

## Commands

`make start` runs the following steps, which can also be run on their own.

| Command | Description |
|---|---|
| `make env` | Create `.env` from `.env.example`, if it does not exist |
| `make install` | Install the Python dependencies (`pyproject.toml`) |
| `make db` | Start the PostgreSQL database in Docker |
| `make migrate` | Create the tables for users and sessions |
| `make run` | Run the web application at http://localhost:8000 |
| `make superuser` | Create a user to log in with |
| `make stop` | Stop the database |
| `make test` | Run the tests (see [Tests](#tests)) |

The web application can be run on another port with `make run PORT=8080`. Add the address to `CSRF_TRUSTED_ORIGINS` in `.env` if you do.

## Configuration

The configuration is in the `.env` file. The minimal configuration only needs the modules of the application to install.

```
MODULES=core
```

| Module | Description |
|---|---|
| `core` | Runs, instances, detections and their products, tags, comments and manual inspection |
| `operations` | Observations, survey components, external conflicts, cross matching and release of sources |
| `wallaby` | Tiles, source extraction regions and kinematic models (requires `operations`) |
| `dingo` | GAMA matches of detections |

`core` is always required. More information about the modules and the structure of the web application is in [`app/README.md`](./app/README.md), and the other options (for example the detection thresholds) are described in [`server/.env.example`](./server/.env.example).

## Database

`make db` starts a PostgreSQL container (`sofiax_dev_db`) on port `5432` of localhost, with its data in the Docker volume `sofiax_dev_db_data`. The database, the admin user and the tables of the modules in `MODULES` are created the first time it is started. Change `DATABASE_PORT` in `.env` before the first `make db` if the port is already in use.

The tables are not changed when `MODULES` is changed later. To add the tables of a module to the database run

```
docker exec sofiax_dev_db install-modules <module>
```

To start again with an empty database remove the container and its volume

```
docker rm -f sofiax_dev_db
docker volume rm sofiax_dev_db_data
```

The web application can use another PostgreSQL database by setting `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER` and `DATABASE_PASSWORD` in `.env`. Its tables have to be created from the files in [`server/db/modules`](./server/db/modules).

## Tests

The tests of the web application run against a throwaway database in Docker. Nothing is shared with a deployment, so they are safe to run on a server with running services.

```
make test
```

Arguments for pytest can be passed to the script directly, for example `app/tests/run.sh -k inspection -x`.

## Server deployment

The deployment of the database, web application, TAP service (GAVO DaCHS) and NGINX reverse proxy with `docker-compose` is described in [`server/README.md`](./server/README.md).
