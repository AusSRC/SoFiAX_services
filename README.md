# SofiAX_services

Code for the deployment of database portals.

[![Linting](https://github.com/AusSRC/SoFiAX_services/actions/workflows/lint.yml/badge.svg)](https://github.com/AusSRC/SoFiAX_services/actions/workflows/lint.yml)

## Setup

### Environment variables

We use environment variables to pass information to the container at runtime. This includes Django configuration details and database connection credentials. 

Create or modify an `api/.env` file and include the following

```
DEBUG=1
DJANGO_SECRET_KEY=<secret_key>
DJANGO_ADMIN_SITE_NAME=<your site name>

# Database connection credentials
DATABASE_NAME=sofiadb
DATABASE_USER=admin
DATABASE_PASSWORD=admin
DATABASE_HOST=sofiax_db
DATABASE_PORT=5432
DATABASE=postgres
```

You will also need to specify the `DJANGO_ALLOWED_HOSTS` environment variable when deploying this to a production environment.

### Migrations

Migrations create the tables that Django requires in the database. The application will not run on an empty database unless migrations are run. With the `init` entrypoint from [`docker-entrypoint.sh`](api/docker-entrypoint.sh) the container will run migrations at startup. You can always run them manually with the following command

```
docker exec sofiax_api python api/manage.py migrate --noinput
```

or 

```
cd api 
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
```

### Create superuser

To access the portal you will need user credentials. To create a superuser with full access to the `api` run the following

```
docker exec -it sofiax_api python api/manage.py createsuperuser
```

or 

```
cd api 
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py createsuperuser
```

## Local

To raise the services run the following

```
docker-compose up
```

You should access the services at [localhost](http://localhost) and the `nginx` reverse proxy will redirect you to the Django admin page. If you are asked for credential, you can log in to the portal initially with the superuser created (see Setup).

### Database

If you have an external database you can connect to it by default by specifying the relevant environment variables. However, if you do not have a database and are working on local deployment, the `docker-compose.yml` contains code for deploying a PostgreSQL database alongside the other services. 

To deploy this database uncomment the code and remove the line `command: start` in the `api` `build` section. You do not need to specify the database environment variables if raised in this way. It is recommended that this method not be used outside of local development.

## Production

There are a few additional configuration steps that are required to deploy the services. The first is to point the services to the appropriate databases. This involves changing the content of [`api/.env`] and [`vo/dsn`](vo/dsn) files.

In the `api/.env` file make sure `DEBUG=0` or omit the environment variable entirely as it will default to `False`.

To deploy the services in detached mode in a production environment run the following

```
docker-compose up -d
```

For a fresh database you will need to run migrations and create a superuser in order to access the services. Also look at the `nginx/README.md` for setting up SSL for the deployment.