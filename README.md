# HI survey portal

A web platform for interactively selecting and managing detections for large HI surveys. Deployed as a collection of containerised services using Docker. Currently used for WALLABY and DINGO ASKAP surveys. Custom web interfaces have also been developed to provide custom functionality for these key science projects. Designed be handle source finding outputs from [SoFiA](https://gitlab.com/SoFiA-Admin/SoFiA-2) and [SoFiAX](https://github.com/AusSRC/SoFiAX).

## Services

- survey_db (PostgreSQL database)
- survey_web (Django web application)
- survey_nginx (NGINX reverse proxy)
- survey_vo (GAVO DACHS TAP service)

## Deploy

### Database

1. Create `db/psql.env` file to set the `POSTGRES_USER` and `POSTGRES_PASSWORD` environment variables
2. Update the `db/01-create.sql` script with custom passwords for users
3. Deploy the service (you will need to create a Docker network first)

```
docker network create survey_network
docker-compose up --build -d survey_db
```

### Web

The `survey_web` service provides core functionality for managing and selecting detections that are stored in the `survey_db` database. It has been designed to be easily extendible for new science projects that require custom functionality. More information about the structure of the Django web application can be found at [`web/README.md`](./web/README.md).

1. Create environment variable file and place it at `web/config` with the following variables (enter your own values for these):

```
PROJECT = WALLABY
DEBUG = True
LOCAL = True
SITE_NAME = WALLABY Catalog
SITE_HEADER = WALLABY Catalog
SITE_TITLE = WALLABY Catalog
INDEX_TITLE = WALLABY Catalog
AUTH_GROUPS = wallaby

DJANGO_SECRET_KEY = <django key>
DJANGO_ALLOWED_HOSTS = 127.0.0.1 localhost

DATABASE_HOST = surveydb
DATABASE_PORT = 5432
DATABASE_NAME = surveydb
DATABASE_USER = postgres
DATABASE_PASSWORD = postgres
SEARCH_PATH = survey,public
```

* The `DJANGO_SECRET_KEY` can be generated here: https://djecrety.ir/
* The `DJANGO_ALLOWED_HOSTS` will need to set to the hostname of the deployment.

2. Deploy the service

```
docker-compose up --build -d survey_web
```

3. Migrations and create user

This is easiest done inside of the container. To create the superuser you will be prompted to provide a password.

```
docker exec -it survey_web /bin/bash
```

and then inside of the container run the following

```
python manage.py migrate
python manage.py createsuperuser --username <username>
```

### GAVO DACHS

### NGINX reverse proxy

## Dependent services

On changes to the deployment of these services you will also need to update the following configuration items:

* `database.env` on Setonix (WALLABY pipeline)
* `sofiax.ini` on Setonix (WALLABY pipeline)
* `wallaby.ini` on AusSRC workflow service (triggers)
