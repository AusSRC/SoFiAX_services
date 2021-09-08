# SofiAX_services

Code for the deployment of database portals.

[![Linting](https://github.com/AusSRC/SoFiAX_services/actions/workflows/lint.yml/badge.svg)](https://github.com/AusSRC/SoFiAX_services/actions/workflows/lint.yml)

<HR>

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

Local deployment can be helpful for developing the services. The local deployment includes the following services:

* `nginx` (reverse proxy)
* `api` (Django project for interacting with the database)
* `vo` 
* `PostgreSQL database`

To raise the services run the following

```
docker-compose up
```

You should access the services at http://localhost and the `nginx` reverse proxy will redirect you to the Django admin page.

#### Prepare the services

```
# Run the migrations
SoFiAX_services/web$ docker exec sofiax_web_app python sofiax_web/manage.py migrate --noinput


# Create superuser
SoFiAX_services/web$ docker exec -it sofiax_web_app python sofiax_web/manage.py createsuperuser
```

#### Access to logs
```
SoFiAX_services/web$ docker-compose -f local.yml logs
```

### Production

To get this working in a production setting you will need to run `python manage.py migrate` and create a user for accessing the admin console. 


Once you have successfully migrated and created the superuser, you can deploy the services in detached mode

```
docker-compose up -d
```

### Database

Note that the services that are deployed through the code in this repository depend on a database service to be active. The code for deploying the database can be found at [this repository](https://github.com/AusSRC/WALLABY_database).
