# API

Code for deploying the Django admin portal for the WALLABY database.

## Local deployment

You can deploy the API service in isolation locally with the following commands

```
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

It is possible to run it through docker as well, but it is worth noting that there will be issues with the static files.

```
docker build -t sofiax_api .
docker run -p 8000:8000 --env-file=.env sofiax_api
```

For working locally we recommend that you use the `python manage.py runserver` method as the `docker-compose.yml` file does some work to ensure that the static files can be located.