# Server deployment

Deployment of all of the services on a server with `docker-compose`. For the minimal deployment of the web application on its own see the [`README.md`](../README.md) in the root of the repository.

## Services

| Service | Description | Folder |
|---|---|---|
| `database` | PostgreSQL database | [`server/db`](./db) |
| `app` | Django web application | [`app`](../app) |
| `gavo` | GAVO DaCHS TAP service | [`server/vo`](./vo) |
| `nginx` | NGINX reverse proxy | [`server/nginx`](./nginx) |

The commands below are run from the root of the repository, where `docker-compose.yml` is. Only start the services that are needed, for example an existing database can be used instead of the `database` service.

## Configuration

Create the environment variable file from the server example and enter your own values. The same file is used by all of the services.

```
cp server/.env.example .env
```

* `MODULES` sets which parts of the service are deployed, and `core` is the minimal service. Each module is an application in `app/modules`, a file with its tables in `server/db/modules`, and a file with the tables exposed by the TAP service in `server/vo/templates/modules`.
* Set your own passwords for the database users.
* `SERVER_URL` is the address of the deployment.

## Database

1. Update volume mount point (`/data`) in `docker-compose.yml` to a local volume
2. Deploy the service (you will need to create a Docker network first)

```
docker network create survey_network
docker-compose up --build -d database
```

The database, users and the tables of the modules are created the first time the service is started with an empty volume (`db/init.sh`). If this fails (for example a missing variable), fix the `.env` file and empty the volume before starting the service again.

* The survey user (`survey_user`) is created if `DATABASE_SURVEY_PASSWORD` is set.
* The users of the TAP service are created if `VO_FEED_PASSWORD`, `VO_TRUSTED_PASSWORD` and `VO_UNTRUSTED_PASSWORD` are set.

To add a module to an existing database add it to `MODULES` and run

```
docker exec database install-modules <module>
```

## Web application

The `app` service provides core functionality for managing and selecting detections that are stored in the database. More information about the structure of the Django web application can be found at [`app/README.md`](../app/README.md).

1. Enter your own values for the web application variables in the `.env` file

* The `DJANGO_SECRET_KEY` can be generated here: https://djecrety.ir/
* The `DJANGO_ALLOWED_HOSTS` will need to set to the hostname of the deployment.

2. Deploy the service

```
docker-compose up --build -d app
```

3. Migrations and create user

This is easiest done inside of the container. To create the superuser you will be prompted to provide a password.

```
docker exec -it app /bin/bash
```

and then inside of the container run the following

```
python manage.py migrate
python manage.py createsuperuser --username <username>
```

## TAP service (GAVO DaCHS)

The configuration files for the TAP service are rendered from the templates in `server/vo/templates` when the container starts, using the environment variables in the `.env` file. The database users are created from the same variables when the database is first started. More information is in [`server/vo/README.md`](./vo/README.md).

```
docker-compose up --build -d gavo
```

The `MODULES` variable sets which tables are exposed. Each module is a file in `server/vo/templates/modules`.

Sometimes I find that I need to give the `gavo` user ownership of the directory `/var/gavo`, otherwise there are warnings in the deployment. You can run

```
chown -R gavo:gavo /var/gavo/
```

## NGINX reverse proxy

```
docker-compose up --build -d nginx
```

## Dependent services

On changes to the deployment of these services you will also need to update the following configuration items:

* `database.env` on Setonix (WALLABY pipeline)
* `sofiax.ini` on Setonix (WALLABY pipeline)
* `wallaby.ini` on AusSRC workflow service (triggers)
