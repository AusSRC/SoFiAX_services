# HI Survey source finding portal

A collection of web services (Django web interface, PostgreSQL database, NGINX reverse proxy and GAVO DACHS service for TAP) used for managing source detections in HI surveys. Currently used for WALLABY and DINGO ASKAP surveys. Custom web interfaces have also been developed to provide custom functionality for these key science projects. Designed be used with [SoFiA](https://gitlab.com/SoFiA-Admin/SoFiA-2) and [SoFiAX](https://github.com/AusSRC/SoFiAX) source finding codes.

## Setup

### Database

1. Create `db/psql.env` file to set the `POSTGRES_USER` and `POSTGRES_PASSWORD` environment variables
2. Update the `db/01-create.sql` script with custom passwords for users
3. Deploy the service (you will need to create a Docker network first)

```
docker network create survey_network
docker-compose up --build -d survey_db
```

## Web

The environoment file contains information regarding project type and database connection details. Create a ``.env`` file under `web/survey_web` with:

```
PROJECT=DINGO
DEBUG=True
SITE_NAME=DINGO Catalog
SITE_HEADER=DINGO Catalog
SITE_TITLE=DINGO Catalog
INDEX_TITLE=DINGO Catalog
KINEMATICS=False
AUTH_GROUPS=dingo

DJANGO_SECRET_KEY=<django key>
DJANGO_ALLOWED_HOSTS=127.0.0.1 localhost

DATABASE_HOST=surveydb
DATABASE_PORT=5432
DATABASE_NAME=surveydb
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
SEARCH_PATH=survey,public
```

* The `DJANGO_SECRET_KEY` can be generated here: https://djecrety.ir/

* The `DJANGO_ALLOWED_HOSTS` will need to set to the hostname of the deployment.

### 2. Deploy services

```
docker network create survey_network
docker-compose up --build -d
```

### 3. Database migrations

```
docker-compose run survey_web python manage.py migrate
docker-compose run survey_web python manage.py makemigrations survey
docker-compose run survey_web python manage.py migrate survey
```

### 4. Create site superuser

```
docker-compose run -e DJANGO_SUPERUSER_PASSWORD=admin survey_web python manage.py createsuperuser --username=admin --email=admin@admin.com --noinput
```

<HR>

## Other

TAP URL:
```
https://localhost/tap
```

Website URL
```
https://localhost
```
