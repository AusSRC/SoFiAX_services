## SofiAX_services

This repository provides dode for the deployment of database portals using *docker* containers.

**TOC**
<HR>

+ [Create an environment file](#create-an-environment-file)
+ [Raise the services](#raise-the-services)
+ [Prepare the services](#prepare-the-services)
+ [Access to logs](#access-to-logs)


#### Create an environment file
Create (or modify) ``.env`` file and include the following values:

```
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=1 
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY=<secret key by generator>
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=sofiadb
SQL_USER=admin
SQL_PASSWORD=admin
SQL_HOST=sofiax_db
SQL_PORT=5432
DATABASE=postgres

#Configuration of the view of Django web application
SITE_HEADER="NAME DB Administration"
SITE_TITLE="NAME DB Site"
INDEX_TITLE="NAME DB Site Administration"
```


#### Raise the services

Raise the servicesfull service with docker-compose:

```
SoFiAX_services/web$ docker-compose -f local.yml up -d
```

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


