# SofiAX Services

Code deploying database and web services for SoFiAX survey runs.

[![Linting](https://github.com/AusSRC/SoFiAX_services/actions/workflows/lint.yml/badge.svg)](https://github.com/AusSRC/SoFiAX_services/actions/workflows/lint.yml)

<HR>

## Installation

Clone package
```
https://github.com/AusSRC/SoFiAX_services.git
```

Instantiate Database
```
docker-compose up survey_db -d
```

Create environment file
The environoment file contains information regarding project type and database connection details. 

```
cd SoFiAX_services/web/survey_web/
vim .env
```

The ``.env`` file:
```
PROJECT=DINGO

SITE_NAME=DINGO Catalog
SITE_HEADER=DINGO Catalog
SITE_TITLE=DINGO Catalog
INDEX_TITLE=DINGO Catalog
KINEMATICS=False

DJANGO_SECRET_KEY=<django key>
DJANGO_ALLOWED_HOSTS=127.0.0.1 localhost

DATABASE_HOST=host.docker.internal
DATABASE_PORT=5432
DATABASE_NAME=surveydb
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
SEARCH_PATH=public,survey
```

* The `DJANGO_SECRET_KEY` can be generated here: https://djecrety.ir/

* The `DJANGO_ALLOWED_HOSTS` will need to set to the hostname of the deployment.


Sync the administration database

```
docker run survey_web python manage.py migrate
```

Create Site superuser
```
docker run -e DJANGO_SUPERUSER_PASSWORD=admin survey_web python manage.py createsuperuser --username=admin --email=admin@admin.com --noinput
```


Start Web Services
```
docker-compose up survey_nginx survey_web -d
```

VO TAP Serices
```
docker-compose up survey_vo -d
```

TAP URL:
```
https://localhost/tap
```

Website URL
```
https://localhost
```

Once the service are running then a SoFiAX run can be performed.

The SoFiAX can be found here: https://github.com/AusSRC/SoFiAX
