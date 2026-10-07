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
3. Update volume mount point (`/data`) to a local volume
4. Deploy the service (you will need to create a Docker network first)

```
docker network create survey_network
docker-compose up --build -d survey_db
```

### Web

The `survey_web` service provides core functionality for managing and selecting detections that are stored in the `survey_db` database. It has been designed to be easily extendible for new science projects that require custom functionality. More information about the structure of the Django web application can be found at [`web/README.md`](./web/README.md).

1. Create the environment variable file from the example and enter your own values. The same file is used by the `survey_vo` service.

```
cp .env.example .env
```

* The `DJANGO_SECRET_KEY` can be generated here: https://djecrety.ir/
* The `DJANGO_ALLOWED_HOSTS` will need to set to the hostname of the deployment.
* For development over plain http (for example `http://localhost:8000` without `survey_nginx`) uncomment the development options in the file.

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

The configuration files for the VO service are rendered from the templates in `vo/templates` when the container starts, using the environment variables in the `.env` file. Copy the example file and edit the values (the passwords must match those set in `db/01-create.sql`)

```
cp .env.example .env
docker-compose up --build -d survey_vo
```

The `MODULES` variable sets which tables are exposed. Each module is a file in `vo/templates/modules`.

Sometimes I find that I need to give the `gavo` user ownership of the directory `/var/gavo`, otherwise there are warnings in the deployment. You can run

```
chown -R gavo:gavo /var/gavo/
```

### NGINX reverse proxy

```
docker-compose up --build -d survey_nginx
```

## Dependent services

On changes to the deployment of these services you will also need to update the following configuration items:

* `database.env` on Setonix (WALLABY pipeline)
* `sofiax.ini` on Setonix (WALLABY pipeline)
* `wallaby.ini` on AusSRC workflow service (triggers)
