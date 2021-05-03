#!/bin/bash

set -e

# Initialise database (for new database connection)
init () {
  echo "Running makemigrations"
  python manage.py makemigrations

  echo "Running migrate"
  python manage.py migrate

  gunicorn -b :8000 api.wsgi:application
}

# Start the service
start () {
  gunicorn -b :8000 api.wsgi:application
}

case ${1} in
  init)
    init
    ;;
  start)
    start
    ;;
  *)
    exec "$@"
    ;;
esac