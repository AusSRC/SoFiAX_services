# HI survey portal

A web platform for interactively selecting and managing detections for large HI surveys. Deployed as a collection of containerised services using Docker. Currently used for WALLABY and DINGO ASKAP surveys. Custom web interfaces have also been developed to provide custom functionality for these key science projects. Designed be handle source finding outputs from [SoFiA](https://gitlab.com/SoFiA-Admin/SoFiA-2) and [SoFiAX](https://github.com/AusSRC/SoFiAX).

## Services

- database (PostgreSQL database)
- web (Django web application)
- nginx (NGINX reverse proxy)
- gavo (GAVO DACHS TAP service)

## Deploy

### Database

1. Create the environment variable file from the example and enter your own values. The same file is used by all of the services.

```
cp .env.example .env
```

* `MODULES` sets which parts of the service are deployed. Each module has a file with its tables in `db/modules`, and `core` is the minimal service.
* Set your own passwords for the database users.

2. Update volume mount point (`/data`) to a local volume
3. Deploy the service (you will need to create a Docker network first)

```
docker network create survey_network
docker-compose up --build -d database
```

The database, users and the tables of the modules are created the first time the service is started with an empty volume (`db/init.sh`). If this fails (for example a missing variable), fix the `.env` file and empty the volume before starting the service again.

To add a module to an existing database add it to `MODULES` and run

```
docker exec database install-modules <module>
```

### Web

The `web` service provides core functionality for managing and selecting detections that are stored in the `database` database. It has been designed to be easily extendible for new science projects that require custom functionality. More information about the structure of the Django web application can be found at [`web/README.md`](./web/README.md).

1. Enter your own values for the web application variables in the `.env` file

* The `DJANGO_SECRET_KEY` can be generated here: https://djecrety.ir/
* The `DJANGO_ALLOWED_HOSTS` will need to set to the hostname of the deployment.
* For development over plain http (for example `http://localhost:8000` without `nginx`) uncomment the development options in the file.

2. Deploy the service

```
docker-compose up --build -d web
```

3. Migrations and create user

This is easiest done inside of the container. To create the superuser you will be prompted to provide a password.

```
docker exec -it web /bin/bash
```

and then inside of the container run the following

```
python manage.py migrate
python manage.py createsuperuser --username <username>
```

### GAVO DACHS

The configuration files for the VO service are rendered from the templates in `vo/templates` when the container starts, using the environment variables in the `.env` file. The database users are created from the same variables when the database is first started

```
cp .env.example .env
docker-compose up --build -d gavo
```

The `MODULES` variable sets which tables are exposed. Each module is a file in `vo/templates/modules`.

Sometimes I find that I need to give the `gavo` user ownership of the directory `/var/gavo`, otherwise there are warnings in the deployment. You can run

```
chown -R gavo:gavo /var/gavo/
```

### NGINX reverse proxy

```
docker-compose up --build -d nginx
```

## Dependent services

On changes to the deployment of these services you will also need to update the following configuration items:

* `database.env` on Setonix (WALLABY pipeline)
* `sofiax.ini` on Setonix (WALLABY pipeline)
* `wallaby.ini` on AusSRC workflow service (triggers)
