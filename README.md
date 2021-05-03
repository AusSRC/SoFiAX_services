# SofiAX_services

Code for the deployment of database portals.

[![Linting](https://github.com/AusSRC/SoFiAX_services/actions/workflows/lint.yml/badge.svg)](https://github.com/AusSRC/SoFiAX_services/actions/workflows/lint.yml)

## Deployment

### Environment variables

We use environment variables to pass information to the image at runtime. These are used to specify the database to connect with. Create or modify a ``.env`` file and include the following values

```
DEBUG=1
DJANGO_SECRET_KEY=<secret_key>
DJANGO_ADMIN_SITE_NAME="WALLABY"
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=sofiadb
DATABASE_USER=admin
DATABASE_PASSWORD=admin
DATABASE_HOST=sofiax_db
DATABASE_PORT=5432
DATABASE=postgres
```

You will also need to specify the `DJANGO_ALLOWED_HOSTS` environment variable when deploying this to a production environment.

### Local

If you deploy the system locally there is a `db` container that is also deployed. If there is no existing database to connect with you can leave database environment variables empty and it will connect with the raised PostgreSQL container.

To raise the services run the following

```
docker-compose up
```

You should access the services at http://localhost and the `nginx` reverse proxy will redirect you to the Django admin page. If you are asked for credential, you can log in to the portal initially with the superuser created (see below).

#### Migrations

Migrations create the tables that Django requires in the database. The application will not run on an empty database unless migrations are run. With the `init` entrypoint from [`docker-entrypoint.sh`](api/docker-entrypoint.sh) the container will run migrations at startup. You can always run them manually with the following command

```
docker exec sofiax_api python api/manage.py migrate --noinput
```

#### Create user

To access the portal you will need user credentials. To create a superuser with full access to the `api` run the following

```
docker exec -it sofiax_api python api/manage.py createsuperuser
```

#### Access logs

```
docker-compose logs
```

### Production

There are a few additional configuration steps that are required to deploy the services. The first is to point the services to the appropriate databases. This involves changing the content of [`api/.env`] and [`vo/dsn`](vo/dsn) files.

Next step is to configure the start commmand of the `api` container. There are two options in the [`docker-entrypoint.sh`](api/docker-entrypoint.sh) file: `init` and `start`. If the database has been initalised previously with Django tables then you can change the `command: init` line of the [`docker-compose.yml`](docker-compose.yml) file to `command: start`. Otherwise, it can remain as `init` which will run migration and superuser creation steps.

To deploy the services in detached mode in a production environment run the following

```
docker-compose up -d
```

**NOTE** This will start all containers including the database. If you have targeted an external database then you can run all other services without the database. You will need to remove that dependency from the `docker-compose.yml` file 

```
depends_on: 
  - db
```

and you can run the following instead

```
docker-compose start api nginx vo
```